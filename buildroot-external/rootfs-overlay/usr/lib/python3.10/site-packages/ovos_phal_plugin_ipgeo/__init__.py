import requests
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.configuration import get_webcache_location, LocalConf
from ovos_utils.messagebus import Message


class IPGeoPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus, "ovos-phal-plugin-ipgeo", config)
        self.location = {}
        self.web_config = LocalConf(get_webcache_location())
        self.bus.on("mycroft.internet.connected", self.on_reset)
        self.on_reset()  # get initial location data

    def on_reset(self, message=None):
        # we update the remote config to allow
        # both backend and user config to take precedence
        # over ip geolocation
        if self.web_config.get("location"):
            return
        # geolocate from ip address
        try:
            self.location = self.ip_geolocate()
            self.web_config["location"] = self.location
            self.web_config.store()
            self.bus.emit(Message("configuration.updated"))
        except:
            pass

    @staticmethod
    def ip_geolocate(ip=None):
        if not ip or ip in ["0.0.0.0", "127.0.0.1"]:
            ip = requests.get('https://api.ipify.org').text
        fields = "status,country,countryCode,region,regionName,city,lat,lon,timezone,query"
        data = requests.get("http://ip-api.com/json/" + ip,
                            params={"fields": fields}).json()
        region_data = {"code": data["region"],
                       "name": data["regionName"],
                       "country": {
                           "code": data["countryCode"],
                           "name": data["country"]}}
        city_data = {"code": data["city"],
                     "name": data["city"],
                     "state": region_data}
        timezone_data = {"code": data["timezone"],
                         "name": data["timezone"]}
        coordinate_data = {"latitude": float(data["lat"]),
                           "longitude": float(data["lon"])}
        return {"city": city_data,
                "coordinate": coordinate_data,
                "timezone": timezone_data}


