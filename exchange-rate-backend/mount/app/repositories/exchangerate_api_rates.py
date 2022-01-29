from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from app.commons.database import DBSession


@dataclass(frozen=True)
class ExchangerateApiRate:
    rec_id: int
    currrency_code: str
    base_currency_code: str
    rate: Decimal
    time_last_update_unix: datetime
    response: str
    created_at: datetime

    @staticmethod
    def from_rec(rec) -> ExchangerateApiRate:
        return ExchangerateApiRate(
            rec_id=rec.get("rec_id"),
            currrency_code=rec.get("currrency_code"),
            base_currency_code=rec.get("base_currency_code"),
            rate=rec.get("rate"),
            time_last_update_unix=rec.get("time_last_update_unix"),
            response=rec.get("response"),
            created_at=rec.get("created_at"),
        )


class ExchangerateApiRateRepo:
    def __init__(self, db: DBSession):
        self._queries = _QueryBuilder()
        self._db = db

    async def create(
        self,
        currrency_code: str,
        base_currency_code: str,
        rate: Decimal,
        time_last_update_unix: datetime,
        response: str = None
    ) -> ExchangerateApiRate:
        sql = self._queries.create()
        rec = await self._db.exec_write(
            sql,
            {
                "currrency_code": currrency_code,
                "base_currency_code": base_currency_code,
                "rate": rate,
                "time_last_update_unix": time_last_update_unix,
                "response": response
            },
        )
        return ExchangerateApiRate.from_rec(rec)

    async def get_by_currrency_code(self, currrency_code: str) -> \
            List[ExchangerateApiRate]:
        sql = self._queries.get_by_currrency_code()

        recs = await self._db.exec_read(
            sql,
            {"currrency_code": currrency_code},
        )
        return [ExchangerateApiRate.from_rec(rec) for rec in recs]

    async def get_by_time_last_update_unix(self,
                                           time_last_update_unix: datetime) \
            -> List[ExchangerateApiRate]:
        sql = self._queries.get_by_time_last_update_unix()

        recs = await self._db.exec_read(
            sql,
            {"time_last_update_unix": time_last_update_unix},
        )
        return [ExchangerateApiRate.from_rec(rec) for rec in recs]

    async def get_last_rates(self) -> List[ExchangerateApiRate]:
        sql = self._queries.get_last_rates()

        recs = await self._db.exec_read(sql)
        return [ExchangerateApiRate.from_rec(rec) for rec in recs]


class _QueryBuilder:
    TABLE = "exchangerate_api_rates"

    READ_PARAMS = """
                  rec_id,
                  currrency_code,
                  base_currency_code,
                  rate,
                  time_last_update_unix,
                  response,
                  created_at
                """

    BASE_READ = f"""
            SELECT {READ_PARAMS} FROM {TABLE}
        """

    def create(self) -> str:
        return f"""
            INSERT INTO {self.TABLE}
            (
                currrency_code,
                base_currency_code,
                rate,
                time_last_update_unix,
                response
            )
            VALUES (
                :currrency_code,
                :base_currency_code,
                :rate,
                :time_last_update_unix,
                :response
            )
            ON CONFLICT (currrency_code, time_last_update_unix)
                DO UPDATE SET
                    currrency_code = EXCLUDED.currrency_code,
                    time_last_update_unix = EXCLUDED.time_last_update_unix
            RETURNING {self.READ_PARAMS}
            """

    def get_by_currrency_code(self) -> str:
        return f"""
                {self.BASE_READ}
                WHERE currrency_code = :currrency_code
        """

    def get_by_time_last_update_unix(self) -> str:
        return f"""
                {self.BASE_READ}
                WHERE time_last_update_unix = :time_last_update_unix
        """

    def get_last_rates(self) -> str:
        return f"""
                  {self.BASE_READ}
                  WHERE time_last_update_unix =
                  (SELECT MAX(time_last_update_unix)
                  FROM exchangerate_api_rates
                  WHERE currrency_code = exchangerate_api_rates.currrency_code)
        """
