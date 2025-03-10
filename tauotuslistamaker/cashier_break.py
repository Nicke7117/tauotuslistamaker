from time_interval import TimeInterval
from datetime import datetime, timedelta
from cashier import Cashier

class CashierBreak(TimeInterval):
    def __init__(self, cashier: Cashier, start_time: datetime, end_time: datetime):
        super().__init__(start_time, end_time)
        self.cashier = cashier
        self.tauottaja = None
        self.assigned_checkout = None

    def __lt__(self, other):
        return self.start_time < other.start_time

    def move_break(self, minutes: int):
        self.start_time += timedelta(minutes=minutes)
        self.end_time += timedelta(minutes=minutes)
        self.cashier.working_segments = self.cashier._get_working_segments()
