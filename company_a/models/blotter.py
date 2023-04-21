import datetime

from pydantic import BaseModel, validator

from company_a.column_names import (
    ANALYST,
    DATE,
    EXPOSURE,
    LKID,
    NAME,
    PAL,
    RETURN_RATE,
    SECTOR,
    TICKER,
)
from constants import ALTERNATE_DATE_FORMAT, DATE_FORMAT


class Transaction(BaseModel):
    date: datetime.date
    lkid: str
    ticker: str
    name: str
    analyst: str
    sector: str
    pal: float
    exposure: float

    class Config:
        anystr_strip_whitespace = True

    @validator("date", pre=True)
    def format_date(cls, v) -> datetime.date:
        if type(v) is not datetime.date:
            try:
                return datetime.datetime.strptime(v, DATE_FORMAT).date()
            except Exception:
                return datetime.datetime.strptime(v, ALTERNATE_DATE_FORMAT).date()

        else:
            return v

    def to_dict(self) -> dict:
        return {
            DATE: self.date,
            LKID: self.lkid,
            TICKER: self.ticker,
            NAME: self.name,
            ANALYST: self.analyst,
            SECTOR: self.sector,
            PAL: self.pal,
            EXPOSURE: self.exposure,
        }


class TransformedTransaction(Transaction):
    return_rate: float

    def to_dict(self) -> dict:
        return {**super().to_dict(), RETURN_RATE: self.return_rate}
