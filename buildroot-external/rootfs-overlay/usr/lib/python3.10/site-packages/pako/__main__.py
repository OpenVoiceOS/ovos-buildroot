# Copyright (c) 2019 Mycroft AI, Inc.
#
# This file is part of Mycroft Skills Manager
# (see https://github.com/MatthewScholefield/mycroft-light).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from argparse import ArgumentParser

from pako.pako_manager import PakoManager


def install(*args, **kwargs):
    return PakoManager().install(*args, **kwargs)


def update(args):
    return PakoManager().update()


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    p = subparsers.add_parser('install')
    p.add_argument('packages', nargs='+')
    subparsers.add_parser('update')
    args = parser.parse_args()
    try:
        result = {'install': install, 'update': update}[args.action](args)
        if result:
            print('{} succeeded'.format(args.action.title()))
            exit(0)
        else:
            print('{} failed'.format(args.action.title()))
            exit(1)
    except KeyboardInterrupt:
        print('Cancelled.')
    except Exception as e:
        print('Error: ' + str(e))
