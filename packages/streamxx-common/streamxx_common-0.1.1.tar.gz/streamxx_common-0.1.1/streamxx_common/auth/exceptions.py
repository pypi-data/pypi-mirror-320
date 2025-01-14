from http import HTTPStatus

from fastapi import HTTPException


class AuthenticationError(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=detail or 'Authentication error occurred',
        )


class TokenExpiredError(AuthenticationError):
    def __init__(self, detail: str | None = None):
        super().__init__(detail or 'Token has expired')


class InvalidTokenError(AuthenticationError):
    def __init__(self, detail: str | None = None):
        super().__init__(detail or 'Invalid token')


class MissingTokenError(AuthenticationError):
    def __init__(self, detail: str | None = None):
        super().__init__(detail or 'Missing authorization token')


class InsufficientPermissionsError(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail=detail or 'Insufficient permissions',
        )


class KeycloakError(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail)
