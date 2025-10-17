from datetime import datetime
from . import TimeIntervalCollection
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional 
from ..models import TimeInterval 

if TYPE_CHECKING:
    from ..models import AvailableInterval

class ScheduleCollectionBase(ABC):

    def __init__(self, boundary_interval: "TimeInterval"):
        self.boundary_interval = boundary_interval
        self.intervals = TimeIntervalCollection()
        self._availability: Optional[list["AvailableInterval"]] = None

    @property
    def all_events(self):
        return self.intervals.intervals
    
    @abstractmethod
    def _wrap_availability(self, interval: "TimeInterval") -> "AvailableInterval":
        pass

    @property
    def availability(self) -> list["AvailableInterval"]:
        if self._availability is not None:
            return self._availability
        else:
            calculated_availability = [deepcopy(self.boundary_interval)]
            
            for time_interval in self.all_events:
                new_availability = []
                for available_interval in calculated_availability:
                    if available_interval.contains(time_interval):
                        non_overlapping_parts = available_interval.subtract(time_interval)
                        new_availability.extend(non_overlapping_parts)
                    else:
                        new_availability.append(available_interval)
                calculated_availability = new_availability

            final_availability = [self._wrap_availability(interval) for interval in calculated_availability]
            
            self._availability = final_availability
            return self._availability

    def add_interval(self, interval: "TimeInterval") -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if not self.boundary_interval.contains(interval):
            raise ValueError("Interval must be within the boundary interval")
        self.intervals.add_interval(interval)
        self._availability = None

    def can_add_interval(self, interval: "TimeInterval") -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if not self.boundary_interval.contains(interval):
            return False
        return self.intervals.can_add_interval(interval)
    
    def try_move_interval(self, 
                          original_interval: "TimeInterval", 
                          minutes_to_move: int, 
                          commit: bool = True) -> tuple[bool, Optional["TimeInterval"]]:
        """
        Attempts to move an existing interval by a number of minutes.
        Performs validation against boundaries and conflicts.
        """
        if not isinstance(original_interval, TimeInterval) or not isinstance(minutes_to_move, int):
            raise ValueError("Invalid argument types.")
        
        self.intervals.remove_interval(original_interval)

        # Create the new interval and check rules
        check_interval = deepcopy(original_interval)
        check_interval.move_by_minutes(minutes_to_move)

        if not self.boundary_interval.contains(check_interval) or not self.intervals.can_add_interval(check_interval):
            self.intervals.add_interval(original_interval)
            return False, original_interval

        # Commit or rollback
        if commit:
            original_interval.move_by_minutes(minutes_to_move)
            self.intervals.add_interval(original_interval)
            self._availability = None 
            return True, original_interval
        else:
            self.intervals.add_interval(original_interval)
            return True, check_interval
    
    def remove_interval(self, interval: "TimeInterval") -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        self.intervals.remove_interval(interval)
        self._availability = None 

    def get_continuous_availability_from(self, from_time: "datetime") -> "AvailableInterval":
        """Get the continuous availability block starting from a specific time."""
        if not isinstance(from_time, datetime):
            raise ValueError("from_time must be a datetime object")

        for available_interval in self.availability:
            if available_interval.start_time <= from_time < available_interval.end_time:
                return available_interval
        return None
    
    def is_within_boundary(self, interval: "TimeInterval") -> bool:
        """Check if the given interval is within the boundary interval."""
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        return self.boundary_interval.contains(interval)
