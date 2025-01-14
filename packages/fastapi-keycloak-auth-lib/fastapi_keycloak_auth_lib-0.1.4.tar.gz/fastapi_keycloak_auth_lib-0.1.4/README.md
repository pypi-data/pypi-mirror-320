# fastapi-keycloak-auth

`fastapi-keycloak-auth` is a Python package that provides an easy integration of Keycloak authentication and role-based authorization into FastAPI applications. The package supports JWT token validation, role checks, and automatic token retrieval, making it simple to implement secure API access.

## Features:
- **Keycloak Integration**: Authenticate and retrieve JWT tokens from Keycloak using the `password` grant type.
- **Token Verification**: Easily verify the JWT token with Keycloak's public key.
- **Role-based Access Control**: Enforce role-based access with custom decorators.
- **Flexible Configuration**: Easily configure Keycloak settings (URL, realm, client ID, username, and password) via environment variables or direct updates.

## Installation:

You can install the package via pip:

```bash
pip install fastapi-keycloak-auth
