

def converse_handler():
    """Decorator for aliasing a method as the converse method"""

    def real_decorator(func):
        if not hasattr(func, 'converse'):
            func.converse = True
        return func

    return real_decorator
