from datetime import date, datetime, timedelta
from typing import Union


def get_start_month_date(
        input_date: Union[date, datetime] = date.today()
) -> date:
    return date(year=input_date.year, month=input_date.month, day=1)


def get_end_month_date(
        input_date: Union[date, datetime] = date.today()
) -> date:
    date_start_month = get_start_month_date(input_date)
    date_start_next_month = get_start_month_date(
        date_start_month + timedelta(days=32))
    return date_start_next_month - timedelta(days=1)
