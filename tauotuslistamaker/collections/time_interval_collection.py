import bisect

from ..models import TimeInterval

"""A class to manage a collection of TimeInterval objects, keeps the intervals sorted and non-overlapping"""
class TimeIntervalCollection:
    def __init__(self):
        self.intervals = []

    def add_interval(self, interval: TimeInterval) -> None:
        """Adds an interval, ensuring no overlaps and maintaining the sorted order."""
        
        # Initial validation checks (Boundary check should be in CashierScheduleCollection, 
        # but is left here for simplicity if this is the only collection)
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
            
        # 1. Use bisect to find pos (O(log n))
        positions = [iv.start_time for iv in self.intervals]
        pos = bisect.bisect_left(positions, interval.start_time)
        
        # 2. Check surrounding neighbors for conflict (O(k))
        
        # Start checking from the interval immediately preceding the insertion point (pos - 1).
        start_check_index = max(0, pos - 1) 
        
        # The loop must check all intervals until the optimization break is triggered.
        # We set the end of the range to the full length of the list.
        for i in range(start_check_index, len(self.intervals)):
            existing_interval = self.intervals[i]
            
            # (Works because the list is sorted by start_time).
            if existing_interval.starts_after_or_at(interval):
                break
                
            # Perform the actual overlap check
            if existing_interval.overlaps(interval):
                raise ValueError("Interval conflicts with existing entries in the collection.")

        # 3. Insert and maintain order
        self.intervals.insert(pos, interval)

