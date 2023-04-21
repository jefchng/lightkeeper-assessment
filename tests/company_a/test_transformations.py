from datetime import date

from company_a.models.blotter import Transaction, TransformedTransaction
from company_a.transformations import aggregate, compute, patch
from constants import LKIDS, SECURITY_NAMES


def test_aggregate():
    blotter = [
        Transaction(
            date=date(2023, 4, 19),
            lkid="IBM_US",
            ticker="ibm",
            name="International Business Machines Corp.asdf",
            analyst="Bob",
            sector="Information",
            pal=-1,
            exposure=5,
        ),
        Transaction(
            date=date(2023, 4, 19),
            lkid="IBM_US",
            ticker="IBM",
            name="International Business Machines Corp.",
            analyst="Alice",
            sector="Technology",
            pal=1,
            exposure=10,
        ),
        Transaction(
            date=date(2023, 4, 20),
            lkid="C_US",
            ticker="C",
            name="Citigroup Inc",
            analyst="Bob",
            sector="Finance",
            pal=1,
            exposure=10,
        ),
    ]

    assert aggregate(blotter) == [
        Transaction(
            date=date(2023, 4, 20),
            lkid="C_US",
            ticker=LKIDS.get("C_US"),
            name=SECURITY_NAMES.get(LKIDS.get("C_US")),
            analyst="Bob",
            sector="Finance",
            pal=1,
            exposure=10,
        ),
        Transaction(
            date=date(2023, 4, 19),
            lkid="IBM_US",
            ticker=LKIDS.get("IBM_US"),
            name=SECURITY_NAMES.get(LKIDS.get("IBM_US")),
            analyst="Alice",
            sector="Information",
            pal=0,
            exposure=15,
        ),
    ]


def test_patch():
    t = Transaction(
        date=date(2023, 4, 19),
        lkid="IBM_US",
        ticker="IBM",
        name="International Business Machines Corp.",
        analyst="Alice",
        sector="Technology",
        pal=238600,
        exposure=3976666.667,
    )

    patched_blotter = list(patch([t]))

    expected = t
    expected.sector = "Information Technology"

    assert len(patched_blotter) == 1
    assert patched_blotter[0] == expected


def test_compute():
    blotter = [
        Transaction(
            date=date(2023, 4, 19),
            lkid="IBM_US",
            ticker="IBM",
            name="International Business Machines Corp.",
            analyst="Alice",
            sector="Information",
            pal=17,
            exposure=2342,
        ),
        Transaction(
            date=date(2023, 4, 20),
            lkid="IBM_US",
            ticker="IBM",
            name="International Business Machines Corp.",
            analyst="Alice",
            sector="Information",
            pal=42,
            exposure=2503,
        ),
        Transaction(
            date=date(2023, 4, 19),
            lkid="C_US",
            ticker="C",
            name="Citigroup Inc",
            analyst="Bob",
            sector="Finance",
            pal=145,
            exposure=3543,
        ),
        Transaction(
            date=date(2023, 4, 20),
            lkid="C_US",
            ticker="C",
            name="Citigroup Inc",
            analyst="Bob",
            sector="Finance",
            pal=-900,
            exposure=2315,
        ),
    ]
    assert compute(blotter) == [
        TransformedTransaction(
            date=date(2023, 4, 19),
            lkid="IBM_US",
            ticker="IBM",
            name="International Business Machines Corp.",
            analyst="Alice",
            sector="Information",
            pal=17,
            exposure=2342,
            return_rate=(17 / (2342 + 3543 - 17 - 145)),
        ),
        TransformedTransaction(
            date=date(2023, 4, 20),
            lkid="IBM_US",
            ticker="IBM",
            name="International Business Machines Corp.",
            analyst="Alice",
            sector="Information",
            pal=42,
            exposure=2503,
            return_rate=(42 / (2342 + 3543)),
        ),
        TransformedTransaction(
            date=date(2023, 4, 19),
            lkid="C_US",
            ticker="C",
            name="Citigroup Inc",
            analyst="Bob",
            sector="Finance",
            pal=145,
            exposure=3543,
            return_rate=(145 / (2342 + 3543 - 17 - 145)),
        ),
        TransformedTransaction(
            date=date(2023, 4, 20),
            lkid="C_US",
            ticker="C",
            name="Citigroup Inc",
            analyst="Bob",
            sector="Finance",
            pal=-900,
            exposure=2315,
            return_rate=(-900 / (2342 + 3543)),
        ),
    ]
