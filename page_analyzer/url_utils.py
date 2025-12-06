from urllib.parse import urlparse

import validators


MAX_URL_LENGTH = 255


def is_valid_url(url_raw: str) -> bool:
    if not url_raw:
        return False
    if len(url_raw) > MAX_URL_LENGTH:
        return False
    return bool(validators.url(url_raw))


def normalize_url(url_raw: str) -> str:
    parsed = urlparse(url_raw)
    return f"{parsed.scheme}://{parsed.netloc}"
