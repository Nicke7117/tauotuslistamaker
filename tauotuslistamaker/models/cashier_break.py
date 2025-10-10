from . import TimeInterval
from datetime import datetime
from . import Cashier

class CashierBreak(TimeInterval):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Cashier):
        super().__init__(start_time, end_time)
        self.cashier = cashier

    def __lt__(self, other):
        return self.start_time < other.start_time


