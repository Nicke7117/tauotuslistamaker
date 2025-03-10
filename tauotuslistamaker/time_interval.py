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
    
    def ends_after(self, time: datetime) -> bool:
        if not isinstance(time, datetime):
            raise ValueError("Time must be a datetime object")
        return self.end_time > time
    
    def remove_overlap(self, interval: "TimeInterval") -> list:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if self.start_time < interval.start_time and self.end_time > interval.end_time:
            return [ TimeInterval(self.start_time, interval.start_time), TimeInterval(interval.end_time, self.end_time) ]
        elif interval.start_time <= self.start_time and interval.end_time < self.end_time:
            return [ TimeInterval(interval.end_time, self.end_time) ]
        elif interval.start_time > self.start_time and interval.end_time >= self.end_time:
            return [ TimeInterval(self.start_time, interval.start_time) ]
        else:
            raise ValueError("Intervals are the same or do not overlap")
        
    def end_time_overlap_in_min(self, start_time: datetime) -> int:
        if not isinstance(start_time, datetime):
            raise ValueError("Start time must be a datetime object")
        if self.end_time > start_time:
            return (self.end_time - start_time).total_seconds() / 60
        else:
            return 0
        
    def push_time_interval_forward(self, minutes: int) -> None:
        self.start_time += timedelta(minutes=minutes)
        self.end_time += timedelta(minutes=minutes)

    
    def length_in_minutes(self):
        return (self.end_time - self.start_time).total_seconds() / 60
    
    def split_into_smaller_intervals(self, time_intervals: list) -> list:
        if not all(isinstance(interval, TimeInterval) for interval in time_intervals):
            raise ValueError("All elements in the list must be TimeInterval objects")
        smaller_intervals = [self]
        for interval_to_remove in time_intervals:
            i = 0
            while i < len(smaller_intervals):
                if smaller_intervals[i].contains_interval(interval_to_remove):
                    splitted_segment = smaller_intervals[i].remove_overlap(interval_to_remove)
                    smaller_intervals.pop(i)
                    smaller_intervals[i:i] = splitted_segment
                i += 1

        return smaller_intervals
    
    def starts_ealier_than(self, time_interval: "TimeInterval") -> bool:
        if not isinstance(time_interval, TimeInterval):
            raise ValueError("time_interval must be a TimeInterval object")
        return self.start_time < time_interval.start_time
        