from . import TimeInterval
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Cashier
    from . import Checkout

class AvailableInterval(TimeInterval):
    def __init__(self, start_time: datetime, end_time: datetime, cashier: Optional['Cashier'] = None, checkout: Optional['Checkout'] = None) -> None:
            super().__init__(start_time, end_time)
            self.cashier = cashier
            self.checkout = checkout

            # Check 1: Must be mutually exclusive (XOR logic)
            has_cashier = self.cashier is not None
            has_checkout = self.checkout is not None

            if has_cashier == has_checkout:
                # Fails if both are True (not both) or both are False (must have one)
                raise ValueError("AvailableInterval must be associated with EITHER a cashier (supply) OR a checkout (demand), but not both or neither.")

            # Check 2: Type validation
            if has_cashier and not isinstance(self.cashier, Cashier):
                raise TypeError("cashier must be a Cashier instance.")
            if has_checkout and not isinstance(self.checkout, Checkout):
                raise TypeError("checkout must be a Checkout instance.")
    
    @classmethod
    def for_cashier(cls, start_time: datetime, end_time: datetime, cashier: 'Cashier') -> "AvailableInterval":
        return cls(start_time, end_time, cashier=cashier)
    
    @classmethod
    def for_checkout(cls, start_time: datetime, end_time: datetime, checkout: 'Checkout') -> "AvailableInterval":
        return cls(start_time, end_time, checkout=checkout)
