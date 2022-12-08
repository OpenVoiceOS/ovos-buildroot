from ovos_config.config import Configuration

from ovos_backend_client.backends.personal import PersonalBackend, BackendType

SELENE_API_URL = "https://api.mycroft.ai"
SELENE_PRECISE_URL = "https://training.mycroft.ai/precise/upload"


class SeleneBackend(PersonalBackend):

    def __init__(self, url=SELENE_API_URL, version="v1", identity_file=None, credentials=None):
        super().__init__(url, version, identity_file, credentials)
        self.backend_type = BackendType.SELENE

    # Device API
    def device_upload_wake_word_v1(self, audio, params, upload_url=None):
        """ upload precise wake word V1 endpoint - url can be external to backend"""
        # ensure default value for selene backend
        if not upload_url:
            config = Configuration().get("listener", {}).get("wake_word_upload", {})
            upload_url = config.get("url") or SELENE_PRECISE_URL
        return super().device_upload_wake_word_v1(audio, params, upload_url)

    # Admin API - NOT available, use home.mycroft.ai instead
    def admin_pair(self, uuid=None):
        raise RuntimeError(f"AdminAPI not available for {self.backend_type}")

    def admin_set_device_location(self, uuid, loc):
        raise RuntimeError(f"AdminAPI not available for {self.backend_type}")

    def admin_set_device_prefs(self, uuid, prefs):
        raise RuntimeError(f"AdminAPI not available for {self.backend_type}")

    def admin_set_device_info(self, uuid, info):
        raise RuntimeError(f"AdminAPI not available for {self.backend_type}")
