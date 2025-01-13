import os

class KeycloakConfig:
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "https://default-keycloak-url.com")
        self.realm = os.getenv("KEYCLOAK_REALM", "default-realm")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "default-client-id")
        self.username = os.getenv("KEYCLOAK_USERNAME", None)
        self.password = os.getenv("KEYCLOAK_PASSWORD", None)

    def update(self, keycloak_url=None, realm=None, client_id=None, username=None, password=None):
        if keycloak_url:
            self.keycloak_url = keycloak_url
        if realm:
            self.realm = realm
        if client_id:
            self.client_id = client_id
        if username:
            self.username = username
        if password:
            self.password = password


# Global configuration object
keycloak_config = KeycloakConfig()

def set_keycloak_config(keycloak_url=None, realm=None, client_id=None, username=None, password=None):
    keycloak_config.update(keycloak_url, realm, client_id, username, password)
