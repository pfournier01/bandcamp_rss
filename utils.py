import datetime

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    if isinstance(val, str):
        return val
    elif isinstance(val, datetime.date):
        return val.isoformat()
    else:
        return str(val)

MONTHS_TO_INT = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}


__all__ = ['adapt_date_iso', 'MONTHS_TO_INT']
