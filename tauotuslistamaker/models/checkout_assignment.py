from . import TimeInterval
from datetime import datetime
from . import Cashier
from . import Checkout

class CheckoutAssignment(TimeInterval):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Cashier, checkout: Checkout):
        super().__init__(start_time, end_time)
        self.cashier = cashier
        self.checkout = checkout


