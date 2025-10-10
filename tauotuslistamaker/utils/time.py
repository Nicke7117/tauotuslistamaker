from datetime import datetime, timedelta

def round_time_to_nearest_quarter(dt, delta=timedelta(minutes=15)):
    return datetime.min + round((dt - datetime.min) / delta) * delta

def time_diff_in_minutes(start: datetime, end: datetime) -> int:
    """Returns the difference between two datetime objects in whole minutes."""
    delta = end - start
    return int(delta.total_seconds() // 60)
