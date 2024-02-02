import datetime

import pytest

from src.utils.utils import get_start_month_date, get_end_month_date


@pytest.mark.parametrize(
    'date, res',
    [
        (datetime.date(2023, 1, 28), datetime.date(2023, 1, 1)),
        (datetime.date(2024, 2, 2), datetime.date(2024, 2, 1)),
    ]
)
def test_get_start_month_date(date: datetime.date, res: datetime.date):
    result = get_start_month_date(date)
    assert result == res


@pytest.mark.parametrize(
    'date, res',
    [
        (datetime.date(2023, 1, 28), datetime.date(2023, 1, 31)),
        (datetime.date(2024, 2, 1), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 2), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 4), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 5), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 6), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 7), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 28), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 2, 29), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 3, 1), datetime.date(2024, 3, 31)),
    ]
)
def test_get_end_month_date(date: datetime.date, res: datetime.date):
    result = get_end_month_date(date)
    assert result == res