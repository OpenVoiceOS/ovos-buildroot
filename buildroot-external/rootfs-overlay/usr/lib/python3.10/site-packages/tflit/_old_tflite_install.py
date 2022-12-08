'''
Versions: https://google-coral.github.io/py-repo/tflite-runtime/
Version Info: https://www.tensorflow.org/lite/guide/python
'''

def get_links():
    import re
    import urllib.request
    with urllib.request.urlopen('https://google-coral.github.io/py-repo/tflite-runtime/') as page:
        content = page.read().decode('utf-8')
    return re.findall(r'<li>\s*<a\s+.*href="(.*)".*>.*<\/a>\s*</li>', content)


def with_keys(links):
    # links: https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp35-cp35m-linux_aarch64.whl#sha256=358ba7558711ef451192fe5d34e369df686012885a08c99d63c3ada91aeb0f18
    # keys:  ('tflite_runtime', '2.5.0', 'cp35', 'cp35m', 'linux_aarch64') -> ('2.5.0', 'cp35', 'linux', 'aarch64')
    keys = [l.split('#')[0].split('/')[-1].rsplit('.', 1)[0].split('-') for l in links]
    keys = [(k[1], k[2]) + tuple(k[4].split('_', 1)) for k in keys]
    return dict(zip(keys, links))


def _find_version(links, version=None, pyversion=None, platform=None, arch=None):
    import fnmatch
    searchkey = version, pyversion, platform, arch
    return next((
        link for key, link in sorted(with_keys(links).items(), reverse=True)
        if all(y is None or fnmatch.fnmatch(x, y) for x, y in zip(key, searchkey))
    ), None)


def get_tflite_url(version=None):
    import sys, platform
    PLATFORMS = {'Linux': 'linux', 'Darwin': 'macosx', 'Windows': 'win'}
    return _find_version(
        get_links(), version=version,
        pyversion='cp' + ''.join(map(str, sys.version_info[:2])),
        platform=PLATFORMS.get(platform.system()),
        arch='*' + platform.uname()[4])


def replace_all(txt, replace):
    for old, new in replace.items():
        if isinstance(txt, bytes):
            old, new = old.encode('utf-8'), new.encode('utf-8')
        txt = txt.replace(old, new)
    return txt

def _download_and_rename_zip_content(url, new='tflite-runtime-unofficial', original='tflite-runtime', outdir='.'):
    import os
    import io
    import zipfile
    import urllib.request

    # FILES = ['RECORD']
    replace = {original: new, original.replace('-', '_'): new.replace('-', '_')}
    fname = replace_all(url.split('#')[0].split('/')[-1], replace)
    os.makedirs(outdir, exist_ok=True)
    fname = os.path.join(outdir, fname)

    with urllib.request.urlopen(url) as page:
        with zipfile.ZipFile(io.BytesIO(page.read()), 'r') as zin:
            with zipfile.ZipFile(fname, 'w') as zout:
                for item in zin.infolist():
                    fname_i, content = item.filename, zin.read(item.filename)
                    # if item.filename in FILES:
                    fname_i, content = replace_all(fname_i, replace), replace_all(content, replace)
                    zout.writestr(fname_i, content)
    return fname

def download_all(outdir='.', new='tflite-runtime-unofficial', original='tflite-runtime'):
    return [_download_and_rename_zip_content(url, new, original, outdir=outdir) for url in get_links()]



# URL = (
#     'https://dl.google.com/coral/python/tflite_runtime-'
#     '{version}-cp{py}-cp{py}{m}-{platform}_{arch}.whl')
# URL = (
#     'https://github.com/google-coral/pycoral/releases/download/release-frogfish/'
#     'tflite_runtime-{version}-cp{py}-cp{py}{m}-{platform}_{arch}.whl'
# )
#
# PLATFORMS = {
#     'Linux': 'linux',
#     'Darwin': 'macosx',
#     'Windows': 'win',
# }
#
# VERSIONS = {
#     'Linux': ['35', '36', '37', '38'],
#     'Darwin': ['35', '36', '37', '38'],
#     'Windows': ['35', '36', '37', '38'],
# }
# NO_M = ['38']
#
# MAC_VERSION = 10, 15

# def get_tflite_url(version='2.5.0'):
#     import sys
#     import platform
#
#     system = platform.system()  # Linux, Darwin, Windows
#     platfm = PLATFORMS.get(system)  # linux, macosx, win
#     arch = platform.uname()[4]  # armv7l, aarch64, x86_64, amd64
#     py_version = '{}{}'.format(*sys.version_info)  # (3, 8)
#
#     if system == 'Linux':
#         pass
#     elif system == 'Darwin':
#         platfm += '_' + '_'.join(map(str, MAC_VERSION))
#     elif system == 'Windows':
#         pass
#     else:
#         raise ValueError('Unknown system: {}'.format(system))
#
#     return URL.format(
#         version=version, py=py_version, m='m'*(py_version not in NO_M),
#         platform=platfm,
#         arch=arch,
#     )



# Fuck it. Pypi you gave me no other choice. You said:
#   ERROR: Packages installed from PyPI cannot depend on packages which are not also hosted on PyPI.
# so I say asdfkadsljsldkfjklsdjflka eat shit. Imma do it anyways. (╯°□°）╯︵ ┻━┻
# apparently this is the recommended way anyways: https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
def install(verbose=False, **kw):
    import sys
    import subprocess
    # url = get_tflite_url(**kw)
    # if verbose:
    #     print('Getting tflite from:', url)
    output = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--index-url', 'https://google-coral.github.io/py-repo/', 'tflite_runtime'],  #url
        check=False,
        stdout=sys.stdout if verbose else subprocess.PIPE,
        stderr=sys.stderr)
    if verbose:
        print(output)
    output.check_returncode()

def check_install(verbose=False, upgrade=False, **kw):
    USER_MESSAGE = (
        "NOTE: The reason that this is even necessary is because tensorflow still "
        "hasn't released tflite_runtime on pypi and pypi freaks out if "
        "a url outside of pypi is included as a dependency. "
        "Once this upstream issue is resolved this message will go away.")
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
    else:
        if upgrade:
            print('tflite is installed, but checking for a newer version.')
            install(verbose=verbose, **kw)


if __name__ == '__main__':
    import fire
    fire.Fire({'check': check_install, 'install': install, 'download_all': download_all})
