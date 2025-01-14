from functools import wraps
from fastapi import HTTPException, Request
from .auth import KeycloakAuth
from .config import keycloak_config
from functools import wraps
from fastapi import Request, HTTPException

def get_keycloak_token(func):
    """Decorator to fetch Keycloak token based on request."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Await the request.json() to get the body as a dictionary
        body = await request.json()
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Username or password not provided in the request body."
            )

        # Fetch the Keycloak token
        token = KeycloakAuth(username=username, password=password).get_keycloak_token()

        # Pass the token to the original function
        return await func(request=request, *args, token=token, **kwargs)

    return wrapper



def verify_roles(required_roles):
    """Decorator to verify JWT token and required roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authorization token is missing.")

            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid Authorization header format. Expected 'Bearer <token>'.")

            token = auth_header.split(" ")[1]

            decoded_token = KeycloakAuth(keycloak_config).verify_token(token, required_roles)
            kwargs['decoded_token'] = decoded_token
            # Pass the decoded token to the decorated function
            return func(request,*args,**kwargs)
        return wrapper
    return decorator
