"""
A simple and lightweight GPSD client.
"""
import json
import re
import socket
from datetime import datetime
from typing import Any, Dict, Iterable, Union

# old versions of gpsd with NTRIP sources emit invalid json which contains trailing
# commas. As the json strings emitted by gpsd are well known to not contain structures
# like `{"foo": ",}"}` it should be safe to remove all commas directly before curly
# braces. (https://github.com/tfeldmann/gpsdclient/issues/1)
REGEX_TRAILING_COMMAS = re.compile(r"\s*,\s*}")


class GPSDClient:
    def __init__(self, host: str = "127.0.0.1", port: Union[str, int] = "2947") -> None:
        self.host = host
        self.port = port
        self.sock = None  # type: Any

    def json_stream(self, filter: Iterable[str] = set()) -> Iterable[str]:
        # Dynamically assemble a regular expression to match the given report classes.
        # This way we don't need to parse the json to filter by report.
        if filter:
            report_classes = set(f.strip().upper() for f in filter)
            filter_regex = re.compile(r'"class":\s?"(%s)"' % "|".join(report_classes))

        self.close()
        self.sock = socket.create_connection(address=(self.host, int(self.port)))
        self.sock.send(b'?WATCH={"enable":true,"json":true}\n')
        expect_version_header = True
        for line in self.sock.makefile("r", encoding="utf-8"):
            answ = line.strip()
            if answ:
                if expect_version_header and not answ.startswith('{"class":"VERSION"'):
                    raise EnvironmentError(
                        "No valid gpsd version header received. Instead received:\n"
                        "%s...\n"
                        "Are you sure you are connecting to gpsd?" % answ[:100]
                    )
                expect_version_header = False

                if not filter or filter_regex.search(answ):
                    cleaned_json = REGEX_TRAILING_COMMAS.sub("}", answ)
                    yield cleaned_json

    def dict_stream(
        self, *, convert_datetime: bool = True, filter: Iterable[str] = set()
    ) -> Iterable[Dict[str, Any]]:
        for line in self.json_stream(filter=filter):
            result = json.loads(line)
            if convert_datetime and "time" in result:
                result["time"] = self._convert_datetime(result["time"])
            yield result

    @staticmethod
    def _convert_datetime(x: Any) -> Union[Any, datetime]:
        """converts the input into a `datetime` object if possible."""
        try:
            if isinstance(x, float):
                return datetime.fromtimestamp(x)
            elif isinstance(x, str):
                # time zone information can be omitted because gps always sends UTC.
                return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            pass
        return x

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None

    def __str__(self):
        return "<GPSDClient(host=%s, port=%s)>" % (self.host, self.port)

    def __del__(self):
        self.close()
