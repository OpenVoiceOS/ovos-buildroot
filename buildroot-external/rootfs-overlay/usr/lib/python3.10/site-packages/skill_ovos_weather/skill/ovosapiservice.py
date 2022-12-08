import json
import requests
from json_database import JsonStorageXDG
from ovos_utils import ovos_service_api


class OvosService:

    def __init__(self) -> None:
        self.ovos_api = ovos_service_api.OVOSApiService()
        self.ovos_api.register_device()

    def get_report_for_weather_onecall_type(self, query: dict):
        self.ovos_api.get_session_challenge()
        headers = {'session_challenge': self.ovos_api.get_session_token(), 'backend': 'OWM'}
        reqdata = {"lat": query.get("lat"), "lon": query.get("lon"), "units": query.get("units"), "lang": query.get("lang")}
        onecall_weather_request = requests.post('https://api.openvoiceos.com/weather/onecall_weather_report/' + self.ovos_api.get_uuid(), data=reqdata, headers=headers)
        onecall_weather_response = onecall_weather_request.text
        return json.loads(onecall_weather_response)
