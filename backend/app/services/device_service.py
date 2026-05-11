from datetime import UTC, datetime
import re

from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else None


def parse_browser(user_agent: str) -> str:
    if "Edg/" in user_agent:
        return "Microsoft Edge"
    if "OPR/" in user_agent or "Opera/" in user_agent:
        return "Opera"
    if "Chrome/" in user_agent and "Chromium/" not in user_agent:
        return "Google Chrome"
    if "Firefox/" in user_agent:
        return "Mozilla Firefox"
    if "Safari/" in user_agent and "Chrome/" not in user_agent:
        return "Safari"
    if "PostmanRuntime/" in user_agent:
        return "Postman"
    return "Bilinmeyen tarayıcı"


def parse_os(user_agent: str, platform_hint: str | None = None) -> str:
    platform = (platform_hint or "").strip('" ')
    if platform:
        return platform

    checks = [
        ("Windows", "Windows"),
        ("Mac OS X", "macOS"),
        ("Android", "Android"),
        ("iPhone", "iOS"),
        ("iPad", "iPadOS"),
        ("Linux", "Linux"),
    ]
    for marker, label in checks:
        if marker in user_agent:
            return label

    return "Bilinmeyen işletim sistemi"


def parse_device(user_agent: str, mobile_hint: str | None = None) -> str:
    if mobile_hint == "?1":
        return "Mobil cihaz"
    if "iPad" in user_agent or "Tablet" in user_agent:
        return "Tablet"
    if any(marker in user_agent for marker in ["Mobi", "Android", "iPhone"]):
        return "Mobil cihaz"
    return "Masaüstü / dizüstü"


def clean_hint(value: str | None, max_length: int = 128) -> str | None:
    value = (value or "").strip().strip('"')
    if not value:
        return None
    return value[:max_length]


def collect_login_device_info(
    request: Request,
    platform_hint: str | None = None,
) -> dict[str, str | datetime | None]:
    user_agent = request.headers.get("user-agent", "")
    stored_user_agent = user_agent[:512] if user_agent else None
    ip_address = get_client_ip(request)
    os_name = parse_os(user_agent, platform_hint or request.headers.get("sec-ch-ua-platform"))
    browser = parse_browser(user_agent)
    device_type = parse_device(user_agent, request.headers.get("sec-ch-ua-mobile"))

    return {
        "last_login_at": datetime.now(UTC),
        "last_login_ip": ip_address,
        "last_login_user_agent": stored_user_agent,
        "last_login_device": device_type,
        "last_login_os": os_name,
        "last_login_browser": browser,
    }
