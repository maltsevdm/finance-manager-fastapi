from datetime import date, datetime
from typing import Union


def get_start_month_date(
        input_date: Union[date, datetime] = date.today()
) -> date:
    return date(year=input_date.year, month=input_date.month, day=1)