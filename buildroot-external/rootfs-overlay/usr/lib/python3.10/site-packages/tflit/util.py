

# these are handled specially
_HIDDEN_DETAILS = ('name', 'dtype', 'shape', 'index')

def format_details(details, ignore=_HIDDEN_DETAILS, depth=1):
    return '\n'.join(
        '{}{} ({} {}) [i={}]'.format(
            ' '*2, d['name'], d['shape'], d['dtype'].__name__, d['index'])
        + '\n' + format_dict(d, ignore=ignore, depth=depth+2)
        for d in details
    )

def format_dict(data, depth=0, ignore=(), w=2, align=False):
    data = {'{}:'.format(k): v for k, v in data.items() if k not in ignore}
    indent = ' '*w*depth
    return '\n'.join(
        '{}{:<{kw}} {}'.format(
            indent, k,
            ('\n' + format_dict(v, depth=depth+1, ignore=ignore, w=w, align=align))
            if isinstance(v, dict) else v,
            kw=max(len(k) for k in data) if align else 0,
        )
        for k, v in data.items()
        if k not in ignore
    )

def add_border(text, ch='*', extra=2, maxlen=80):
    lines = text.splitlines()
    maxlen = max(len(l) for l in lines) + len(ch) + 1 + extra
    return ch * maxlen + '\n' + (
        '\n'.join('{} {}'.format(ch, l) for l in lines)
    ) + '\n' + ch * maxlen


def get_auto_index(idxs, details, multi_input=None):
    if isinstance(idxs, int):
        idxs = [idxs]
    elif idxs is None:
        idxs = list(range(len(details)))
    multi_input = len(idxs) != 1 if multi_input is None else multi_input

    idxs = [(i, details[i]['index']) for i in idxs]
    return (idxs if multi_input else idxs[:1]), multi_input




# class C:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#
# def _text_wrapper(start, end=C.ENDC):
#     return '{}{{}}{}'.format(start, end).format
#
# red = _text_wrapper(C.FAIL)
# blue = _text_wrapper(C.OKBLUE)
# green = _text_wrapper(C.OKGREEN)
# yellow = _text_wrapper(C.WARNING)
# bold = _text_wrapper(C.BOLD)
# underline = _text_wrapper(C.UNDERLINE)
