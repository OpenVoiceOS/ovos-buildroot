from json_database import JsonDatabaseXDG
from ovos_local_backend.backend.decorators import requires_opt_in
import json


@requires_opt_in
def save_metric(uuid, name, data):
    with JsonMetricDatabase() as db:
        db.add_metric(name, data, uuid)


class Metric:
    def __init__(self, metric_id, metric_type, meta=None, uuid="AnonDevice"):
        if isinstance(meta, str):
            meta = json.loads(meta)
        self.metric_id = metric_id
        self.metric_type = metric_type
        self.meta = meta or {}
        self.uuid = uuid


class JsonMetricDatabase(JsonDatabaseXDG):
    def __init__(self):
        super().__init__("ovos_metrics")

    def add_metric(self, metric_type=None, meta=None, uuid="AnonDevice"):
        metric_id = self.total_metrics() + 1
        metric = Metric(metric_id, metric_type, meta, uuid)
        self.add_item(metric)

    def total_metrics(self):
        return len(self)

    def __enter__(self):
        """ Context handler """
        return self

    def __exit__(self, _type, value, traceback):
        """ Commits changes and Closes the session """
        try:
            self.commit()
        except Exception as e:
            print(e)

