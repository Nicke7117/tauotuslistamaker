from ..models import TimeInterval
from . import TimeIntervalCollection
from ..utils import round_time_to_nearest_quarter
from datetime import timedelta
from ..models import CashierBreak

class CashierScheduleCollection:

    def __init__(self, boundary_interval: TimeInterval):
        self.boundary_interval = boundary_interval
        self.intervals = TimeIntervalCollection()
    
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
                break_interval = CashierBreak(break_start_time, break_end_time)
                cashier_breaks.append(break_interval)
                
                # Move to the start of the next break's placement zone
                break_start_time = round_time_to_nearest_quarter(
                    break_start_time + timedelta(minutes=length + time_between_breaks)
                )

        # 3. Commit the breaks to the internal collection
        for break_interval in cashier_breaks:
            self.add_interval(break_interval)

    def add_interval(self, interval: TimeInterval) -> None:
        if not isinstance(interval, TimeInterval):
            raise ValueError("Interval must be a TimeInterval object")
        if not self.boundary_interval.contains_interval(interval):
            raise ValueError("Interval must be within the boundary interval")
        self.intervals.add_interval(interval)

    
        