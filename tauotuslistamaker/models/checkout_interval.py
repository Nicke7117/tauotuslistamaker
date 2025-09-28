from datetime import datetime
from .time_interval import TimeInterval


class CheckoutInterval(TimeInterval):
    """Represents a period when a cashier is assigned to a checkout.

    Attributes:
        checkout: identifier for the checkout (string or int)
    """

    def __init__(self, start_time: datetime, end_time: datetime, checkout) -> None:
        super().__init__(start_time, end_time)
        self.checkout = checkout

    def __repr__(self) -> str:  # pragma: no cover - small helper
        return f"CheckoutInterval({self.start_time!r}, {self.end_time!r}, checkout={self.checkout!r})"
