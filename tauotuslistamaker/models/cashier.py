from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..collections import CashierScheduleCollection

class Cashier:
    def __init__(self, name, schedule: "CashierScheduleCollection"):
        self.name = name
        self.schedule = schedule