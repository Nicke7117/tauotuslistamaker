import bisect
from ..models import TimeInterval
from typing import List

class TimeIntervalCollection:
    def __init__(self):
        self.intervals: List[TimeInterval] = []

    @property
    def last_interval(self) -> TimeInterval | None:
        if not self.intervals:
            return None
        return self.intervals[-1]

    def remove_interval(self, interval: TimeInterval) -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        try:
            self.intervals.remove(interval)
        except ValueError:
            raise ValueError("Interval not found in the collection")

    def find_interval_index(self, interval: TimeInterval) -> int:
        try:
            return self.intervals.index(interval)
        except ValueError:
            raise ValueError("Interval not found in the collection")

    def remove_at_index(self, index: int) -> None:
        if index < 0 or index >= len(self.intervals):
            raise IndexError("Index out of range")
        del self.intervals[index]

    def _find_conflict_intervals(self, interval: TimeInterval) -> List[TimeInterval]:
        """
        Internal helper: Finds all existing intervals that overlap with the new interval.
        Returns a list of overlapping intervals (empty list if none).
        """
        conflicts = []
        positions = [iv.start_time for iv in self.intervals]
        pos = bisect.bisect_left(positions, interval.start_time)

        start_check_index = max(0, pos - 1)

        for i in range(start_check_index, len(self.intervals)):
            existing_interval = self.intervals[i]

            # Optimization: Stop checking if the existing interval starts AFTER the new one ENDS.
            if existing_interval.start_time >= interval.end_time:
                 break

            if existing_interval.overlaps(interval):
                conflicts.append(existing_interval)

        return conflicts

    def can_add_interval(self, interval: TimeInterval) -> bool:
        """
        Checks if an interval can be added without conflicts.
        Returns True if no conflicts exist, False otherwise.
        """
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")

        conflict_intervals = self._find_conflict_intervals(interval)

        return len(conflict_intervals) == 0

    def add_interval(self, interval: TimeInterval) -> None:
        """Adds an interval, ensuring no overlaps and maintaining the sorted order."""
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")

        can_add = self.can_add_interval(interval)

        if not can_add:
            conflicts = self._find_conflict_intervals(interval)
            interval_info = f"{interval.start_time.strftime('%H:%M')}-{interval.end_time.strftime('%H:%M')}"
            conflict_str = ", ".join([f"({c.start_time.strftime('%H:%M')} to {c.end_time.strftime('%H:%M')})" for c in conflicts])
            raise ValueError(f"Interval {interval_info} overlaps with existing intervals: {conflict_str}")

        positions = [iv.start_time for iv in self.intervals]
        insert_pos = bisect.bisect_left(positions, interval.start_time)
        self.intervals.insert(insert_pos, interval)