from flask import request

from ovos_local_backend.backend import API_VERSION
from ovos_local_backend.backend.decorators import noindex, requires_auth, check_selene_pairing
from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.utils import dict_to_camel_case, ExternalApiManager


def _get_lang():
    auth = request.headers.get('Authorization', '').replace("Bearer ", "")
    uid = auth.split(":")[-1]  # this split is only valid here, not selene
    device = DeviceDatabase().get_device(uid)
    if device:
        return device.lang
    return CONFIGURATION.get("lang", "en-us")


def _get_units():
    auth = request.headers.get('Authorization', '').replace("Bearer ", "")
    uid = auth.split(":")[-1]  # this split is only valid here, not selene
    device = DeviceDatabase().get_device(uid)
    if device:
        return device.system_unit
    return CONFIGURATION.get("system_unit", "metric")


def _get_latlon():
    auth = request.headers.get('Authorization', '').replace("Bearer ", "")
    uid = auth.split(":")[-1]  # this split is only valid here, not selene
    device = DeviceDatabase().get_device(uid)
    if device:
        loc = device.location
    else:
        loc = CONFIGURATION["default_location"]
    lat = loc["coordinate"]["latitude"]
    lon = loc["coordinate"]["longitude"]
    return lat, lon


def get_services_routes(app):

    apis = ExternalApiManager()
    @app.route("/" + API_VERSION + '/geolocation', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def geolocation():
        address = request.args["location"]
        return apis.geolocate(address)

    @app.route("/" + API_VERSION + '/wolframAlphaSpoken', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def wolfie_spoken():
        query = request.args.get("input") or request.args.get("i")
        units = request.args.get("units") or _get_units()
        return apis.wolfram_spoken(query, units)

    @app.route("/" + API_VERSION + '/wolframAlphaSimple', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def wolfie_simple():
        query = request.args.get("input") or request.args.get("i")
        units = request.args.get("units") or _get_units()
        return apis.wolfram_simple(query, units)

    @app.route("/" + API_VERSION + '/wolframAlphaFull', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def wolfie_full():
        query = request.args.get("input") or request.args.get("i")
        units = request.args.get("units") or _get_units()
        return apis.wolfram_full(query, units)

    @app.route("/" + API_VERSION + '/wa', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def wolfie_xml():
        """ old deprecated endpoint with XML results """
        query = request.args["i"]
        units = request.args.get("units") or _get_units()
        return apis.wolfram_xml(query, units)

    @app.route("/" + API_VERSION + '/owm/forecast/daily', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def owm_daily_forecast():
        lang = request.args.get("lang") or _get_lang()
        units = request.args.get("units") or _get_units()
        lat, lon = request.args.get("lat"), request.args.get("lon")
        if not lat or not lon:
            lat, lon = _get_latlon()
        return apis.owm_daily(lat, lon, units, lang)

    @app.route("/" + API_VERSION + '/owm/forecast', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def owm_3h_forecast():
        lang = request.args.get("lang") or _get_lang()
        units = request.args.get("units") or _get_units()
        lat, lon = request.args.get("lat"), request.args.get("lon")
        if not lat or not lon:
            lat, lon = _get_latlon()
        return apis.owm_hourly(lat, lon, units, lang)

    @app.route("/" + API_VERSION + '/owm/weather', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def owm():
        lang = request.args.get("lang") or _get_lang()
        units = request.args.get("units") or _get_units()
        lat, lon = request.args.get("lat"), request.args.get("lon")
        if not lat or not lon:
            lat, lon = _get_latlon()
        return apis.owm_current(lat, lon, units, lang)

    @app.route("/" + API_VERSION + '/owm/onecall', methods=['GET'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def owm_onecall():
        units = request.args.get("units") or _get_units()
        lang = request.args.get("lang") or _get_lang()
        lat, lon = request.args.get("lat"), request.args.get("lon")
        if not lat or not lon:
            lat, lon = _get_latlon()
        data = apis.owm_onecall(lat, lon, units, lang)
        # Selene converts the keys from snake_case to camelCase
        return dict_to_camel_case(data)

    return app
