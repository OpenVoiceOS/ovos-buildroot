import sys

PY3K = sys.version_info[0] == 3


if PY3K:
    # Based on six
    def int2byte(x):
        return bytes((x,))
else:
    int2byte = chr


def get_validator(tp, name):
    def f(x):
        if not isinstance(x, tp):
            raise TypeError("Expected %s" % name)
    return f


validators = {}
for tp, name in [(int, 'integer'), (float, 'float'),
                 (str, 'string'), (dict, 'dict'), (list, 'list')]:
    validators[tp] = get_validator(tp, name)


def validate(**schema):
    def wrapper(fn):
        code = fn.__code__
        nargs = code.co_argcount
        varnames = code.co_varnames
        if PY3K:
            defaults = fn.__defaults__ if fn.__defaults__ else []
            kwdefaults = fn.__kwdefaults__ if fn.__kwdefaults__ else {}
        else:
            defaults = fn.func_defaults if fn.func_defaults else []
            kwdefaults = {}

        def validator(*args):
            largs = len(args)

            if largs != nargs and largs + len(defaults) + len(kwdefaults) != nargs:
                raise TypeError("%s() takes exactly %d arguments (%d given)" %
                                (fn.__name__, nargs, len(args) + len(kwdefaults)))
            for i, value in enumerate(args):
                name = varnames[i]
                if name not in schema:
                    continue
                typ = schema[name]
                validators[typ](value)
            if largs < nargs:
                for i in range(largs, nargs):
                    value = defaults[largs - i]
                    name = varnames[i]
                    if name not in schema:
                        continue
                    typ = schema[name]
                    validators[typ](value)
            return fn(*args, **kwdefaults)
        validator.__name__ = fn.__name__
        validator.__doc__ = fn.__doc__
        return validator
    return wrapper
