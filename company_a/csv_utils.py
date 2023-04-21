from typing import Iterable

from pandas import DataFrame, read_csv

from company_a.column_names import DATE
from company_a.models.blotter import Transaction
from constants import DATE_FORMAT


def read_blotter_csv(filename) -> Iterable[Transaction]:
    df = read_csv(filename)
    df[DATE] = df[DATE].astype(str).str.zfill(8)
    return [Transaction(**record) for record in df.to_dict("records")]


def write_blotter_csv(blotter: Iterable[Transaction], filename: str) -> None:
    blotter_df = DataFrame.from_records(
        [transaction.to_dict() for transaction in blotter]
    )
    blotter_df.to_csv(filename, date_format=DATE_FORMAT, index=False)
