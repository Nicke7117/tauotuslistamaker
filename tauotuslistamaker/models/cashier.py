from ..collections import CashierScheduleCollection
from . import TimeInterval

class Cashier:
    def __init__(self, name, cashier_schedule_collection: CashierScheduleCollection):
        self.name = name
        self.cashier_schedule_collection = cashier_schedule_collection
    
    #change availability can take a parameter to change the availability to a specific time, the param can either be a TimeInterval object or a list of TimeInterval objects
    def change_availability(self, *args: TimeInterval):
        updated_availability = []
        for availability_interval in self.availability:
            try:
                new_availability = availability_interval.remove_overlaps(*args)
                updated_availability.extend(new_availability)
            except ValueError:
                raise ValueError("The cashier is already unavailable at the given time")
        self.availability = updated_availability

    def add_availability(self, availability: TimeInterval):
        # TODO: implement merging/validation logic when adding availability
        # Placeholder implementation to keep file syntactically valid for now.
        if not isinstance(availability, TimeInterval):
            raise ValueError("availability must be a TimeInterval")
        # Append to availability list (caller should ensure no overlaps or normalize afterwards)
        try:
            self.availability.append(availability)
        except AttributeError:
            # If availability attribute not yet initialized, create it
            self.availability = [availability]

    def is_available(self, time: TimeInterval):
        # Check if the cashier is available at the given time interval
        for interval in self.availability:
            if interval.contains_interval(time):
                return True
        return False
        
    def remove_earliest_break(self):
        # Remove the earliest break interval
        if self.break_times:
            self.break_times.pop(0)
        else:
            raise ValueError("Cashier has no breaks")