from .tflite_install import check_install

def install(verbose=True, **kw):
    return check_install(verbose=verbose, **kw)

if __name__ == '__main__':
    import fire
    fire.Fire(install)