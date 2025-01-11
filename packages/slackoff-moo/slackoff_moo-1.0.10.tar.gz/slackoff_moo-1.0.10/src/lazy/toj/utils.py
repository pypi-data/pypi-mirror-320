
class Utils:
    @staticmethod
    def handle(call, func, data):
        if callable(call):
            return call(data)
        elif isinstance(call, object):
            return getattr(call, func)(data)
        elif isinstance(call, str):
            return call

