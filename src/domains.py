from urllib.parse import urlsplit

from tld import get_fld


def registrable_domain(url: str) -> str:
    candidate = url if "://" in url else f"https://{url}"
    parsed = urlsplit(candidate)
    return (
        get_fld(candidate, fail_silently=True)
        or parsed.hostname
        or candidate
    )
