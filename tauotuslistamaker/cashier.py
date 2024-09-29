from datetime import datetime, timedelta
from utils import round_time_to_nearest_quarter


def calculate_optimal_break_times(cashiers):
    # TODO: remove tauottaja key and only have arrays of containing the break dicts
    cashiers_breaks = []
    for cashier in cashiers["cashiers"]:
        start_time = cashier["shift_start"]
        end_time = cashier["shift_end"]

        time_difference = end_time - start_time
        if time_difference.days < 0:
            time_difference = timedelta(
                days=0, seconds=time_difference.seconds, microseconds=time_difference.microseconds)
        shift_length_minutes = time_difference.total_seconds() / 60

        breaks_length = []
        if shift_length_minutes < 360:
            breaks_length.append(15)
        elif shift_length_minutes >= 360 and shift_length_minutes <= 420:
            breaks_length.append(15)
            breaks_length.append(15)
        else:
            breaks_length.append(15)
            breaks_length.append(30)
            breaks_length.append(15)

        cashier_breaks = []
        split_shift = shift_length_minutes / (len(breaks_length) + 1)
        for i in range(len(breaks_length)):
            start_time = start_time + timedelta(minutes=split_shift)
            start_time_rounded = round_time_to_nearest_quarter(start_time)
            end_time = start_time_rounded + timedelta(minutes=breaks_length[i])
            cashier_breaks.append(
                {"start_time": start_time_rounded, "end_time": end_time})

        cashiers_breaks.append(
            {"name": cashier["name"], "breaks": cashier_breaks})
    return cashiers_breaks


def turn_cashiers_shift_start_and_end_times_to_datetime(cashiers):
    for cashier in cashiers["cashiers"]:
        cashier["shift_start"] = datetime.strptime(
            cashier["shift_start"], "%H:%M")
        cashier["shift_end"] = datetime.strptime(cashier["shift_end"], "%H:%M")

        # If the shift ends at 00:00 or later, it means that the shift ends the next day
        if cashier["shift_start"] > cashier["shift_end"]:
            cashier["shift_end"] = cashier["shift_end"] + timedelta(days=1)
    return cashiers
