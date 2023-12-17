import datetime


def get_start_month_date() -> datetime.date:
    current_date = datetime.date.today()
    return datetime.date(year=current_date.year, month=current_date.month, day=1)
