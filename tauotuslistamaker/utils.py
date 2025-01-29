from datetime import datetime, timedelta


def round_time_to_nearest_quarter(dt, delta=timedelta(minutes=15)):
    return datetime.min + round((dt - datetime.min) / delta) * delta
