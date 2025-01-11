# 数据合并
from abc import ABC, abstractmethod
from re import match
from .reconciliation_exper_processor import NifiExpression, DefaultCalcExpression
from .reconciliation_rule import Utils


# 合并数据的基本行为
class DataMerge(ABC):
    @abstractmethod
    def merge(self, arg1, arg2):
        pass

    def merges(self, h):
        pass


# 合并数据
class DefaultMerge(DataMerge):

    # 表达式
    def __init__(self, rules_dict):
        if isinstance(rules_dict, dict):
            self.rules = []
            self.exper = []
            self.filter = []
            self.key_name = []
            self.exper_processor = NifiExpression(DefaultCalcExpression())
            for key in rules_dict.keys():
                self.rules.append(key.split("."))
                self.exper.append(rules_dict[key]["exper"])
                self.key_name.append(rules_dict[key]["name"])
                if "filter" not in rules_dict[key].keys():
                    self.filter.append(lambda ctx: True)
                else:
                    self.filter.append(rules_dict[key]["filter"])
        else:
            raise Exception()

    # 深度优先遍历context，通过layer_num去匹配exper和rules，把匹配后的
    # layer_num: 记录当前变量处于第几层。
    # layer_key_name: 记录深度上的key名
    def parse(self, context, rules, exper, origin, filter_call):
        if isinstance(context, dict):
            key_name_stack = list(reversed([key for key in context.keys()]))
            # 深度遍历context字典
            obj_stack = [context[key] for key in list(reversed([key for key in context.keys()]))]
            # 维护变量对应的深度
            layer_stack = [0 for key in range(len(obj_stack))]
            # 维护一个深度上的变量名
            layer_key_name = []
            last_layer = -1
            while len(key_name_stack) > 0:
                key_name = key_name_stack.pop()
                pack_obj = obj_stack.pop()
                layer_num = layer_stack.pop()

                # 维护一个变量名栈，用来记录深度上的变量
                # 模拟一个深度优先搜索，这里保存的
                if layer_num > last_layer:
                    layer_key_name.append(key_name)
                else:
                    while last_layer >= layer_num:
                        layer_key_name.pop()
                        last_layer -= 1
                    layer_key_name.append(key_name)

                last_layer = layer_num

                # 规则匹配
                if layer_num < len(rules) and layer_num == len(rules) - 1:
                    all_match = True
                    for i in range(layer_num):
                        key_name = layer_key_name[i]
                        all_match &= match("^" + rules[i] + "$", key_name) is not None

                    if all_match:
                        exper_copy = str(exper)
                        # 搜索变量
                        filter_ = Utils.handle(filter_call, "filter", pack_obj)
                        if filter_:
                            pack_obj[origin] = self.exper_processor.processor(exper_copy, pack_obj)

                # 深度优先
                if isinstance(pack_obj, dict):
                    items = list(reversed([item for item in pack_obj.keys()]))
                    for item in items:
                        key_name_stack.append(item)
                        obj_stack.append(pack_obj[item])
                        layer_stack.append(layer_num + 1)
        else:
            raise Exception()

    def merge(self, arg1, arg2):
        if isinstance(arg1, dict) and isinstance(arg2, dict):
            variable_stack = [item for item in arg2.keys()]
            obj2_stack = [arg2 for i in arg2.keys()]
            obj1_stack = [arg1 for i in arg2.keys()]
            while len(variable_stack) > 0:
                key = variable_stack.pop()
                obj1 = obj1_stack.pop()
                obj2 = obj2_stack.pop()
                if key not in obj1:
                    obj1[key] = obj2[key]
                if not isinstance(obj1[key], dict) and not isinstance(obj2[key], dict):
                    obj1[key] = obj2[key]
                else:
                    for item in obj2[key].keys():
                        obj2_stack.append(obj2[key])
                        obj1_stack.append(obj1[key])
                        variable_stack.append(item)
            return arg1
        else:
            raise Exception()

    # 合并数据
    def merges(self, h):
        if isinstance(h, list) and all(isinstance(item, dict) for item in h):
            if len(h) >= 2:
                while len(h) >= 2:
                    h.append(self.merge(h.pop(), h.pop()))
                merge_result = h.pop()
                for i in range(len(self.rules)):
                    self.parse(merge_result, self.rules[i], self.exper[i], str(self.key_name[i]), self.filter[i])
                return merge_result
            else:
                raise Exception("数据长度必须大于等于2，不然合并有啥意义？")
        else:
            raise Exception()
