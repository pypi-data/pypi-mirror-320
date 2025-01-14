import requests
from fastapi import HTTPException
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from authlib.jose import jwt, JoseError
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class KeycloakAuth:
    def __init__(self, config):
        self.config = config

    def get_keycloak_public_key(self):
        """Retrieve and decode the public key from Keycloak."""
        certs_url = f"{self.config.keycloak_url}/realms/{self.config.realm}/protocol/openid-connect/certs"
        response = requests.get(certs_url)
        if response.status_code != 200:
            logging.error("Failed to fetch public key from Keycloak.")
            raise HTTPException(status_code=500, detail="Failed to fetch public key from Keycloak")

        certs = response.json()
        x5c = certs["keys"][0]["x5c"][0]
        der_cert = base64.b64decode(x5c)
        cert = load_der_x509_certificate(der_cert, default_backend())

        public_key = cert.public_key()
        if not isinstance(public_key, RSAPublicKey):
            logging.error("Unsupported key type fetched from Keycloak.")
            raise HTTPException(status_code=500, detail="Unsupported key type")
        return public_key

    def get_keycloak_token(self):
        """Authenticate with Keycloak and retrieve a token."""
        token_url = f"{self.config.keycloak_url}/realms/{self.config.realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": self.config.client_id,
            "username": self.config.username,
            "password": self.config.password,
        }
        print(data, token_url)
        
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            logging.error("Failed to authenticate with Keycloak.")
            raise HTTPException(status_code=401, detail="Failed to authenticate with Keycloak")
        return response.json()

    def verify_token(self, token: str, required_roles: list):
        """Verify the JWT token and validate required roles."""
        public_key = self.get_keycloak_public_key()
        try:
            claims = jwt.decode(token, public_key)
            claims.validate()

            realm_roles = claims.get("realm_access", {}).get("roles", [])
            client_roles = claims.get("resource_access", {}).get(self.config.client_id, {}).get("roles", [])
            missing_roles = [role for role in required_roles if role not in realm_roles and role not in client_roles]
            if missing_roles:
                raise HTTPException(status_code=403, detail=f"Missing required roles: {', '.join(missing_roles)}")
            return claims
        except JoseError as e:
            logging.error(f"Token validation error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token signature")
