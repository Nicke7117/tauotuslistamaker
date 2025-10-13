from . import TimeInterval
from datetime import datetime
from . import Cashier
from typing import Optional
from . import Checkout

class BreakAssignment(TimeInterval):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Cashier, tauottaja: Cashier, checkout: Optional[Checkout] = None) -> None:
        super().__init__(start_time, end_time)
        self.cashier = cashier
        self.tauottaja = tauottaja
        self.checkout = checkout


