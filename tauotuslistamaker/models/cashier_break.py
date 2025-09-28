from . import TimeInterval
from datetime import datetime

class CashierBreak(TimeInterval):
    def __init__(self, start_time: datetime, end_time: datetime):
        super().__init__(start_time, end_time)

    def __lt__(self, other):
        return self.start_time < other.start_time


