# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from socket import gethostname
from time import time, strftime

from neon_utils.logger import LOG
from neon_utils.mq_utils import send_mq_request
from neon_utils.packaging_utils import get_neon_core_version


# TODO: Enable metric reporting DM
class Stopwatch:
    """
    Provides a stopwatch object compatible with mycroft.metrics Stopwatch.
    """

    def __init__(self, metric_name=None, allow_reporting=False):
        """
        Create a stopwatch object with an optional metric_name
        Args:
            metric_name: name of the metric this stopwatch is measuring
            allow_reporting: boolean flag to allow this stopwatch to report measured metrics
        """
        self._metric = metric_name
        self._report = allow_reporting
        self._context = dict()
        self.start_time = None
        self.time = None

    def __enter__(self):
        self.start()

    def __exit__(self, typ, val, traceback):
        self.stop()
        # self.report()

    # def add_context(self, context: dict):
    #     """
    #     Add context to the measured metric.
    #     Args:
    #         context: dict of arbitrary data to add to this metric reporting
    #     """
    #     if self._metric:
    #         self._context = context

    def start(self):
        self.start_time = time()

    def stop(self):
        self.time = time() - self.start_time
        return self.time

    # def report(self):
    #     if self._metric and self._report:
    #         report_metric(self._metric, self._context)
    #         self._context = dict()


def report_metric(name: str, **kwargs):
    """
    Report a metric over the MQ bus.
    :param name: Name of the metric to report
    :param kwargs: Arbitrary data to include with metric report
    """
    try:
        send_mq_request("/neon_metrics", {**{"name": name}, **kwargs}, "neon_metrics_input", expect_response=False)
        return True
    except Exception as e:
        LOG.error(e)
        return False


def announce_connection():
    try:
        from ovos_config.config import Configuration
        data = {"time": strftime('%Y-%m-%d %H:%M:%S'),
                "name": dict(Configuration()).get("device_name") or "unknown",
                "host": gethostname(),
                "ver": get_neon_core_version()}
        send_mq_request("/neon_metrics", data, "neon_connections_input", expect_response=False)
        return True
    except Exception as e:
        LOG.error(e)
        return False
