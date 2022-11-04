def optional_arg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])

        else:
            def real_decorator(decorates):
                return fn(decorates, *args, **kwargs)

            return real_decorator

    return wrapped_decorator