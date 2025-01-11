# 数据源，加载数据源
from abc import ABC, abstractmethod
from os import listdir, path
from collections.abc import Iterator


class DataSource(ABC):
    @abstractmethod
    def load(self):
        pass


# 默认解析
class XlsxDataSource(DataSource):
    def __init__(self, init_):
        self.folders = init_["folders"]
        self.files = []
        self.current_file_index = 0
        self.iter = None
        # init_iter 初始化
        # iterator_item 获取单元格的值
        # filter 过滤文件
        self.init_ = init_
        # 加载迭代器
        self.load()

    def load(self):
        if isinstance(self.folders, list) and all(isinstance(item, str) for item in self.folders):
            stack = []
            [stack.append(item) for item in self.folders]
            while len(stack) > 0:
                folder = stack.pop()
                if path.isfile(folder):
                    self.files.append(folder)
                else:
                    for name in listdir(folder):
                        current_path = path.join(folder, name)
                        if path.isfile(current_path):
                            if "filter" not in self.init_:
                                self.files.append(current_path)
                            elif self.call_method(current_path, self.init_["filter"], "filter"):
                                self.files.append(current_path)
                        elif path.isdir(current_path):
                            stack.append(current_path)
        else:
            raise Exception('folders must be a list')

    def __next__(self):
        if self.iter is None:
            self.call_method(self, self.init_["init_iterator"], "init_iterator")
        elif not isinstance(self.iter, Iterator):
            raise Exception('iter must be an iterator')
        try:
            return self.call_method(self.iter.__next__(), self.init_["iterator_item"], "iterator_item")
        except StopIteration:
            self.call_method(self, self.init_["init_iterator"], "init_iterator")
            if self.iter is None:
                raise StopIteration
            return self.call_method(self.iter.__next__(), self.init_["iterator_item"], "iterator_item")

    def __iter__(self):
        return self

    @staticmethod
    def call_method(ctx, method, method_name):
        if callable(method):
            return method(ctx)
        elif isinstance(method, object):
            return getattr(method, method_name, None)(ctx)
        else:
            raise Exception(method_name + ' method must be a callable')

    def filename(self):
        return self.files[self.current_file_index - 1]
