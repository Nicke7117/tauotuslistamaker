from datetime import datetime
from datetime import timedelta

class TimeInterval:
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        if start_time >= end_time:
            raise ValueError("Start time must start before end time")
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise ValueError("Start time and end time must be datetime objects")
        self.start_time = start_time
        self.end_time = end_time

    def contains(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time <= interval.start_time and self.end_time >= interval.end_time

    def overlaps(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time < interval.end_time and self.end_time > interval.start_time
                
    def subtract(self, interval: "TimeInterval") -> list["TimeInterval"]:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        
        if not self.overlaps(interval):
            raise ValueError("Intervals do not overlap")
        
        result_intervals = []
        
        if self.start_time < interval.start_time:
            result_intervals.append(TimeInterval(self.start_time, interval.start_time))
        
        if self.end_time > interval.end_time:
            result_intervals.append(TimeInterval(interval.end_time, self.end_time))
        
        return result_intervals
    
    def length_in_minutes(self):
        return (self.end_time - self.start_time).total_seconds() / 60
    
    def move_by_minutes(self, minutes: int) -> None:
        self.start_time += timedelta(minutes=minutes)
        self.end_time += timedelta(minutes=minutes)
        