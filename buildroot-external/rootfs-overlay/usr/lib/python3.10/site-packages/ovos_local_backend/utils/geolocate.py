import enum

import geocoder
from flask import request
from timezonefinder import TimezoneFinder

from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.session import SESSION as requests
from ovos_backend_client.api import GeolocationApi


def get_timezone(latitude, longitude):
    tf = TimezoneFinder()
    return tf.timezone_at(lng=longitude, lat=latitude)


def get_request_location():
    if not request.headers.getlist("X-Forwarded-For"):
        ip = request.remote_addr
    else:
        # TODO http://esd.io/blog/flask-apps-heroku-real-ip-spoofing.html
        ip = request.headers.getlist("X-Forwarded-For")[0]
    if CONFIGURATION["override_location"]:
        new_location = CONFIGURATION["default_location"]
    elif CONFIGURATION["geolocate"]:
        new_location = ip_geolocate(ip)
    else:
        new_location = {}
    return new_location


def ip_geolocate(ip=None):
    if not ip or ip in ["0.0.0.0", "127.0.0.1"]:
        ip = requests.get('https://api.ipify.org').text
    fields = "status,country,countryCode,region,regionName,city,lat,lon,timezone,query"
    data = requests.get("http://ip-api.com/json/" + ip,
                        params={"fields": fields}).json()
    region_data = {"code": data.get("region"), "name": data.get("regionName"),
                   "country": {
                       "code": data.get("countryCode"),
                       "name": data.get("country")}}
    city_data = {"code": data.get("city"), "name": data.get("city"),
                 "state": region_data,
                 "region": region_data}
    if "timezone" in data:
        timezone_data = {"code": data["timezone"],
                         "name": data["timezone"]}
    else:
        timezone_data = {}
    if "lat" in data and "lon" in data:
        coordinate_data = {"latitude": float(data["lat"]),
                           "longitude": float(data["lon"])}
    else:
        coordinate_data = {}
    return {"city": city_data,
            "coordinate": coordinate_data,
            "timezone": timezone_data}


class GeocoderProviders(str, enum.Enum):
    AUTO = "auto"
    SELENE = "selene"
    OSM = "osm"
    ARCGIS = "arcgis"
    GEOCODE_FARM = "geocode_farm"
    # NOTE - most providers in geopy are non functional
    # the lib seems abandoned, TODO migrate to geopy instead


class Geocoder:
    def __init__(self, provider=None):
        self.provider = provider or \
                        CONFIGURATION["microservices"].get("geolocation_provider") or \
                        GeocoderProviders.AUTO

    @property
    def engine(self):
        if self.provider == GeocoderProviders.OSM or \
                self.provider == GeocoderProviders.AUTO:
            return geocoder.osm
        elif self.provider == GeocoderProviders.ARCGIS:
            return geocoder.arcgis
        elif self.provider == GeocoderProviders.GEOCODE_FARM:
            return geocoder.geocodefarm
        elif self.provider == GeocoderProviders.SELENE:
            cfg = CONFIGURATION["selene"]
            if not cfg["enabled"] or not cfg.get("proxy_geolocation"):
                raise ValueError("Selene selected for geolocation, but it is disabled in config!")
            _url = cfg.get("url")
            _version = cfg.get("version") or "v1"
            _identity_file = cfg.get("identity_file")
            return GeolocationApi(_url, _version, _identity_file).get_geolocation

        raise ValueError(f"Unknown geolocation provider: {self.provider}")

    def _geolocate(self, address):
        data = {}
        error = ""
        location_data = self.engine(address)
        if location_data.ok:
            location_data = location_data.json
            if location_data["raw"].get("error"):
                error = location_data["raw"]["error"]
            elif location_data.get("accuracy") == "Unmatchable":
                error = "No results found"

            data["raw"] = location_data
            data["country"] = location_data.get("country")
            data["country_code"] = location_data.get("country_code")
            data["region"] = location_data.get("region")
            data["address"] = location_data.get("address")
            data["state"] = location_data.get("state")
            data["confidence"] = location_data.get("confidence")
            data["lat"] = location_data.get("lat")
            data["lon"] = location_data.get("lng")
            data["city"] = location_data.get("city") or location_data.get("address")

            data["postal"] = location_data.get("postal")
            data["timezone"] = location_data.get("timezone_short")
        if not data:
            error = "No results found"
        if error:
            raise RuntimeError(error)
        return data

    def get_location(self, address):

        if self.provider == GeocoderProviders.SELENE:
            return self.engine(address)  # selene proxy, special handling

        location = {
            "city": {
                "code": "",
                "name": "",
                "state": {
                    "code": "",
                    "name": "",
                    "country": {
                        "code": "US",
                        "name": "United States"
                    }
                }
            },
            "coordinate": {
                "latitude": 37.2,
                "longitude": 121.53
            },
            "timezone": {
                "dstOffset": 3600000,
                "offset": -21600000
            }
        }

        data = self._geolocate(address)
        location["city"]["code"] = data["city"]
        location["city"]["name"] = data["city"]
        location["city"]["state"]["name"] = data["state"]
        # TODO state code
        location["city"]["state"]["code"] = data["state"]
        location["city"]["state"]["country"]["name"] = data["country"]
        # TODO country code
        location["city"]["state"]["country"]["code"] = data["country"]
        location["coordinate"]["latitude"] = data["lat"]
        location["coordinate"]["longitude"] = data["lon"]

        timezone = get_timezone(data["lat"], data["lon"])
        location["timezone"]["name"] = data["timezone"]
        location["timezone"]["code"] = timezone

        return location


def geolocate(address):
    """ Deprecated! use Geocoder().get_location(address) instead"""
    return Geocoder()._geolocate(address)


def get_location_config(address):
    """ Deprecated! use Geocoder().get_location(address) instead"""
    return Geocoder().get_location(address)


if __name__ == "__main__":
    g = Geocoder(GeocoderProviders.OSM)
    print(g.get_location("Lisboa"))

    g = Geocoder(GeocoderProviders.ARCGIS)
    print(g.get_location("Moscow"))

    g = Geocoder(GeocoderProviders.GEOCODE_FARM)
    print(g.get_location("Berlin"))
