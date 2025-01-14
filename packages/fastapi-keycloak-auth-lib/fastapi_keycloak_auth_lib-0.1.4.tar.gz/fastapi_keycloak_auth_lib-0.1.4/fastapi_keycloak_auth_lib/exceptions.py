from fastapi import HTTPException

class KeycloakError(HTTPException):
    """Custom exception for Keycloak-related errors."""
    pass
