# 差异对账，提供计算每天应收和实收的差异，以及小计。
# 组织数据结构 -> 合并（基于数据结构自定义合并规则）-> 把合并数据写入excel（编写合并规则）
from os import listdir, path
# 规则处理器


# 使用嵌套键值对的方式组织数据
class OrganizationColl:
    def __int__(self, folders, namespace):
        self.__init__(folders=folders, namespace=namespace, organization_process=OrganizationRuleProcessor())

    def __init__(self, folders, namespace, organization_process):
        if not isinstance(folders, list):
            Exception()
        self.filenames = []
        self.namespace = namespace  # 标识组织好的数据
        self.rule_key_deep = {}  # 记录规则的深度
        self.table_result = {}  # 组织结果
        self.folders = folders  # 目录
        self.organization_process = organization_process  # 规则处理器

    # 组织数据结构
    def organization(self, regulation):
        filename_filter = getattr(regulation.fileHandle, "filter")
        load_file = getattr(regulation.fileHandle, "load")  # 加载文件数据
        parse = getattr(regulation.fileHandle, "parse")  # 解析数据
        stack = self.folders.copy()
        while len(stack) > 0:  # 深度遍历文件
            folder = stack.pop()
            all_files = listdir(folder)
            for dirname in all_files:
                if filename_filter(folder + dirname):  # 文件过滤
                    if path.isdir(dirname):
                        stack.append(dirname)
                    elif path.isfile(dirname):
                        iterator = load_file(folder + dirname)  # 加载数据，返回一个标准迭代器
                        if not hasattr(iterator, "__iter__") and hasattr(iterator, "__next__"):
                            Exception("不是迭代器")
                        # 迭代数据
                        for item in iterator:
                            parsed = parse(item)
                            # data是放到代码
                            self.parse_rules(rules=regulation.rules, data={
                                "row": parsed,
                                "filename": dirname,
                                "folder": folder
                            })

    # 规则解析
    def parse_rules(self, rules, data):
        if "organization" not in rules:
            Exception("organization必填")

        stack = [rules]
        result_reference = [self.table_result]
        while len(stack) > 0:
            regulation = stack.pop()
            # 数据过滤
            if getattr(self.organization_process, "filter")(regulation, data):
                continue

            if "rule" not in regulation:
                continue

            # 执行规则
            if "rule" in regulation:
                rule = regulation["rule"]
                if callable(rule):
                    return_a = rule(data, result_reference[len(result_reference) - 1])
                    if "key" in return_a and "val" in return_a:
                        result = result_reference.pop()


# 组织数据的规则处理器
class OrganizationRuleProcessor:
    def __init__(self):
        pass

    # 组织数据过程中，过滤掉指定数据
    @staticmethod
    def filter(regulation, data):
        if "filter" not in regulation.organization:
            return False
        filter_call = regulation.organization.filter
        if callable(filter_call):
            if filter_call(data):
                return True
        elif isinstance(filter_call, object):
            if getattr(filter_call, "filter")(data):
                return True
        return False

    # 对孩子数据的处理
    @staticmethod
    def children(regulation, data, stack):
        if "children" in regulation.organization:
            children = regulation.organization.children
            if isinstance(children, list) and len(children) > 0:
                for child_regulation in children:
                    stack.append(child_regulation)
