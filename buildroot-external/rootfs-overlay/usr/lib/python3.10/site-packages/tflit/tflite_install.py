'''
Versions: https://google-coral.github.io/py-repo/tflite-runtime/
Version Info: https://www.tensorflow.org/lite/guide/python
'''
# Fuck it. Pypi you gave me no other choice. You said:
#   ERROR: Packages installed from PyPI cannot depend on packages which are not also hosted on PyPI.
# so I say asdfkadsljsldkfjklsdjflka eat shit. Imma do it anyways. (╯°□°）╯︵ ┻━┻
# apparently this is the recommended way anyways: https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
def install(verbose=False):
    import sys
    import subprocess
    output = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--index-url', 'https://google-coral.github.io/py-repo/', 'tflite_runtime'],
        check=False,
        stdout=sys.stdout if verbose else subprocess.PIPE,
        stderr=sys.stderr)
    # if verbose:
    #     print(output)
    output.check_returncode()

def check_install(verbose=False, upgrade=False, force=False, **kw):
    USER_MESSAGE = (
        "NOTE: The reason that this is even necessary is because tensorflow still "
        "hasn't released tflite_runtime on pypi and pypi freaks out if "
        "a url outside of pypi is included as a dependency. "
        "Once this upstream issue is resolved this message will go away.")
    if upgrade or force:
        # print('tflite is installed, but checking for a newer version.')
        install(verbose=verbose, **kw)
    try:
        import tflite_runtime
    except ImportError as e:
        print(e, 'installing the right version for your system now...')
        if verbose:
            print(USER_MESSAGE)
        install(verbose=verbose, **kw)
        if verbose:
            print('.'*50)
        print('All done! Carry on.')


if __name__ == '__main__':
    import fire
    fire.Fire({'check': check_install, 'install': install, 'upgrade': install})
