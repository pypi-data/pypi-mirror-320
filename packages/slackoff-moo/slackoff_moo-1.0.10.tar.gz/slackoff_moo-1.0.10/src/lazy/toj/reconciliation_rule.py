# 把表格数据解析成json数据
# 步骤：解析规则 -> 执行解析 -> 合并解析结果
from abc import ABC, abstractmethod
from collections.abc import Iterator
from .reconciliation_source import DataSource
from .reconciliation_exper_processor import NifiExpression, DefaultCalcExpression
from .utils import Utils


# 规则的行为
class Rule(ABC):
    # 规则解析
    @abstractmethod
    def parse(self, ctx):
        pass


class OrganizationMergeRule:
    def __init__(self):
        self.merges = [DictMerge(), StringMerge(), IntegerMerge(), FloatMerge(), ListMerge()]

    @abstractmethod
    def merge(self, args):
        if not isinstance(args, list):
            raise Exception()
        for merge in self.merges:
            if merge.check(args):
                return merge.merge(args)
        return None


class DictMerge:
    def merge(self, args):
        if self.check(args=args):
            result = {}
            for arg in args:
                result.update(arg)
            return result
        return None

    @staticmethod
    def check(args):
        if not isinstance(args, list):
            raise Exception()
        return all(isinstance(item, dict) for item in args)


class StringMerge:
    def merge(self, args):
        if self.check(args):
            result = ""
            for arg in args:
                result = result.join(arg)
            return result
        return None

    @staticmethod
    def check(args):
        if not isinstance(args, list):
            raise Exception()
        return all(isinstance(item, str) for item in args)


class IntegerMerge:
    def merge(self, args):
        if self.check(args):
            result = 0
            for arg in args:
                result += arg
            return result
        return None

    @staticmethod
    def check(args):
        return all(isinstance(item, int) for item in args)


class FloatMerge:
    def merge(self, args):
        if self.check(args):
            result = 0
            for arg in args:
                result += arg
            return result
        return None

    @staticmethod
    def check(args):
        return all(isinstance(item, float) for item in args)


class ListMerge:
    def merge(self, args):
        vals = []
        if len(args) == 2 and self.check(args):
            a = args[0]
            b = args[1]
            array_len = max(len(a), len(b))
            for i in range(array_len):
                av = a[i]
                bv = b[i]
                if av is None and bv is not None:
                    vals.append(bv)
                elif av is not None and bv is None:
                    vals.append(av)
                elif type(av) == type(bv):
                    if type(av) == str:
                        vals.append(av)
                    elif type(av) == int or type(av) == float:
                        vals.append(av + bv)
                    else:
                        vals.append(None)
                else:
                    vals.append(None)
        return vals

    @staticmethod
    def check(args):
        return all(isinstance(item, list) for item in args)


# 一、组织数据
# 1. 按照组织规则去生成对应的json
class AbsOrganizationExperRule(Rule, ABC):
    def __int__(self, rules, process, merge):
        if not isinstance(rules, BaseProcess):
            Exception()
        self.rules = rules
        # self.init_exper()
        self.process = process
        self.key_level = {}  # 健映射层级
        self.merge = merge  # 合并规则
        self.KEY_ROW = "row"
        self.KEY_THIS = "this"
        self.KEY_MOUNT = "mount"

    # 深度优先
    def parse(self, ctx):
        if self.KEY_ROW not in ctx:
            raise Exception("row数据未定义")
        tables = ctx[self.KEY_ROW]
        if not isinstance(tables, Iterator):
            raise Exception()
        frame = {
            "rules": self.rules,  # 规则
            "ctx": ctx,  # 给规则执行时，需要用到的上下文
            "part": {
                "this": None
            }
        }
        # 解析后的结果
        num = 0
        for row in tables:
            ctx[self.KEY_ROW] = row
            ctx[self.KEY_MOUNT] = {}  # 数据挂载
            self.doParse(frame)
            num += 1

        return frame["part"]["this"]

    def doParse(self, frame):
        rules = frame["rules"]
        if "before" in rules:
            Utils.handle(rules["before"], "before", frame["ctx"])

        if "filter" in rules:
            filter_result = Utils.handle(rules["filter"], "filter", frame["ctx"])  # 过滤
            if not isinstance(filter_result, bool):
                raise ValueError(rules["filter"], "的返回值为", filter_result, "filter返回值必须是bool类型")
            if not filter_result:
                return None

        self.doExecute(frame)

        if "rule" in frame["rules"]:
            return self.exist_rule(frame)
        elif "children" in frame["rules"]:
            return self.not_exist_rule(frame)

    # 如果存在rule，就解析成字典
    def exist_rule(self, frame):
        rules = frame["rules"]
        children = "children"
        mount = frame["ctx"][self.KEY_MOUNT]

        # 1. 生成键值对的键
        returned_rule = getattr(self.process, "rule", None)(rules, frame["ctx"])
        if children not in rules:
            return returned_rule

        # 根节点特殊处理
        if frame["part"]["this"] is None:
            frame["part"]["this"] = {}

        merge_work = frame["part"]["this"]
        this = {}          # 对象上下文
        vals = []          # 解析children的值

        if returned_rule in frame["part"]["this"]:
            this = frame["part"]["this"][returned_rule]

        # 2. 解析值，无限套娃children
        if children in rules and len(rules[children]) > 0:
            # 恢复为当前局部的挂载
            frame["ctx"][self.KEY_MOUNT] = mount
            for rule in rules[children]:
                frame["ctx"][self.KEY_THIS] = vals  # 同级别上下文
                val = self.doParse({
                    "rules": rule,
                    "ctx": frame["ctx"],
                    "part": {
                        "top_val": returned_rule,
                        "this": this
                    }
                })
                vals.append(val)

        # 3. 合并值
        # 合并自定义规则之后的值
        if "toString" in rules:
            vals = Utils.handle(rules["toString"], "toString", vals)

        if isinstance(merge_work, dict):
            # 合并同一父级的值
            if returned_rule in merge_work:
                origin_vals = merge_work[returned_rule]
                merge_work[returned_rule] = getattr(self.merge, "merge", None)([vals, origin_vals])
                return merge_work
            # 如果没有共同父级，直接赋值
            else:
                merge_work[returned_rule] = vals
                return merge_work
        elif isinstance(merge_work, list):
            merge_work.append(vals)
            return merge_work

    # 如果只存在children，则把数据解析成数组
    def not_exist_rule(self, frame):
        rules = frame["rules"]
        children = "children"
        mount = frame["ctx"][self.KEY_MOUNT]

        # 局部上下文：已经解析好的，同级别的上下文
        part_context = []

        # 解析值，无限套娃children
        if children in rules and len(rules[children]) > 0:
            frame["ctx"][self.KEY_THIS] = part_context
            # 恢复为当前局部的挂载
            frame["ctx"][self.KEY_MOUNT] = mount
            for i in range(len(rules[children])):
                rule = rules[children][i]
                val = self.doParse({
                    "rules": rule,
                    "ctx": frame["ctx"],
                    "part": {
                        "this": part_context
                    }
                })
                part_context.insert(i, val)
        if "top_val" in frame["part"]:
            frame["part"]["this"][frame["part"]["top_val"]] = part_context
        else:
            if frame["part"]["this"] is None:
                frame["part"]["this"] = part_context
            else:
                [frame["part"]["this"].append(item) for item in part_context]
        return part_context

    # 规则扩展
    @abstractmethod
    def doExecute(self, frame):
        pass


# 二、合并
# 组织数据合并规则
class OrganizationRule(AbsOrganizationExperRule):
    def __init__(self, rules, data):
        self.__int__(rules, OrganizationProcess(data), OrganizationMergeRule())

    # 如果元素是
    def doExecute(self, frame):
        rules = frame["rules"]
        children = "children"
        # 如果children是字典，就直接包装成数组，并且默认toString获取数组第一个元素
        if children in rules and isinstance(rules[children], dict):
            rules[children] = [rules[children]]
            if "toString" not in rules:
                rules["toString"] = lambda vals: vals[0]


# 通用的规则处理器
class BaseProcess:
    # source数据源
    def __init__(self, source):
        if not isinstance(source, DataSource):
            raise Exception()
        self.source = source
        self.exper_processor = NifiExpression(DefaultCalcExpression())

    @staticmethod
    def filter(regulation, data):
        handle_name = "filter"
        if handle_name not in regulation:
            return True
        returned = Utils.handle(regulation[handle_name], handle_name, data)
        if returned is None:
            raise Exception("filter只支持函数或对象，并且必须返回bool类型")
        return returned

    @staticmethod
    def children(regulation, stack):
        children = "children"
        if children in regulation and isinstance(regulation[children], list):
            for child in regulation[children]:
                stack.append(child)

    @staticmethod
    def before(regulation, cxt):
        if "before" in regulation:
            Utils.handle(regulation["before"], "before", cxt)

    def rule(self, regulation, ctx):
        rule = "rule"
        ctx["filename"] = getattr(self.source, "filename", None)()
        if isinstance(regulation[rule], str):
            return self.rule_str(regulation[rule], ctx)
        if rule not in regulation:
            raise Exception("唯一标识rule没有定义")
        returned = Utils.handle(regulation[rule], rule, ctx)
        return returned

    def rule_str(self, rule, ctx):
        return self.exper_processor.processor(exper_=rule, context_=ctx)


# 组织数据规则处理器
class OrganizationProcess(BaseProcess):
    pass

