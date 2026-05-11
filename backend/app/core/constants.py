from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    RESEARCHER = "researcher"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


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
        "username": "admin",
        "password": "123456",
        "role": UserRole.ADMIN.value,
    },
    {
        "username": "tidesense",
        "password": "tidesense123",
        "role": UserRole.SUPER_ADMIN.value,
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
    {
        "name": "Mersin Limanı",
        "code": "MERSIN_LIMAN",
        "latitude": 36.7960,
        "longitude": 34.6360,
        "city": "Mersin",
        "base_level": 105.0,
    },
    {
        "name": "Antalya Limanı",
        "code": "ANT_LIMAN",
        "latitude": 36.8333,
        "longitude": 30.6000,
        "city": "Antalya",
        "base_level": 102.0,
    },
    {
        "name": "Samsun Limanı",
        "code": "SAM_LIMAN",
        "latitude": 41.2928,
        "longitude": 36.3313,
        "city": "Samsun",
        "base_level": 100.0,
    },
    {
        "name": "Haydarpaşa Limanı",
        "code": "HAY_LIMAN",
        "latitude": 40.9964,
        "longitude": 29.0169,
        "city": "İstanbul",
        "base_level": 108.0,
    },
    {
        "name": "Bandırma Limanı",
        "code": "BAN_LIMAN",
        "latitude": 40.3541,
        "longitude": 27.9658,
        "city": "Balıkesir",
        "base_level": 105.0,
    },
    {
        "name": "Derince Limanı",
        "code": "DER_LIMAN",
        "latitude": 40.7511,
        "longitude": 29.8331,
        "city": "Kocaeli",
        "base_level": 107.0,
    },
    {
        "name": "Ambarlı Limanı",
        "code": "AMB_LIMAN",
        "latitude": 40.9705,
        "longitude": 28.6833,
        "city": "İstanbul",
        "base_level": 108.0,
    },
    {
        "name": "Zonguldak Limanı",
        "code": "ZON_LIMAN",
        "latitude": 41.4564,
        "longitude": 31.7806,
        "city": "Zonguldak",
        "base_level": 102.0,
    },
    {
        "name": "Aliağa Limanı",
        "code": "ALI_LIMAN",
        "latitude": 38.8354,
        "longitude": 26.9388,
        "city": "İzmir",
        "base_level": 106.0,
    },
    {
        "name": "İsdemir Limanı",
        "code": "ISD_LIMAN",
        "latitude": 36.7266,
        "longitude": 36.1950,
        "city": "Hatay",
        "base_level": 104.0,
    },
    {
        "name": "Gemlik Limanı",
        "code": "GEM_LIMAN",
        "latitude": 40.4286,
        "longitude": 29.1368,
        "city": "Bursa",
        "base_level": 106.0,
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
    "MERSIN_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1566838318109-a8bffb91d082?auto=format&fit=crop&w=960&h=540",
    },
    "ANT_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=960&h=540",
    },
    "SAM_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1498673394965-85cb14905c89?auto=format&fit=crop&w=960&h=540",
    },
    "HAY_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=960&h=540",
    },
    "BAN_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1542385151-efd9000785a0?auto=format&fit=crop&w=960&h=540",
    },
    "DER_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1484981138541-3d074aa97716?auto=format&fit=crop&w=960&h=540",
    },
    "AMB_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=960&h=540",
    },
    "ZON_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1506509657218-c0b7ecfb6301?auto=format&fit=crop&w=960&h=540",
    },
    "ALI_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1598901847919-b95dd0fabbb6?auto=format&fit=crop&w=960&h=540",
    },
    "ISD_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1588614959060-4d142dc42f4e?auto=format&fit=crop&w=960&h=540",
    },
    "GEM_LIMAN": {
        "page_url": "",
        "stream_url": "",
        "resolution": "1920x1080",
        "fps": 30,
        "snapshot_url": "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=960&h=540",
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
