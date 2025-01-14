from functools import wraps
from fastapi import HTTPException, Request
from .auth import KeycloakAuth
from .config import keycloak_config

def get_keycloak_token(func):
    """Decorator to fetch Keycloak token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not keycloak_config.username or not keycloak_config.password:
            raise HTTPException(status_code=400, detail="Keycloak username or password not configured.")
        token = KeycloakAuth(keycloak_config)
        token = token.get_keycloak_token()
        return func(token=token,*args, **kwargs)
    return wrapper


def verify_roles(required_roles):
    """Decorator to verify JWT token and required roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authorization token is missing.")

            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid Authorization header format. Expected 'Bearer <token>'.")

            token = auth_header.split(" ")[1]

            decoded_token = KeycloakAuth(keycloak_config).verify_token(token, required_roles)

            # Pass the decoded token to the decorated function
            return await func(request,*args,**kwargs)
        return wrapper
    return decorator
