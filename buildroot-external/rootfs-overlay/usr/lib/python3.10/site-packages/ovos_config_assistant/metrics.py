import json
import os

from cutecharts.charts import Pie, Bar, Scatter
from json_database import JsonDatabaseXDG
from ovos_config import Configuration
from pywebio.input import actions
from pywebio.output import put_text, popup, put_code, put_markdown, put_html, use_scope, put_image

chart_type = Pie


def metrics_select(back_handler=None):
    buttons = []
    db = JsonDatabaseXDG("ovos_metrics")
    if not len(db):
        with use_scope("main_view", clear=True):
            put_text("No metrics uploaded yet!")
        metrics_menu(back_handler=back_handler)
        return

    for m in db:
        name = f"{m['metric_id']}-{m['metric_type']}"
        buttons.append({'label': name, 'value': m['metric_id']})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
    opt = actions(label="Select a metric to inspect",
                  buttons=buttons)
    if opt == "main":
        if back_handler:
            back_handler()
        return
    # id == db_position + 1
    with use_scope("main_view", clear=True):
        put_markdown("# Metadata")
        put_code(json.dumps(db[opt - 1], indent=4), "json")
    metrics_select(back_handler=back_handler)


def _plot_metrics(selected_metric="types"):
    m = MetricsReportGenerator()

    with use_scope("main_view", clear=True):
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
            md = f"""# Open Dataset Report
            Currently Opted-in: {Configuration().get('opt_in', False)}

            Total Metrics collected: {m.total_metrics}
            Total WakeWords collected: {m.total_ww}
            Total Utterances collected: {m.total_utt}"""

            put_markdown(md)
            if chart_type == Pie:
                put_html(m.dataset_pie_chart().render_notebook())
            else:
                put_html(m.dataset_bar_chart().render_notebook())


def metrics_menu(back_handler=None, selected_metric="types"):
    global chart_type

    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/metrics.png', 'rb').read()
        put_image(img)

    _plot_metrics(selected_metric)

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
    buttons.append({'label': 'Delete metrics database', 'value': "delete_metrics"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)

    if opt == "chart":
        if chart_type == Pie:
            chart_type = Bar
        else:
            chart_type = Pie
    elif opt in ["intents", "stt", "ww", "tts", "types", "fallback", "opt-in", "timings"]:
        selected_metric = opt
    elif opt == "delete_metrics":
        with popup("Are you sure you want to delete the metrics database?"):
            put_text("this can not be undone, proceed with caution!")
            put_text("ALL metrics will be lost")
        opt = actions(label="Delete metrics database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            os.remove(JsonDatabaseXDG("ovos_metrics").db.path)
            with use_scope("main_view", clear=True):
                if back_handler:
                    back_handler()
        else:
            metrics_menu(back_handler=back_handler,
                         selected_metric=selected_metric)
        return
    elif opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    metrics_menu(back_handler=back_handler,
                 selected_metric=selected_metric)


class MetricsReportGenerator:
    def __init__(self):
        self.total_intents = 0
        self.total_fallbacks = 0
        self.total_stt = 0
        self.total_tts = 0
        self.total_ww = len(JsonDatabaseXDG("ovos_wakewords"))
        self.total_utt = len(JsonDatabaseXDG("ovos_utterances"))
        self.total_metrics = len(JsonDatabaseXDG("ovos_metrics"))

        self.intents = {}
        self.fallbacks = {}
        self.ww = {}
        self.tts = {}
        self.stt = {}

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
        self.total_ww = len(JsonDatabaseXDG("ovos_wakewords"))
        self.total_metrics = len(JsonDatabaseXDG("ovos_metrics"))
        self.total_utt = len(JsonDatabaseXDG("ovos_utterances"))

        self.intents = {}
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
        for m in JsonDatabaseXDG("ovos_metrics"):
            self._process_metric(m)
        for ww in JsonDatabaseXDG("ovos_wakewords"):
            if ww["meta"]["name"] not in self.ww:
                self.ww[ww["meta"]["name"]] = 0
            else:
                self.ww[ww["meta"]["name"]] += 1

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
        start = m["meta"].get("start_time") or -1
        end = m["meta"].get("time") or -1
        duration = end - start
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

        self.total_ww = len([ww for ww in JsonDatabaseXDG("ovos_wakewords")
                             if ww["uuid"] == self.uuid])
        self.total_metrics = 0
        self.total_utt = len([utt for utt in JsonDatabaseXDG("ovos_utterances")
                              if utt["uuid"] == self.uuid])

        for m in JsonDatabaseXDG("ovos_metrics"):
            if m["uuid"] != self.uuid:
                continue
            self._process_metric(m)
            self.total_metrics += 1
        for ww in JsonDatabaseXDG("ovos_wakewords"):
            if ww["uuid"] != self.uuid:
                continue
            if ww["meta"]["name"] not in self.ww:
                self.ww[ww["meta"]["name"]] = 0
            else:
                self.ww[ww["meta"]["name"]] += 1


if __name__ == "__main__":
    for ww in JsonDatabaseXDG("ovos_wakewords"):
        print(ww)
