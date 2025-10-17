from typing import TYPE_CHECKING, Union
from .time_interval import TimeInterval

if TYPE_CHECKING:
    from ..collections import CheckoutScheduleCollection
    from . import CheckoutAssignment
    
class Checkout:
    def __init__(self, identifier: Union[str, int], schedule: "CheckoutScheduleCollection", is_tobacco_checkout: bool, is_mandatory_open: bool) -> None:
        if isinstance(identifier, str): 
            self.identifier = identifier
        elif isinstance(identifier, int):
            self.identifier = str(identifier)
        else:
            raise ValueError("identifier must be a string or integer")
        self.schedule = schedule
        self.is_tobacco_checkout = is_tobacco_checkout
        self.is_mandatory_open = is_mandatory_open
    
    def is_within_boundary(self, interval: "TimeInterval") -> bool:
        """Check if the checkout is open during the entire specified interval."""
        return self.schedule.is_within_boundary(interval)
    
    def assign_cashier(self, checkout_assignment: "CheckoutAssignment") -> None:
        """Assign a cashier to this checkout."""
        self.schedule.add_interval(checkout_assignment)