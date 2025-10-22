"""
Runtime environment helpers backed by PostgreSQL + Redis.

Stores configuration values that must be editable at runtime and provides
helper accessors that fall back to .env definitions when missing.
"""
from __future__ import annotations

import logging
from contextlib import suppress
from typing import Any, Callable, Optional, TypeVar

from app.core.env import settings
from app.db.postgre_db import PostgreDB
from app.schemas.env_schema import EnvVariableCreate, EnvVariableUpdate
from app.services.env_services.env_cache import EnvCacheService
from app.services.env_services.env_variable import EnvVariableService

_logger = logging.getLogger(__name__)

T = TypeVar("T")

_DEFAULT_DESCRIPTIONS: dict[str, str] = {
    "CORS_ORIGINS": "Comma separated list of origins allowed for CORS",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "Access token expiration (minutes)",
}

_sync_ran = False


def _managed_default_map() -> dict[str, tuple[str, Optional[str]]]:
    """
    Build a mapping of managed environment keys to their default values.
    """
    managed: dict[str, tuple[str, Optional[str]]] = {}

    for key in settings.RUNTIME_ENV_KEYS_LIST:
        if not key:
            continue

        if hasattr(settings, key):
            value: Any = getattr(settings, key)
        else:
            value = None

        if value is None:
            continue

        managed[key] = (str(value), _DEFAULT_DESCRIPTIONS.get(key))

    return managed


def ensure_core_env_synced(force: bool = False) -> None:
    """
    Persist managed settings to PostgreSQL and refresh Redis cache.

    Called during application startup; safe to call multiple times.
    """
    global _sync_ran

    if _sync_ran and not force:
        return

    with suppress(Exception):
        PostgreDB.init_db()

    session = None
    try:
        session = PostgreDB.get_session()
        service = EnvVariableService(session)

        managed_defaults = _managed_default_map()

        for key, (value, description) in managed_defaults.items():
            try:
                existing = service.get(key)
                if not existing:
                    service.create(
                        EnvVariableCreate(
                            key=key, value=value, description=description
                        )
                    )
                    continue

                if description and existing.description != description:
                    service.update(
                        key,
                        EnvVariableUpdate(description=description),
                    )
            except Exception as exc:  # pragma: no cover - defensive
                session.rollback()
                _logger.warning(
                    "Failed to sync environment variable '%s': %s", key, exc
                )

        if not service.sync_to_redis():  # pragma: no cover - defensive
            _logger.warning("Failed to sync managed environment variables to Redis")

        _sync_ran = True
    except Exception as exc:  # pragma: no cover - defensive
        _logger.error("Failed to ensure core environment sync: %s", exc, exc_info=True)
    finally:
        if session is not None:
            session.close()


def _with_cache(callback: Callable[[EnvCacheService], Optional[str]]) -> Optional[str]:
    """
    Helper that instantiates the cache safely; returns None on failure.
    """
    try:
        cache = EnvCacheService()
        return callback(cache)
    except Exception:  # pragma: no cover - Redis connection issues
        return None


def _fetch_value(key: str) -> Optional[str]:
    """
    Retrieve a stored value from Redis, falling back to PostgreSQL.
    """
    cached_value = _with_cache(lambda cache: cache.get(key))
    if cached_value is not None:
        return cached_value

    session = None
    try:
        session = PostgreDB.get_session()
        service = EnvVariableService(session)
        env_var = service.get(key)
        if env_var:
            return env_var.value
        return None
    except Exception:  # pragma: no cover - defensive
        return None
    finally:
        if session is not None:
            session.close()


def get_env_value(
    key: str,
    *,
    default: Optional[T] = None,
    cast: Optional[Callable[[str], T]] = None,
) -> Optional[T]:
    """
    Fetch a managed environment value with optional casting.
    """
    ensure_core_env_synced()

    fallback: Optional[Any] = (
        default if default is not None else getattr(settings, key, None)
    )

    raw_value: Optional[Any] = _fetch_value(key)
    if raw_value is None:
        raw_value = fallback

    if raw_value is None:
        return None

    if cast is None:
        return raw_value  # type: ignore[return-value]

    try:
        return cast(str(raw_value))
    except (TypeError, ValueError):  # pragma: no cover - defensive
        _logger.warning(
            "Failed to cast environment variable '%s' with value '%s'",
            key,
            raw_value,
        )
        if fallback is None:
            return None
        try:
            return cast(str(fallback))
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return None


def get_cors_origins(default: Optional[str] = None) -> list[str]:
    """
    Return the list of allowed CORS origins.
    """
    fallback = default if default is not None else settings.CORS_ORIGINS
    raw_value = get_env_value("CORS_ORIGINS", default=fallback)

    if raw_value is None:
        return []

    if isinstance(raw_value, (list, tuple)):
        origins = [str(origin).strip() for origin in raw_value]
    else:
        origins = [origin.strip() for origin in str(raw_value).split(",")]

    return [origin for origin in origins if origin]


def get_access_token_expire_minutes(default: Optional[int] = None) -> int:
    """
    Return the access token expiration window in minutes.
    """
    fallback = default if default is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    result = get_env_value(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=fallback, cast=int
    )

    if result is None:
        return fallback

    return result
