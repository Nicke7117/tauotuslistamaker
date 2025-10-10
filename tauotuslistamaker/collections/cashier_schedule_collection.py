from ..models import TimeInterval
from . import TimeIntervalCollection
from ..utils import round_time_to_nearest_quarter
from datetime import timedelta
from ..models import CashierBreak
from ..models import Cashier
from copy import deepcopy

class CashierScheduleCollection:

    def __init__(self, boundary_interval: TimeInterval, cashier: Cashier):
        self.boundary_interval = boundary_interval
        self.cashier = cashier
        self.intervals = TimeIntervalCollection()

    @property
    def all_events(self):
        return self.intervals.intervals

    @property
    def all_breaks(self):
        return [interval for interval in self.all_events if isinstance(interval, CashierBreak)]

    def setup_initial_breaks(self):
        """Calculates and commits the required breaks to the schedule."""
        shift_length_minutes = self.boundary_interval.length_in_minutes()
        break_minutes = []

        # Determine break requirements
        if shift_length_minutes < 360:
            break_minutes.append(15)
        elif 360 <= shift_length_minutes <= 420:
            break_minutes.extend([15, 15])
        else: # > 420 minutes
            break_minutes.extend([15, 30, 15])

        # Determine break placement with even distribution logic
        cashier_breaks = []
        if break_minutes:
            time_between_breaks = shift_length_minutes / (len(break_minutes) + 1)
            break_start_time = round_time_to_nearest_quarter(
                self.boundary_interval.start_time + timedelta(minutes=time_between_breaks)
            )
            
            for length in break_minutes:
                break_end_time = break_start_time + timedelta(minutes=length)
                break_interval = CashierBreak(break_start_time, break_end_time, self.cashier)
                cashier_breaks.append(break_interval)

                # Move to the start of the next break's placement zone
                break_start_time = round_time_to_nearest_quarter(
                    break_start_time + timedelta(minutes=length + time_between_breaks)
                )

        # Commit the breaks to the internal collection
        for break_interval in cashier_breaks:
            self.add_interval(break_interval)

    def add_interval(self, interval: TimeInterval) -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if not self.boundary_interval.contains(interval):
            raise ValueError("Interval must be within the boundary interval")
        self.intervals.add_interval(interval)

    def can_add_interval(self, interval: TimeInterval) -> bool:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if not self.boundary_interval.contains(interval):
            return False
        return self.intervals.can_add_interval(interval)
    
    def try_move_interval(self, 
                          original_interval: TimeInterval, 
                          minutes_to_move: int, 
                          commit: bool = True) -> tuple[bool, TimeInterval | None]:
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
            return True, original_interval
        else:
            self.intervals.add_interval(original_interval)
            return True, check_interval
    
    def remove_interval(self, interval: TimeInterval) -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        self.intervals.remove_interval(interval)