import logging
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)

from fastapi import Request
from jwcrypto import jwk
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakOpenID
from redis.asyncio import Redis

from streamxx_common.auth.exceptions import (
    AuthenticationError,
    InsufficientPermissionsError,
    KeycloakError,
    MissingTokenError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


class KeycloakTokenValidator:
    def __init__(
        self,
        keycloak_url: str,
        realm_name: str,
        client_id: str,
        client_secret: str,
        kc_public_key_cache_ttl: int,
        redis_url: str,
    ):
        """
        Keycloak token validator initialization.

        :param keycloak_url:
        :param realm_name:
        :param client_id:
        :param client_secret:
        :param redis_url:
        :param kc_public_key_cache_ttl: keycloak public key time to live in seconds
        """
        self.keycloak_url = keycloak_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.kc_public_key_cache_ttl = kc_public_key_cache_ttl

        self.keycloak_client = KeycloakOpenID(
            server_url=self.keycloak_url,
            client_id=self.client_id,
            realm_name=self.realm_name,
            client_secret_key=self.client_secret,
        )

        self._redis_url = redis_url
        self._redis_client: Optional[Redis] = None

        # redis keys
        self._public_key_cache_key = f'keycloak:public_key:{self.realm_name}'

    async def get_redis_client(self) -> Redis:
        """Get or create redis client."""
        if self._redis_client is None:
            self._redis_client = Redis.from_url(self._redis_url)
        return self._redis_client

    async def _get_cached_public_key(self) -> Optional[str]:
        """Get public key from cache."""
        redis_client = await self.get_redis_client()
        cached_key = await redis_client.get(self._public_key_cache_key)
        return cached_key.decode('utf-8') if cached_key else None

    async def _set_cached_public_key(self, public_key: str):
        """Save public key to cache."""
        redis_client = await self.get_redis_client()
        await redis_client.setex(
            self._public_key_cache_key,
            self.kc_public_key_cache_ttl,
            public_key,
        )

    async def get_public_key(self) -> str:
        """Get public key from redis or from keycloak"""
        cached_key = await self._get_cached_public_key()
        if cached_key:
            return cached_key

        try:
            # get new keycloak public key
            public_key = self.keycloak_client.public_key()
            # save public key to cache
            await self._set_cached_public_key(public_key)
            return public_key
        except Exception as e:
            raise KeycloakError(f'Failed to get public key from Keycloak: {str(e)}')

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token

        :param token: JWT token to verify
        :return: Decoded token data
        :raises AuthenticationError: if token is invalid
        """
        try:
            public_key = await self.get_public_key()
            try:
                public_key = jwk.JWK.from_pem(public_key.encode('utf-8'))
            except ValueError as e:
                logger.error(f'Keycloak public key error {str(e)}')
                raise AuthenticationError()
            kwargs = {'key': public_key, 'algs': ['RS256']}
            # Use python-keycloak's built-in token validation
            token_info = self.keycloak_client.decode_token(
                token,
                validate=True,
                **kwargs,
            )
            return token_info
        except JWTExpired:
            raise TokenExpiredError()
        except Exception as e:
            logger.error(f'Auth token error: {str(e)}')
            raise AuthenticationError()

    def require_token(self, roles: Optional[list[str]] = None) -> Callable:
        """
        FastAPI endpoint decorator

        :param roles: List of required roles (optional)
        :return: Decorator
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    raise MissingTokenError()

                token = auth_header.split(' ')[1]
                token_data = await self.verify_token(token)

                if roles:
                    token_roles = token_data.get('realm_access', {}).get('roles', [])
                    if not any(role in token_roles for role in roles):
                        raise InsufficientPermissionsError()

                # Add token data to request state for use in endpoint
                request.state.token_data = token_data
                return await func(request, *args, **kwargs)

            return wrapper

        return decorator
