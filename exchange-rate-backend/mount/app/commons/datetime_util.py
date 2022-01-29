from datetime import datetime
from dateutil import tz


def localize_date(dt: datetime) -> datetime:
    return dt.replace(tzinfo=tz.tzlocal())


def timestamp_to_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp)


def current_date() -> datetime:
    return localize_date(datetime.now())


def fromisoformat(iso_format: str) -> datetime:
    return localize_date(datetime.fromisoformat(iso_format))
