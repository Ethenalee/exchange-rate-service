from __future__ import annotations
from decimal import Decimal
from datetime import datetime

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ExchangerateApiResponse:
    result: str
    provider: str
    documentation: str
    terms_of_use: str
    time_last_update_unix: datetime
    time_last_update_utc: str
    time_next_update_unix: datetime
    time_next_update_utc: str
    time_eol_unix: str
    base_code: str
    rates: dict[str, Decimal]
