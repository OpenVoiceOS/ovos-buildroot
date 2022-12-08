
def fallback_handler(priority=50):
    def real_decorator(func):
        if not hasattr(func, 'fallback_priority'):
            func.fallback_priority = priority
        return func

    return real_decorator
