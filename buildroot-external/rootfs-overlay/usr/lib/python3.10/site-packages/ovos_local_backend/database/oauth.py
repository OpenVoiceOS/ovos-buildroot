from json_database import JsonStorageXDG


class OAuthTokenDatabase(JsonStorageXDG):
    def __init__(self):
        super().__init__("ovos_oauth")

    def add_token(self, oauth_service, token_data):
        self[oauth_service] = token_data

    def total_tokens(self):
        return len(self)


class OAuthApplicationDatabase(JsonStorageXDG):
    def __init__(self):
        super().__init__("ovos_oauth_apps")

    def add_application(self, oauth_service,
                        client_id, client_secret,
                        auth_endpoint, token_endpoint, refresh_endpoint,
                        callback_endpoint, scope):
        self[oauth_service] = {"oauth_service": oauth_service,
                               "client_id": client_id,
                               "client_secret": client_secret,
                               "auth_endpoint": auth_endpoint,
                               "token_endpoint": token_endpoint,
                               "refresh_endpoint": refresh_endpoint,
                               "callback_endpoint": callback_endpoint,
                               "scope": scope}

    def total_apps(self):
        return len(self)
