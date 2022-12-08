# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import locale
import sys
import time

from tailhead import head, tail, follow_path


def _test():
    import doctest
    doctest.testmod()


def _main(filepath, options):
    try:
        if options.lines > 0:
            with open(filepath, 'rb') as f:
                if options.head:
                    if options.follow:
                        sys.stderr.write('Cannot follow from top of file.\n')
                        sys.exit(1)
                    lines = head(f, options.lines)
                else:
                    lines = tail(f, options.lines)

                encoding = locale.getpreferredencoding()
                for line in lines:
                    print(line.decode(encoding))

        if options.follow:
            for line in follow_path(filepath):
                if line is not None:
                    print(line)
                else:
                    time.sleep(options.sleep)
    except KeyboardInterrupt:
        # Escape silently
        pass


def main():
    from argparse import ArgumentParser
    import sys

    parser = ArgumentParser(prog='pytail')

    test_group = parser.add_argument_group("Test")
    test_group.add_argument('--test', dest='test', default=False, action='store_true',
                            help='run some basic tests')

    parser.add_argument('-n', '--lines', dest='lines', default=10, type=int,
                        help='output the last N lines, instead of the last 10')
    parser.add_argument('file', nargs='?', metavar='FILE', help="path to file")

    head_group = parser.add_argument_group('Head')
    head_group.add_argument('-t', '--top', dest='head', default=False, action='store_true',
                            help='output lines from the top instead of the bottom; does not work with follow')

    tail_group = parser.add_argument_group('Tail')
    tail_group.add_argument('-f', '--follow', dest='follow', default=False, action='store_true',
                            help='output appended data as  the  file  grows')
    tail_group.add_argument('-s', '--sleep-interval', metavar='DELAY', dest='sleep', default=1.0, type=float,
                            help='with -f, sleep for approximately DELAY seconds between iterations')

    args = parser.parse_args()

    if args.test:
        _test()
    elif args.file:
        _main(args.file, args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
