from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class RiskSeverity(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "DIKKAT"
    CRITICAL = "KRITIK"


DEMO_USERS = [
    {
        "username": "coastal_user",
        "password": "User123!",
        "role": UserRole.USER.value,
    },
    {
        "username": "marine_researcher",
        "password": "Research123!",
        "role": UserRole.RESEARCHER.value,
    },
    {
        "username": "tidesense",
        "password": "tidesense123",
        "role": UserRole.ADMIN.value,
    },
]


DEFAULT_STATIONS = [
    {
        "name": "İskenderun Limanı",
        "code": "ISK_LIMAN",
        "latitude": 36.5872,
        "longitude": 36.1735,
        "city": "Hatay",
        "base_level": 104.0,
    },
    {
        "name": "İzmir Alsancak Limanı",
        "code": "IZM_ALSANCAK",
        "latitude": 38.4404,
        "longitude": 27.1518,
        "city": "İzmir",
        "base_level": 106.0,
    },
    {
        "name": "İstanbul Boğazı",
        "code": "IST_BOGAZ",
        "latitude": 41.0438,
        "longitude": 29.0370,
        "city": "İstanbul",
        "base_level": 108.0,
    },
    {
        "name": "Trabzon Limanı",
        "code": "TRB_LIMAN",
        "latitude": 41.0050,
        "longitude": 39.7300,
        "city": "Trabzon",
        "base_level": 101.0,
    },
]


STATION_STREAMS = {
    "ISK_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1588614959060-4d142dc42f4e?auto=format&fit=crop&w=960&h=540",
    },
    "IZM_ALSANCAK": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1598901847919-b95dd0fabbb6?auto=format&fit=crop&w=960&h=540",
    },
    "IST_BOGAZ": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=960&h=540",
    },
    "TRB_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1616091216791-a0862080a911?auto=format&fit=crop&w=960&h=540",
    },
}


MOON_PHASE_MAP = {
    "New Moon": 0,
    "Waxing Crescent": 1,
    "First Quarter": 2,
    "Waxing Gibbous": 3,
    "Full Moon": 4,
    "Waning Gibbous": 5,
    "Last Quarter": 6,
    "Waning Crescent": 7,
}
