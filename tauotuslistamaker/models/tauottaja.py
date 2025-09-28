from . import Cashier
from . import CashierBreak
from typing import Optional
from . import TimeInterval
from datetime import datetime

class Tauottaja(Cashier):
    def __init__(self, cashier: Optional[Cashier] = None):
        self.cashier = cashier
        self.scheduled_cashiers_breaks = []
        self.breaks_in_minutes = 0

    def add_break(self, break_: CashierBreak):
        self.scheduled_cashiers_breaks.append(break_)
        self.breaks_in_minutes += break_.length_in_minutes()
    
    def add_breaks(self, breaks: list[CashierBreak]):
        for break_ in breaks:
            self.add_break(break_)
    
    # get latest break 
    def get_latest_break(self):
        return self.scheduled_cashiers_breaks[-1]
    
    # make function for returning the absolute amount of breaks in self.scheduled_other_cashiers_breaks
    def get_breaks_amount(self):
        return len(self.scheduled_cashiers_breaks)
    
    def break_fits_in_schedule(self, break_: CashierBreak):
        if self.scheduled_cashiers_breaks:
            return self.get_latest_break().ends_before_or_at(break_.start_time)
        return True
    
    def change_cashier_availability(self):
        self.cashier.working_segments = self.cashier._get_working_segments()
    
