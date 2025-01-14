"""Connect to Google Service API's.

The `libgoogle` package provides a function to connect to a google
service (such as Calendar, Drive and Mail), and manage credentials
and access tokens under the `XDG` schema.
"""

import httplib2
import xdg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from googleapiclient.discovery import Resource, build  # type: ignore[import-untyped]
from loguru import logger

__all__ = ["connect", "set_debug", "use_cache"]

_USE_CACHE = False
_CACHE: dict[str, Resource] = {}


def connect(scope: str, version: str) -> Resource:
    """Connect to Google service identified by `scope` and `version`.

    Args:
        scope:          (valid examples):
                        "https://www.googleapis.com/auth/gmail"
                        "https://www.googleapis.com/auth/gmail.readonly"
                        "gmail"
                        "gmail.readonly"
                        "drive.metadata.readonly"
                        "photoslibrary.readonly"

        version:        "v1", "v3", etc.

    Files:
        credentials:    XDG_CONFIG_HOME / libgoogle / credentials.json
                        Must exist, or raises FileNotFoundError.

        token:          XDG_CACHE_HOME / libgoogle / {scope}-token.json
    """

    # Normalize `scope` to be abbreviated (without the prefix).
    _scope_prefix = "https://www.googleapis.com/auth/"
    if scope.startswith(_scope_prefix):
        scope = scope[len(_scope_prefix) :]  # strip prefix

    # Check the cache, if we're using it.
    if _USE_CACHE:
        key = f"{scope}-{version}"
        if service := _CACHE.get(key):
            logger.trace(f"Found in cache: key={key!r}")
            return service
        logger.trace(f"Not in cache: key={key!r}")
    else:
        logger.trace("Not using cache")

    # Path to user's credentials.
    _credentials_dir = xdg.xdg_config_home() / "libgoogle"
    _credentials_dir.mkdir(parents=True, exist_ok=True)
    credentials_file = _credentials_dir / "credentials.json"
    if not credentials_file.exists():  # pragma: no cover
        raise FileNotFoundError(f"Can't find credentials: {str(credentials_file)!r}")

    # Path to access token.
    _token_dir = xdg.xdg_cache_home() / "libgoogle"
    _token_dir.mkdir(parents=True, exist_ok=True)
    token_file = _token_dir / f"{scope}-token.json"

    # Check access token.
    scopes = [_scope_prefix + scope]  # fully qualified
    creds = None
    if token_file.exists():
        logger.trace(f"Using access token {str(token_file)!r}")
        creds = Credentials.from_authorized_user_file(token_file, scopes)  # type: ignore[no-untyped-call]

    # Refresh access-token, or (re-)authorize user, as necessary.
    if not creds or not creds.valid:  # pragma: no cover
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
        else:
            logger.debug(f"Signing in with {str(credentials_file)!r}")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        # Save access token.
        with open(token_file, "w", encoding="utf-8") as fp:
            fp.write(creds.to_json())

    # Connect to service.
    service_name = scope.split(".")[0]
    service_version = version
    logger.debug(f"Connecting to service={service_name!r} version={service_version!r}")

    service = build(
        service_name,
        service_version,
        credentials=creds,
        cache_discovery=False,
    )

    if _USE_CACHE:
        _CACHE[key] = service
    return service


def set_debug(flag: bool) -> None:
    """Turn on/off low-level `httplib2` debugging.

    Args:
        flag:   True to turn on debugging, False to turn off.
    """

    if flag:
        httplib2.debuglevel = 4
    else:
        httplib2.debuglevel = 0


def use_cache(flag: bool) -> None:
    """Use cache or not.

    Args:
        flag:   True to use cache, False to not.
    """

    global _USE_CACHE  # pylint: disable=global-statement
    _USE_CACHE = flag
