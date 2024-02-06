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
    'date',
    [datetime.date(2024, 1, 1) + datetime.timedelta(days=i)
     for i in range(366)]
)
def test_get_end_month_date(date):
    results = {
        1: datetime.date(2024, 1, 31),
        2: datetime.date(2024, 2, 29),
        3: datetime.date(2024, 3, 31),
        4: datetime.date(2024, 4, 30),
        5: datetime.date(2024, 5, 31),
        6: datetime.date(2024, 6, 30),
        7: datetime.date(2024, 7, 31),
        8: datetime.date(2024, 8, 31),
        9: datetime.date(2024, 9, 30),
        10: datetime.date(2024, 10, 31),
        11: datetime.date(2024, 11, 30),
        12: datetime.date(2024, 12, 31),
    }

    result = get_end_month_date(date)
    assert result == results[result.month]
