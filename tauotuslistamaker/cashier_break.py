from time_interval import TimeInterval
from datetime import datetime

class CashierBreak(TimeInterval):
    def __init__(self, cashier: "Cashier", start_time: datetime, end_time: datetime):
        super().__init__(start_time, end_time)
        self.cashier = cashier
        self.tauottaja = None
        self.assigned_checkout = None

