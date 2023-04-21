from typing import Iterable

from pandas import DataFrame

from company_a.column_names import (
    ANALYST,
    DAILY_TOTAL_PAL,
    DATE,
    END_OF_DAY_CAP,
    EXPOSURE,
    LKID,
    NAME,
    PAL,
    RETURN_RATE,
    SECTOR,
    START_OF_DAY_CAP,
    TICKER,
)
from company_a.models.blotter import Transaction, TransformedTransaction
from constants import LKIDS, SECTOR_PATCHES, SECURITY_NAMES


def transform(blotter: Iterable[Transaction]) -> Iterable[TransformedTransaction]:
    return compute(patch(aggregate(blotter)))


def aggregate(blotter: Iterable[Transaction]) -> Iterable[Transaction]:
    """Aggregates blotter, grouping by lkid (unique) by date.
    When aggregating the sector and analyst tags, first alphabetically every day.
    When aggregating P&L and exposure, summed.


    Args:
        blotter (Iterable[TransformedTransaction]): Blotter to be aggregated

    Returns:
        Iterable[TransformedTransaction]: Aggregated Blotter
    """
    blotter_df = DataFrame.from_records(
        [transaction.to_dict() for transaction in blotter]
    )

    aggregated_blotter_df = (
        blotter_df.groupby(
            [
                LKID,
                DATE,
            ],
        )
        .agg({ANALYST: "min", SECTOR: "min", PAL: "sum", EXPOSURE: "sum"})
        .reset_index()
    )

    # Merge with securities information
    detailed_df = aggregated_blotter_df.merge(
        DataFrame(LKIDS.items(), columns=[LKID, TICKER]).merge(
            DataFrame(SECURITY_NAMES.items(), columns=[TICKER, NAME])
        )
    )
    return [Transaction(**record) for record in detailed_df.to_dict("records")]


def patch(blotter: Iterable[Transaction]) -> Iterable[Transaction]:
    """Patch blotter

    Args:
        df (Iterable[TransformedTransaction]): Blotter to be patched

    Returns:
        Iterable[TransformedTransaction]: Patched Blotter
    """
    blotter_df = DataFrame.from_records(
        [transaction.to_dict() for transaction in blotter]
    )

    # Patch sectors column
    blotter_df[SECTOR] = blotter_df[SECTOR].replace(SECTOR_PATCHES)

    return [Transaction(**record) for record in blotter_df.to_dict("records")]


def compute(blotter: Iterable[Transaction]) -> Iterable[TransformedTransaction]:
    """Compute daily returns

    Args:
        Iterable[Transaction] (DataFrame): blotter

    Returns:
        Iterable[TransformedTransaction]: Blotter with return rate
    """
    blotter_df = DataFrame.from_records(
        [transaction.to_dict() for transaction in blotter]
    )

    # Get end of day capital by summing the total exposure for all securities
    blotter_df[END_OF_DAY_CAP] = blotter_df.groupby(DATE)[EXPOSURE].transform("sum")

    # Get total P&L for the day
    blotter_df[DAILY_TOTAL_PAL] = blotter_df.groupby(DATE)[PAL].transform("sum")

    # Get start capital (previous day's end capital).
    # Use end capital - total P&L if there is no previous day
    blotter_df[START_OF_DAY_CAP] = (
        blotter_df.groupby(LKID)[END_OF_DAY_CAP]
        .shift(1)
        .fillna(blotter_df[END_OF_DAY_CAP] - blotter_df[DAILY_TOTAL_PAL])
    )

    # The daily return is pal of the security divided by the
    # beginning of day capital for the entire fund
    blotter_df[RETURN_RATE] = blotter_df[PAL] / blotter_df[START_OF_DAY_CAP]

    return [
        TransformedTransaction(**record) for record in blotter_df.to_dict("records")
    ]
