from datetime import timedelta
from utils import round_time_to_nearest_quarter
from cashier_break import CashierBreak

class Cashier:
    def __init__(self, name, shift_interval):
        self.name = name
        self.shift_interval = shift_interval
        self.break_times = self.__calculate_breaks()
        # maybe store the information about the assigned checkout in working_segments
        self.working_segments = self._get_working_segments()

    def __calculate_breaks(self):
        shift_length_minutes = self.shift_interval.length_in_minutes()
        break_times_in_min = []
        # 15 minute break for shifts shorter than 6 hours
        # Two 15 minute breaks for shifts between 6 and 7 hours
        # Two 15 minute breaks and one 30 minute lunch break for shifts longer than 7 hours
        if shift_length_minutes < 360:
            break_times_in_min.append(15)
        elif shift_length_minutes >= 360 and shift_length_minutes <= 420:
            break_times_in_min.append(15)
            break_times_in_min.append(15)
        else:
            break_times_in_min.append(15)
            break_times_in_min.append(30)
            break_times_in_min.append(15)

        # Create breaks evenly between the shift start and end times
        cashier_breaks = []
        time_between_breaks = shift_length_minutes / (len(break_times_in_min) + 1)
        break_start_time = round_time_to_nearest_quarter(self.shift_interval.start_time + timedelta(minutes=time_between_breaks))
        for i in range(len(break_times_in_min)):
            break_end_time = break_start_time + timedelta(minutes=break_times_in_min[i])
            break_interval = CashierBreak(self, break_start_time, break_end_time)
            cashier_breaks.append(break_interval)
            break_start_time = round_time_to_nearest_quarter(break_start_time + timedelta(minutes=time_between_breaks))
        
        return cashier_breaks
    
    def _get_working_segments(self):
        # Generate working segments by removing break intervals from the shift interval
        self.working_segments = self.shift_interval.split_into_smaller_intervals(self.break_times)
        return self.working_segments
        
    def remove_earliest_break(self):
        # Remove the earliest break interval
        if self.break_times:
            self.break_times.pop(0)
        else:
            raise ValueError("Cashier has no breaks")