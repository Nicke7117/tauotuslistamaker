from abc import ABC
from datetime import datetime

from tauotuslistamaker.models.checkout import Checkout
from . import TimeInterval, Cashier
from typing import Optional

class BaseAssignment(TimeInterval, ABC):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Cashier, checkout: Optional[Checkout] = None) -> None:
        super().__init__(start_time, end_time)
        self.cashier = cashier
        self.checkout = checkout