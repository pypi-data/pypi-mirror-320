"""HTTP Utility functions."""

__all__ = ["route_url", "new_api_key_http_header"]

from typing import Dict

from urllib.parse import urljoin


def route_url(base_url: str, *route_parts: str) -> str:
    """Join the base URL with the given route parts.


    For processing URL route parts, we follow these rules.

    First, we normalize each part:

    1. shrinking consecutive "/" characters to a single "/"
    2. after shrinking, if the it's the last part, preserve trailing "/" but
       drop leading "/"
       1. special case for length 1: leading and trailing "/" are the same, so
          preserve it
    3. after shrinking, if it's not the last part, drop leading and trailing "/"

    Then, we process according to the rules:

    1. if a part is empty, we skip it
    2. if a part is not the last part and is only "/", skip it
    3. if a part is the last part and is not empty, keep it (even if just "/")
    4. otherwise, include the part

    See tests/utils/test_http.py for example path routing.
    """
    return urljoin(base_url, _join_url_path_parts(*route_parts))


def _join_url_path_parts(*route_parts: str) -> str:
    """
    Join the URL path parts.

    We cannot use os.path.join because if a path part starts with "/", it will
    drop all previous parts. This makes sense for UNIX systems, where that means
    it is an absolute path, but we never intend to format URL paths like that,
    so we want to be safe about allowing leading "/".
    """
    parts = []
    for part in route_parts[:-1]:
        part = _normalize_part(part, False)
        if part in ("", "/"):
            continue
        parts.append(part)

    if len(route_parts) > 0 and route_parts[-1]:
        last_part = route_parts[-1]
        last_part = _normalize_part(last_part, True)
        if last_part:
            parts.append(last_part)

    return "/".join(parts)


def _normalize_part(part: str, last_part: bool) -> str:
    # First, change consecutive "/" characters to a single "/".
    chars = []
    is_slash = False
    for char in part:
        if char == "/":
            if not is_slash:
                chars.append("/")
            is_slash = True
        else:
            is_slash = False
            chars.append(char)

    # Base cases
    if len(chars) == 0:
        return ""
    if len(chars) == 1:
        if last_part:
            return "/"
        else:
            return ""

    start_idx = 0
    end_idx = len(chars)
    if chars[0] == "/":
        start_idx = 1
    if chars[-1] == "/":
        if not last_part:
            end_idx -= 1

    return "".join(chars[start_idx:end_idx])


def new_api_key_http_header(api_key: str) -> Dict[str, str]:
    """Create a new API key HTTP header."""
    return {"X-Api-Key": api_key}
