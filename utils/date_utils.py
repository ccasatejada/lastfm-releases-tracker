from datetime import date, datetime


def format_datetime(dt: datetime) -> str:
    if dt is None:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M')


def format_date(dt: date) -> str:
    if dt is None:
        return ''
    return dt.strftime('%Y-%m-%d')
