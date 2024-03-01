from datetime import date, datetime, timedelta


def get_start_month_date(input_date: date | datetime | None = None) -> date:
    if input_date is None:
        input_date = date.today()
    return date(year=input_date.year, month=input_date.month, day=1)


def get_end_month_date(input_date: date | datetime | None = None) -> date:
    if input_date is None:
        input_date = date.today()
    date_start_month = get_start_month_date(input_date)
    date_start_next_month = get_start_month_date(
        date_start_month + timedelta(days=32))
    return date_start_next_month - timedelta(days=1)
