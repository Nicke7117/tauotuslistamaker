from datetime import datetime
from datetime import timedelta
from copy import copy

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
    
    def contains(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time <= interval.start_time and self.end_time >= interval.end_time

    def contains_strict(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time < interval.start_time and self.end_time > interval.end_time
    
    def starts_within_and_ends_after(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return (self.start_time >= interval.start_time and self.start_time < interval.end_time) and self.end_time > interval.end_time
    
    def starts_before_and_ends_within(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time < interval.start_time and self.end_time <= interval.end_time
    
    def starts_after_interval_ends(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time > interval.end_time

    def starts_after_or_at(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time >= interval.start_time

    def ends_before_or_at(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.end_time <= interval.end_time

    def ends_after(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.end_time > interval.end_time
    
    def remove_overlaps(self, *args: "TimeInterval") -> list:
        if not args:
            raise ValueError("At least one TimeInterval object must be given")
        if not all(isinstance(interval, TimeInterval) for interval in args):
            raise ValueError("Interval must be a TimeInterval object")
        intervals = [self]

        for interval_arg in args:
            has_been_removed = False
            interval_arg_copy = copy(interval_arg)
            for interval in intervals[:]:
                if interval.contains_interval_strict(interval_arg):
                    intervals.remove(interval)
                    has_been_removed = True
                    intervals.extend([TimeInterval(interval.start_time, interval_arg_copy.start_time), TimeInterval(interval_arg_copy.end_time, interval.end_time)])
                elif interval.starts_within_and_ends_after(interval_arg):
                    intervals.remove(interval)
                    intervals.append(TimeInterval(interval_arg_copy.end_time, interval.end_time))
                    interval_arg_copy.end_time = interval.start_time
                elif interval.starts_before_and_ends_within(interval_arg):
                    intervals.remove(interval)
                    intervals.append(TimeInterval(interval.start_time, interval_arg_copy.start_time))
                    interval_arg_copy.start_time = interval.end_time
            if not has_been_removed:
                raise ValueError(f"Interval {interval_arg} is not overlapping with the given interval")
                
        return intervals
    
    def overlaps(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.start_time < interval.end_time and self.end_time > interval.start_time
                
    def extend_interval(self, interval: "TimeInterval") -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        self.start_time = min(self.start_time, interval.start_time)
        self.end_time = max(self.end_time, interval.end_time)
        
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
    
    def minutes_until_start(self, interval: "TimeInterval") -> int:
        """
        Calculates the time difference in minutes from this interval's end_time 
        to the other interval's start_time. Returns a negative number if they overlap.
        
        Example: 
        A(10:00-11:00).minutes_until_start(B(11:15-12:00)) returns 15.0
        A(10:00-11:00).minutes_until_start(B(10:30-11:30)) returns -30.0
        """
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        time_diff = interval.start_time - self.end_time
        return int(time_diff.total_seconds() / 60)
    
    def starts_earlier_than(self, time_interval: "TimeInterval") -> bool:
        if not isinstance(time_interval, TimeInterval):
            raise ValueError("time_interval must be a TimeInterval object")
        return self.start_time < time_interval.start_time
    
    def move_by_minutes(self, minutes: int) -> None:
        self.start_time += timedelta(minutes=minutes)
        self.end_time += timedelta(minutes=minutes)
        