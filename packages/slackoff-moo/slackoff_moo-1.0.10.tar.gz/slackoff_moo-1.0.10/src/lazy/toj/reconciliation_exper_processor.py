from abc import ABC, abstractmethod
from re import findall, match
from sympy import sympify, SympifyError
import math
import re


# 表达式处理器
class ExperProcessor(ABC):
    @abstractmethod
    def processor(self, exper_, context_):
        pass


# 处理中缀表达式
class NifiExpression(ExperProcessor):
    def __init__(self, calc):
        if not isinstance(calc, CalcExpression):
            raise TypeError
        self.calc = calc

    def processor(self, exper_, context_):
        if isinstance(exper_, str):
            variable_exper = findall(r"\$\{([]\[a-zA-Z0-9\u4e00-\u9fff\"\']+)}", exper_)
            # 解析变量，寻找变量在上下文的值，并进行替换
            try:
                for i in range(len(variable_exper)):
                    variable = variable_exper[i]
                    exp_val = context_
                    chains = findall(r"(\[[a-zA-Z0-9-\u4e00-\u9fff\"\']+]|[a-zA-Z0-9-\u4e00-\u9fff]+)", variable)
                    for chain in chains:
                        if exp_val is None:
                            return None
                        if "[" in chain and "]" in chain:
                            key = findall(r"[^]\"\'\[]+", chain)
                            if match(r"\d+", key[0]) is not None:
                                if int(key[0]) > len(exp_val):
                                    return None
                                exp_val = exp_val[int(key[0])]
                            elif isinstance(key[0], str):
                                if key[0] not in exp_val:
                                    return None
                                exp_val = exp_val[key[0]]
                        elif match("^[0-9]+$", chain) is not None:
                            if int(chain) > len(exp_val):
                                return None
                            exp_val = exp_val[int(chain)]
                        elif match("^[a-zA-Z0-9-\u4e00-\u9fff]+$", chain) is not None:
                            if chain not in exp_val:
                                return None
                            exp_val = exp_val[chain]
                    if not isinstance(exp_val, str):
                        exper_ = exper_.replace("${" + variable + "}", str(exp_val))
                    else:
                        exper_ = exper_.replace("${" + variable + "}", "'" + exp_val + "'")
                if self.is_valid_expression_sympy(exper_):
                    return self.calc.calc(exper_)
                return exper_
            except Exception:
                raise Exception("请检查表达式：", exper_)
        else:
            raise ValueError("表达式必须处理为数组")

    @staticmethod
    def is_valid_expression_sympy(expression):
        try:
            # 尝试将表达式解析为 sympy 对象
            sympify(expression)
            return True
        except (SympifyError, ValueError, TypeError):
            # 如果解析失败，则表达式无效
            return False


class CalcExpression(ABC):
    @abstractmethod
    def calc(self, exper_):
        pass


class DefaultCalcExpression(CalcExpression):
    safe_globals = {
        '__builtins__': {},
        'math': math,
        'str': str,
        'int': int,
        'float': float,
        're': re,
        'findall': findall,
        'match': match,
        'round': round
    }

    def calc(self, expression):
        try:
            compiled_code = compile(expression, "<string>", "eval")
            result = eval(compiled_code, self.safe_globals)
            return result
        except (SyntaxError, NameError, TypeError) as e:
            return f"Invalid expression: {e}"
