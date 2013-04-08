import datetime


def get_date_range(start, end):
    """
    Creates a range of dates with start and end being the endpoints
    (inclusive).
    """
    if start > end:
        raise ValueError("start has to be before end!")
    delta = datetime.timedelta(days=1)
    date = start
    while date <= end:
        yield date
        date = date + delta
