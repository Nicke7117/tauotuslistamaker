from .base_assignment import BaseAssignment
from datetime import datetime, timedelta
from . import Cashier
from . import Checkout

class CheckoutAssignment(BaseAssignment):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Cashier, checkout: Checkout):
        super().__init__(start_time, end_time, cashier, checkout)

    def extend(self, minutes: int) -> None:
        """Extend the end time of the assignment by the specified number of minutes."""
        self.end_time += timedelta(minutes=minutes)
