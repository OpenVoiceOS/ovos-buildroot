# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse

from ovos_stt_http_server import start_stt_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help="stt plugin to be used", required=True)
    parser.add_argument("--port", help="port number", default=8080)
    parser.add_argument("--host", help="host", default="0.0.0.0")
    args = parser.parse_args()

    start_stt_server(args.engine, args.port, args.host)


if __name__ == '__main__':
    main()
