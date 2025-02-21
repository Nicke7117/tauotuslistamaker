from datetime import datetime

class TimeInterval:
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        if start_time >= end_time:
            raise ValueError("Start time must start before end time")
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise ValueError("Start time and end time must be datetime objects")
        self.start_time = start_time
        self.end_time = end_time

    def contains_time(self, time: datetime) -> bool:
        if not isinstance(time, datetime):
            raise ValueError("Time must be a datetime object")
        return self.start_time < time < self.end_time
    
    def contains_interval(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time <= interval.start_time and self.end_time >= interval.end_time
    
    def ends_before_or_at(self, time: datetime) -> bool:
        if not isinstance(time, datetime):
            raise ValueError("Time must be a datetime object")
        return self.end_time <= time
    
    def split_interval_with(self, interval: "TimeInterval") -> list:
        if self.start_time < interval.start_time and self.end_time > interval.end_time:
            return [ TimeInterval(self.start_time, interval.start_time), TimeInterval(interval.end_time, self.end_time) ]
        elif interval.start_time <= self.start_time and interval.end_time < self.end_time:
            return [ TimeInterval(interval.end_time, self.end_time) ]
        elif interval.start_time > self.start_time and interval.end_time >= self.end_time:
            return [ TimeInterval(self.start_time, interval.start_time) ]
        else:
            raise ValueError("Intervals are the same or do not overlap")
        