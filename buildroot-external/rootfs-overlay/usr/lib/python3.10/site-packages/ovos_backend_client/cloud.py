import base64
import json

from ovos_utils.security import encrypt, decrypt

from ovos_backend_client.api import DeviceApi


class SeleneCloud:
    def __init__(self, db_id="SeleneCloud", url=None, version="v1"):
        self.api = DeviceApi(url, version)
        self.db_id = db_id

    def add_entry(self, data_id, data):
        if not isinstance(data, str):
            data = json.dumps(data)
        display_name = f"{self.db_id}|{data_id}"
        meta = {
            "skill_gid": f"{data_id}|{self.db_id}",
            "display_name": display_name,
            "skillMetadata": {
                "sections": [
                    {
                        "name": display_name,
                        "fields": [
                            {"type": "label",
                             "label": "This is encoded data, DO NOT EDIT in browser"},
                            {"type": "checkbox",  # special flag for local backend
                             "name": "__shared_settings",  # not tied to devices
                             "value": "true"},
                            {"type": "text",
                             "name": "encoded_data",
                             "value": data}
                        ]
                    }
                ]
            }
        }

        return self.api.put_skill_settings_v1(meta)

    def get_entry(self, data_id):
        data_id = f"{data_id}|{self.db_id}"
        settings = self.api.get_skill_settings_v1()
        data = None
        for s in settings:
            if s['skill_gid'] == data_id:
                sections = s['skillMetadata']['sections']
                data = sections[0]["fields"][-1]["value"]
                break
        return data


class SecretSeleneCloud(SeleneCloud):
    def __init__(self, key, db_id="SecretSeleneCloud", url=None, version="v1"):
        self.key = key
        super().__init__(db_id, url, version)

    def add_entry(self, data_id, data):
        if not isinstance(data, str):
            data = json.dumps(data)

        ciphertext, tag, nonce = encrypt(self.key, data)
        # b64 strings for storage
        tag = base64.encodebytes(tag).decode("utf-8")
        nonce = base64.encodebytes(nonce).decode("utf-8")
        ciphertext = base64.encodebytes(ciphertext).decode("utf-8")

        data = {"tag": tag, "nonce": nonce, "ciphertext": ciphertext}
        return super().add_entry(data_id, data)

    def get_entry(self, data_id):
        data = super().get_entry(data_id)
        if data:
            data = json.loads(data)
            ciphertext = data["ciphertext"].encode("utf-8")
            tag = data["tag"].encode("utf-8")
            nonce = data["nonce"].encode("utf-8")

            ciphertext = base64.decodebytes(ciphertext)
            tag = base64.decodebytes(tag)
            nonce = base64.decodebytes(nonce)

            return decrypt(self.key, ciphertext, tag, nonce)


if __name__ == "__main__":
    cloud = SeleneCloud(url="http://0.0.0.0:6712")
    cloud.add_entry("test3", {"secret": "NOT ENCRYPTED MAN"})
    print(cloud.get_entry("test3"))

    k = "D8fmXEP5VqzVw2HE"
    cloud = SecretSeleneCloud(k, url="http://0.0.0.0:6712")
    cloud.add_entry("test7", {"secret": "secret data"})
    print(cloud.get_entry("test7"))
