import json
import os
import time

from cutecharts.charts import Pie, Bar, Scatter
from ovos_local_backend.database.metrics import JsonMetricDatabase
from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.database.utterances import JsonUtteranceDatabase
from ovos_local_backend.database.wakewords import JsonWakeWordDatabase
from pywebio.input import actions
from pywebio.output import put_text, popup, put_code, put_markdown, put_html, use_scope, put_image

chart_type = Pie


def device_select(back_handler=None):
    devices = {uuid: f"{device['name']}@{device['device_location']}"
               for uuid, device in DeviceDatabase().items()}
    buttons = [{'label': "All Devices", 'value': "all"}] + \
              [{'label': d, 'value': uuid} for uuid, d in devices.items()]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if devices:
        uuid = actions(label="What device would you like to inspect?",
                       buttons=buttons)
        if uuid == "main":
            metrics_menu(back_handler=back_handler)
            return
        else:
            if uuid == "all":
                uuid = None
            if uuid is not None:
                with use_scope("main_view", clear=True):
                    put_markdown(f"\nDevice: {uuid}")
            metrics_menu(uuid=uuid, back_handler=back_handler)
    else:
        popup("No devices paired yet!")
        metrics_menu(back_handler=back_handler)


def metrics_select(back_handler=None, uuid=None):
    buttons = []
    db = JsonMetricDatabase()
    if not len(db):
        with use_scope("main_view", clear=True):
            put_text("No metrics uploaded yet!")
        metrics_menu(back_handler=back_handler, uuid=uuid)
        return

    for m in db:
        name = f"{m['metric_id']}-{m['metric_type']}"
        if uuid is not None and m["uuid"] != uuid:
            continue
        buttons.append({'label': name, 'value': m['metric_id']})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
    opt = actions(label="Select a metric to inspect",
                  buttons=buttons)
    if opt == "main":
        device_select(back_handler=back_handler)
        return
    # id == db_position + 1
    with use_scope("main_view", clear=True):
        put_markdown("# Metadata")
        put_code(json.dumps(db[opt - 1], indent=4), "json")
    metrics_select(back_handler=back_handler, uuid=uuid)


def _plot_metrics(uuid, selected_metric="types"):
    if uuid is not None:
        m = DeviceMetricsReportGenerator(uuid)
    else:
        m = MetricsReportGenerator()

    with use_scope("main_view", clear=True):
        if uuid is not None:
            put_markdown(f"\nDevice: {uuid}")
        if selected_metric == "timings":
            put_html(m.timings_chart().render_notebook())
        elif selected_metric == "stt":
            silents = max(0, m.total_stt - m.total_utt)
            put_markdown(f"""Total Transcriptions: {m.total_stt}
                    Total Recording uploads: {m.total_utt}

                    Silent Activations (estimate): {silents}""")
            if chart_type == Pie:
                put_html(m.stt_pie_chart().render_notebook())
            else:
                put_html(m.stt_bar_chart().render_notebook())
        elif selected_metric == "devices":
            md = f"""# Devices Report
                        Total Devices: {m.total_devices}

                        Total untracked: {len(m.untracked_devices)}
                        Total active (estimate): {len(m.active_devices)}
                        Total dormant (estimate): {len(m.dormant_devices)}"""
            put_markdown(md)
            if chart_type == Pie:
                put_html(m.devices_pie_chart().render_notebook())
            else:
                put_html(m.devices_bar_chart().render_notebook())
        elif selected_metric == "intents":
            txt_estimate = max(m.total_intents + m.total_fallbacks - m.total_stt, 0)
            stt_estimate = max(m.total_intents + m.total_fallbacks - txt_estimate, 0)
            md = f"""# Intent Matches Report
                        Total queries: {m.total_intents + m.total_fallbacks}

                        Total text queries (estimate): {txt_estimate}
                        Total speech queries (estimate): {stt_estimate}

                        Total Matches: {m.total_intents}"""
            put_markdown(md)
            if chart_type == Bar:
                put_html(m.intents_bar_chart().render_notebook())
            else:
                put_html(m.intents_pie_chart().render_notebook())
        elif selected_metric == "ww":
            bad = max(0, m.total_stt - m.total_ww)
            silents = max(0, m.total_stt - m.total_utt)
            put_markdown(f"""Total WakeWord uploads: {m.total_ww}

            Total WakeWord detections (estimate): {m.total_stt}
            False Activations (estimate): {bad or silents}
            Silent Activations (estimate): {silents}""")

            if chart_type == Pie:
                put_html(m.ww_pie_chart().render_notebook())
            else:
                put_html(m.ww_bar_chart().render_notebook())
        elif selected_metric == "tts":
            if chart_type == Pie:
                put_html(m.tts_pie_chart().render_notebook())
            else:
                put_html(m.tts_bar_chart().render_notebook())
        elif selected_metric == "types":
            put_markdown(f"""
        # Metrics Report

        Total Intents: {m.total_intents}
        Total Fallbacks: {m.total_fallbacks}
        Total Transcriptions: {m.total_stt}
        Total TTS: {m.total_tts}
        """)
            if chart_type == Pie:
                put_html(m.metrics_type_pie_chart().render_notebook())
            else:
                put_html(m.metrics_type_bar_chart().render_notebook())
        elif selected_metric == "fallback":
            f = 0
            if m.total_intents + m.total_fallbacks > 0:
                f = m.total_intents / (m.total_intents + m.total_fallbacks)
            put_markdown(f"""
                        # Fallback Matches Report

                        Total queries: {m.total_intents + m.total_fallbacks}
                        Total Intents: {m.total_intents}
                        Total Fallbacks: {m.total_fallbacks}

                        Failure Percentage (estimate): {1 - f}
                        """)
            if chart_type == Pie:
                put_html(m.fallback_pie_chart().render_notebook())
            else:
                put_html(m.fallback_bar_chart().render_notebook())
        elif selected_metric == "opt-in":
            md = ""
            if uuid is None:
                md = f"""# Open Dataset Report
            Total Registered Devices: {len(DeviceDatabase())}
            Currently Opted-in: {len([d for d in DeviceDatabase() if d.opt_in])}
            Unique Devices seen: {m.total_devices}"""

            # Open Dataset Report"""

            md += f"""

            Total Metrics submitted: {m.total_metrics}
            Total WakeWords submitted: {m.total_ww}
            Total Utterances submitted: {m.total_utt}"""

            put_markdown(md)
            if chart_type == Pie:
                put_html(m.dataset_pie_chart().render_notebook())
            else:
                put_html(m.dataset_bar_chart().render_notebook())


def metrics_menu(back_handler=None, uuid=None, selected_metric="types"):
    global chart_type

    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/metrics.png', 'rb').read()
        put_image(img)

    _plot_metrics(uuid, selected_metric)

    buttons = [{'label': 'Timings', 'value': "timings"},
               {'label': 'Metric Types', 'value': "types"},
               {'label': 'Intents', 'value': "intents"},
               {'label': 'FallbackSkill', 'value': "fallback"},
               {'label': 'STT', 'value': "stt"},
               {'label': 'TTS', 'value': "tts"},
               {'label': 'Wake Words', 'value': "ww"},
               {'label': 'Open Dataset', 'value': "opt-in"}]
    if chart_type == Pie:
        buttons.append({'label': 'Bar style graphs', 'value': "chart"})
    elif chart_type == Bar:
        buttons.append({'label': 'Pie style graphs', 'value': "chart"})
    if uuid is not None:
        buttons.append({'label': 'Delete Device metrics', 'value': "delete_metrics"})
    else:
        buttons.insert(1, {'label': 'Devices', 'value': "devices"})
        buttons.append({'label': 'Inspect Devices', 'value': "metrics"})
        buttons.append({'label': 'Delete ALL metrics', 'value': "delete_metrics"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)

    if opt == "chart":
        if chart_type == Pie:
            chart_type = Bar
        else:
            chart_type = Pie
    elif opt in ["devices", "intents", "stt", "ww", "tts", "types", "fallback", "opt-in", "timings"]:
        selected_metric = opt
    elif opt == "metrics":
        device_select(back_handler=back_handler)
    elif opt == "delete_metrics":
        if uuid is not None:
            with use_scope("main_view", clear=True):
                put_markdown(f"\nDevice: {uuid}")
        with popup("Are you sure you want to delete the metrics database?"):
            put_text("this can not be undone, proceed with caution!")
            put_text("ALL metrics will be lost")
        opt = actions(label="Delete metrics database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            os.remove(JsonMetricDatabase().db.path)
            with use_scope("main_view", clear=True):
                if back_handler:
                    back_handler()
        else:
            metrics_menu(back_handler=back_handler, uuid=uuid,
                         selected_metric=selected_metric)
        return
    elif opt == "main":
        with use_scope("main_view", clear=True):
            if uuid is not None:
                device_select(back_handler=back_handler)
            elif back_handler:
                back_handler()
        return
    metrics_menu(back_handler=back_handler, uuid=uuid,
                 selected_metric=selected_metric)


class MetricsReportGenerator:
    def __init__(self):
        self.total_intents = 0
        self.total_fallbacks = 0
        self.total_stt = 0
        self.total_tts = 0
        self.total_ww = len(JsonWakeWordDatabase())
        self.total_utt = len(JsonUtteranceDatabase())
        self.total_devices = len(DeviceDatabase())
        self.total_metrics = len(JsonMetricDatabase())

        self.intents = {}
        self.fallbacks = {}
        self.ww = {}
        self.tts = {}
        self.stt = {}
        self.devices = {}

        self.stt_timings = []
        self.tts_timings = []
        self.intent_timings = []
        self.fallback_timings = []
        self.device_timings = []

        self.load_metrics()

    def reset_metrics(self):
        self.total_intents = 0
        self.total_fallbacks = 0
        self.total_stt = 0
        self.total_tts = 0
        self.total_ww = len(JsonWakeWordDatabase())
        self.total_metrics = len(JsonMetricDatabase())
        self.total_utt = len(JsonUtteranceDatabase())
        self.total_devices = 0

        self.intents = {}
        self.devices = {}
        self.fallbacks = {}
        self.tts = {}
        self.stt = {}
        self.ww = {}

        self.stt_timings = []
        self.tts_timings = []
        self.intent_timings = []
        self.fallback_timings = []
        self.device_timings = []

    def load_metrics(self):
        self.reset_metrics()
        for m in JsonMetricDatabase():
            if m["uuid"] not in self.devices:
                self.total_devices += 1
            self._process_metric(m)
        for ww in JsonWakeWordDatabase():
            if ww["meta"]["name"] not in self.ww:
                self.ww[ww["meta"]["name"]] = 0
            else:
                self.ww[ww["meta"]["name"]] += 1

    @property
    def active_devices(self):
        thresh = time.time() - 7 * 24 * 60 * 60
        return [uuid for uuid, ts in self.devices.items()
                if ts > thresh and uuid not in self.untracked_devices]

    @property
    def dormant_devices(self):
        return [uuid for uuid in self.devices.keys()
                if uuid not in self.untracked_devices
                and uuid not in self.active_devices]

    @property
    def untracked_devices(self):
        return [dev.uuid for dev in DeviceDatabase() if not dev.opt_in]

    # cute charts
    def timings_chart(self):
        chart = Scatter("Execution Time")
        chart.set_options(y_tick_count=8, is_show_line=True,
                          x_label="Unix Time", y_label="Seconds")
        chart.add_series(
            "STT", [(z[0], z[1]) for z in self.stt_timings]
        )
        chart.add_series(
            "TTS", [(z[0], z[1]) for z in self.tts_timings]
        )
        chart.add_series(
            "Intent Matching", [(z[0], z[1]) for z in self.intent_timings]
        )
        chart.add_series(
            "Fallback Handling", [(z[0], z[1]) for z in self.fallback_timings]
        )
        return chart

    def devices_pie_chart(self):
        chart = Pie("Devices")
        chart.set_options(
            labels=["active", "dormant", "untracked"],
            inner_radius=0,
        )
        chart.add_series([len(self.active_devices),
                          len(self.dormant_devices),
                          len(self.untracked_devices)])
        return chart

    def devices_bar_chart(self):
        chart = Bar("Devices")
        chart.set_options(
            labels=["active", "dormant", "untracked"],
            x_label="Status", y_label="Number"
        )
        chart.add_series("Count", [len(self.active_devices),
                                   len(self.dormant_devices),
                                   len(self.untracked_devices)])
        return chart

    def ww_bar_chart(self):
        chart = Bar("Wake Words")
        labels = []
        series = []
        for ww, count in self.ww.items():
            labels.append(ww)
            series.append(count)

        chart.set_options(
            labels=labels, x_label="Wake Word", y_label="# Submitted"
        )
        chart.add_series("Count", series)
        return chart

    def ww_pie_chart(self):
        chart = Pie("Wake Words")
        labels = []
        series = []
        for ww, count in self.ww.items():
            labels.append(ww)
            series.append(count)

        chart.set_options(
            labels=labels,
            inner_radius=0,
        )
        chart.add_series(series)
        return chart

    def dataset_pie_chart(self):
        chart = Pie("Uploaded Data")
        chart.set_options(
            labels=["wake-words", "utterances", "metrics"],
            inner_radius=0,
        )
        chart.add_series([self.total_ww, self.total_utt, self.total_metrics])
        return chart

    def dataset_bar_chart(self):
        chart = Bar("Uploaded Data")
        chart.set_options(
            labels=["wake-words", "utterances", "metrics"],
            x_label="Data Type", y_label="# Submitted"
        )
        chart.add_series("Count", [self.total_ww, self.total_utt, self.total_metrics])
        return chart

    def metrics_type_bar_chart(self):
        chart = Bar("Metric Types")
        chart.set_options(
            labels=["intents", "fallbacks", "stt", "tts"],
            x_label="Metric Type", y_label="# Submitted"
        )
        chart.add_series("Number", [self.total_intents,
                                    self.total_fallbacks,
                                    self.total_stt,
                                    self.total_tts])
        return chart

    def metrics_type_pie_chart(self):
        chart = Pie("Metric Types")
        chart.set_options(
            labels=["intents", "fallbacks", "stt", "tts"],
            inner_radius=0,
        )
        chart.add_series([self.total_intents,
                          self.total_fallbacks,
                          self.total_stt,
                          self.total_tts])
        return chart

    def intents_bar_chart(self):
        chart = Bar("Intent Matches")
        chart.set_options(labels=list(self.intents.keys()),
                          x_label="Intent Name", y_label="Times Triggered")
        chart.add_series("Count", list(self.intents.values()))
        return chart

    def intents_pie_chart(self):
        chart = Pie("Intent Matches")
        chart.set_options(
            labels=list(self.intents.keys()),
            inner_radius=0,
        )
        chart.add_series(list(self.intents.values()))
        return chart

    def fallback_bar_chart(self):
        chart = Bar("Fallback Skills")
        chart.set_options(
            labels=list(self.fallbacks.keys()),
            x_label="Fallback Handler", y_label="Times Triggered"
        )
        chart.add_series("Count", list(self.fallbacks.values()))
        return chart

    def fallback_pie_chart(self):
        chart = Pie("Fallback Skills")
        chart.set_options(
            labels=list(self.fallbacks.keys()),
            inner_radius=0,
        )
        chart.add_series(list(self.fallbacks.values()))
        return chart

    def tts_bar_chart(self):
        chart = Bar("Text To Speech Engines")
        chart.set_options(
            labels=list(self.tts.keys()),
            x_label="Engine", y_label="Times Triggered"
        )
        chart.add_series("Count", list(self.tts.values()))
        return chart

    def tts_pie_chart(self):
        chart = Pie("Text To Speech Engines")
        chart.set_options(
            labels=list(self.tts.keys()),
            inner_radius=0,
        )
        chart.add_series(list(self.tts.values()))
        return chart

    def stt_bar_chart(self):
        chart = Bar("Speech To Text Engines")
        chart.set_options(
            labels=list(self.stt.keys()),
            x_label="Engine", y_label="Times Triggered"
        )
        chart.add_series("Count", list(self.stt.values()))
        return chart

    def stt_pie_chart(self):
        chart = Pie("Speech To Text Engines")
        chart.set_options(
            labels=list(self.stt.keys()),
            inner_radius=0,
        )
        chart.add_series(list(self.stt.values()))
        return chart

    def _process_metric(self, m):
        start = m["meta"]["start_time"]
        end = m["meta"]["time"]
        duration = end - start
        if m["uuid"] not in self.devices or \
                m["meta"]["time"] > self.devices[m["uuid"]]:
            self.devices[m["uuid"]] = m["meta"]["time"]
        if m["metric_type"] == "intent_service":
            label = m["meta"]["intent_type"]
            self.intent_timings.append((start, duration, label))
            self.total_intents += 1
            k = f"{m['meta']['intent_type']}"
            if k not in self.intents:
                self.intents[k] = 0
            self.intents[k] += 1
        if m["metric_type"] == "fallback_handler":
            self.total_fallbacks += 1
            k = f"{m['meta']['handler']}"
            if m['meta'].get("skill_id"):
                k = f"{m['meta']['skill_id']}:{m['meta']['handler']}"
            if k not in self.fallbacks:
                self.fallbacks[k] = 0
            self.fallbacks[k] += 1
            label = k
            self.fallback_timings.append((start, duration, label))
        if m["metric_type"] == "stt":
            label = m["meta"]["transcription"]
            self.stt_timings.append((start, duration, label))
            self.total_stt += 1
            k = f"{m['meta']['stt']}"
            if k not in self.stt:
                self.stt[k] = 0
            self.stt[k] += 1
        if m["metric_type"] == "speech":
            label = m["meta"]["utterance"]
            self.tts_timings.append((start, duration, label))
            self.total_tts += 1
            k = f"{m['meta']['tts']}"
            if k not in self.tts:
                self.tts[k] = 0
            self.tts[k] += 1

        self.device_timings.append((start, duration, m["uuid"]))

        # sort by timestamp
        self.device_timings = sorted(self.device_timings, key=lambda k: k[0], reverse=True)
        self.stt_timings = sorted(self.stt_timings, key=lambda k: k[0], reverse=True)
        self.tts_timings = sorted(self.tts_timings, key=lambda k: k[0], reverse=True)
        self.intent_timings = sorted(self.intent_timings, key=lambda k: k[0], reverse=True)
        self.fallback_timings = sorted(self.fallback_timings, key=lambda k: k[0], reverse=True)


class DeviceMetricsReportGenerator(MetricsReportGenerator):
    def __init__(self, uuid):
        self.uuid = uuid
        super().__init__()

    def load_metrics(self):
        self.reset_metrics()

        self.total_ww = len([ww for ww in JsonWakeWordDatabase()
                             if ww["uuid"] == self.uuid])
        self.total_metrics = 0
        self.total_utt = len([utt for utt in JsonUtteranceDatabase()
                              if utt["uuid"] == self.uuid])

        for m in JsonMetricDatabase():
            if m["uuid"] != self.uuid:
                continue
            self._process_metric(m)
            self.total_metrics += 1
        for ww in JsonWakeWordDatabase():
            if ww["uuid"] != self.uuid:
                continue
            if ww["meta"]["name"] not in self.ww:
                self.ww[ww["meta"]["name"]] = 0
            else:
                self.ww[ww["meta"]["name"]] += 1


if __name__ == "__main__":
    for ww in JsonWakeWordDatabase():
        print(ww)
