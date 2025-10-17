from ..models import TimeInterval
from .schedule_collection_base import ScheduleCollectionBase
from ..utils import round_time_to_nearest_quarter
from datetime import datetime, timedelta
from ..models import BreakAssignment, Cashier, AvailableInterval

class CashierScheduleCollection(ScheduleCollectionBase):

    def __init__(self, boundary_interval: TimeInterval, cashier: Cashier):
        super().__init__(boundary_interval)
        self.cashier = cashier

    @property
    def all_breaks(self):
        return [interval for interval in self.all_events if isinstance(interval, BreakAssignment)]
    
    def _wrap_availability(self, interval):
        return AvailableInterval.for_cashier(start_time=interval.start_time, end_time=interval.end_time, cashier=self.cashier)

    def setup_initial_breaks(self):
        """Calculates and commits the required breaks to the schedule."""
        shift_length_minutes = self.boundary_interval.length_in_minutes()
        break_minutes = []

        # Determine break requirements
        if shift_length_minutes < 240:
            # No breaks
            pass
        elif 240 <= shift_length_minutes < 360:
            break_minutes.append(15)
        elif 360 <= shift_length_minutes <= 420:
            break_minutes.extend([15, 15])
        else:  # > 420 minutes
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
                break_interval = BreakAssignment(break_start_time, break_end_time, self.cashier, tauottaja=None)
                cashier_breaks.append(break_interval)

                # Move to the start of the next break's placement zone
                break_start_time = round_time_to_nearest_quarter(
                    break_start_time + timedelta(minutes=length + time_between_breaks)
                )

        # Commit the breaks to the internal collection
        for break_interval in cashier_breaks:
            self.add_interval(break_interval)
        self._availability = None
    
    def is_on_break_during(self, interval: "TimeInterval") -> tuple[BreakAssignment, bool]:
        """Check if the cashier is on a break during the entire specified interval."""
        for break_interval in self.all_breaks:
            if break_interval.contains(interval) and break_interval.cashier is self.cashier:
                return break_interval, True
        return None, False

    def is_on_shift_at(self, date_time: "datetime") -> bool:
        """Check if the cashier is on shift at the specified date and time."""
        if not isinstance(date_time, datetime):
            raise ValueError("date_time must be a datetime object")
        if self.boundary_interval.start_time <= date_time < self.boundary_interval.end_time:
            return True
        return False
    
    def is_tauottaja_during(self, interval: "TimeInterval") -> bool:
        """Check if the cashier is a tauottaja during the entire specified interval."""
        for event in self.all_events:
            if event.contains(interval) and isinstance(event, BreakAssignment) and event.cashier is self.cashier:
                # If the event is not a BreakAssignment, it's a tauottaja assignment
                return True
        return False

    def is_assigned_to_checkout_or_available_during(self, interval: "TimeInterval") -> bool:
        """Check if the cashier is available for checkout duties during the entire specified interval."""
        return self.boundary_interval.contains(interval) and (self.can_add_interval(interval) or not self.is_tauottaja_during(interval))