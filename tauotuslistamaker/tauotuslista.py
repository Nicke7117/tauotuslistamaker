from datetime import timedelta
import copy


def create_breaks_list(cashiers_optimal_break_times):
    cashiers_optimal_break_times_copy = copy.deepcopy(
        cashiers_optimal_break_times)
    breaks_list = [{"tauottaja": 1, "breaks": []}]
    while len(cashiers_optimal_break_times_copy) > 0:
        # find the cashier with the earliest break
        current_earliest_break = None
        for cashier in cashiers_optimal_break_times_copy:
            for cashier_break in cashier["breaks"]:
                if current_earliest_break == None:
                    current_earliest_break = {
                        "name": cashier["name"], "start_time": cashier_break["start_time"], "end_time": cashier_break["end_time"]}
                elif cashier_break["start_time"] < current_earliest_break["start_time"]:
                    current_earliest_break = {
                        "name": cashier["name"], "start_time": cashier_break["start_time"], "end_time": cashier_break["end_time"]}
        # add the cashier break to the breaks list
        for i, tauottaja in enumerate(breaks_list):
            if tauottaja["breaks"] == []:
                tauottaja["breaks"].append(current_earliest_break)
                break
            elif current_earliest_break["start_time"] >= tauottaja["breaks"][-1]["end_time"]:
                tauottaja["breaks"].append(current_earliest_break)
                break
            elif current_earliest_break["start_time"] < tauottaja["breaks"][-1]["end_time"]:
                minutes_difference = (
                    tauottaja["breaks"][-1]["end_time"] - current_earliest_break["start_time"]).total_seconds() / 60
                if minutes_difference <= 30:
                    tauottaja["breaks"].append({"name": current_earliest_break["name"], "start_time": current_earliest_break["start_time"] + timedelta(
                        minutes=minutes_difference), "end_time": current_earliest_break["end_time"] + timedelta(minutes=minutes_difference)})
                    break
            # create new tauottaja if the break can't be added to any of the existing tauottajas
            if i == len(breaks_list) - 1:
                breaks_list.append(
                    {"tauottaja": breaks_list[-1]["tauottaja"] + 1, "breaks": [current_earliest_break]})
                break

        # remove the break, that was just added to the breaks list, from cashiers
        cashier_break_to_remove_found = False
        for cashier in cashiers_optimal_break_times_copy:
            if cashier_break_to_remove_found:
                break
            elif cashier["name"] == current_earliest_break["name"]:
                for index, cashier_break in enumerate(cashier["breaks"]):
                    if cashier_break["start_time"] == current_earliest_break["start_time"]:
                        del cashier["breaks"][index]
                        # if the breaks list of the cashier is empty, remove the cashier from the list of cashiers
                        if not cashier["breaks"]:
                            cashiers_optimal_break_times_copy.remove(cashier)
                        cashier_break_to_remove_found = True
                        break
    return breaks_list
