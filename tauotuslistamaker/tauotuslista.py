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


def assign_tauottajat(breaks_list, cashiers):
    cashiers_copy = copy.deepcopy(cashiers)
    # Sort the list of dictionaries in descending order based on the length of the "breaks" list
    sorted_breaks_list = sorted(
        breaks_list, key=lambda x: len(x["breaks"]), reverse=True)
    # Assign the tauottaja roles to the cashiers that are able to let as many cashiers as possible to have their breaks
    final_tauotuslista = [{"name": "itse", "breaks": []}]
    # Algoritm to find the best tauottajas
    while sorted_breaks_list != []:
        current_best_tauottaja_candidate = {
            "name": "", "breaks": [], "breaks_able_to_let_cashiers_have_in_minutes": 0}
        for cashier in cashiers["cashiers"]:
            current_tauottaja_candidate = {"name": cashier["name"], "breaks": [
            ], "breaks_able_to_let_cashiers_have_in_minutes": 0}
            for tauottaja in sorted_breaks_list:
                for break_ in tauottaja["breaks"]:
                    if break_["start_time"] >= cashier["shift_start"] and break_["end_time"] <= cashier["shift_end"]:
                        if not current_tauottaja_candidate["breaks"]:
                            current_tauottaja_candidate["breaks"].append(
                                break_)
                            current_tauottaja_candidate["breaks_able_to_let_cashiers_have_in_minutes"] += (
                                break_["end_time"] - break_["start_time"]).total_seconds() / 60
                        elif break_["start_time"] >= current_tauottaja_candidate["breaks"][-1]["end_time"]:
                            current_tauottaja_candidate["breaks"].append(
                                break_)
                            current_tauottaja_candidate["breaks_able_to_let_cashiers_have_in_minutes"] += (
                                break_["end_time"] - break_["start_time"]).total_seconds() / 60
                if current_tauottaja_candidate["breaks_able_to_let_cashiers_have_in_minutes"] > current_best_tauottaja_candidate["breaks_able_to_let_cashiers_have_in_minutes"]:
                    current_best_tauottaja_candidate = current_tauottaja_candidate
        # append the tauottaja to the final_tauotuslista, remove the breaks that the tauottaja is able to let the cashiers have from the sorted_breaks_list and remove breaks_able_to_let_cashiers_have_in_minutes from the dict put in the final list
        del current_best_tauottaja_candidate["breaks_able_to_let_cashiers_have_in_minutes"]
        if len(current_best_tauottaja_candidate["breaks"]) < 3:
            for tauottaja in final_tauotuslista:
                if tauottaja["name"] == "itse":
                    tauottaja["breaks"].extend(
                        current_best_tauottaja_candidate["breaks"])
        else:
            final_tauotuslista.append(current_best_tauottaja_candidate)
        # Remove the selected cashier from the copy
        cashiers_copy["cashiers"][:] = [cashier for cashier in cashiers_copy["cashiers"]
                                        if cashier.get("name") != current_best_tauottaja_candidate["name"]]
        for break_ in current_best_tauottaja_candidate["breaks"]:
            for tauottaja in sorted_breaks_list:
                if break_ in tauottaja["breaks"]:
                    tauottaja["breaks"].remove(break_)
                    if tauottaja["breaks"] == []:
                        sorted_breaks_list.remove(tauottaja)
    # check if the tauottaja has their own breaks in the final list and if not then move the breaks from other tauottajas to the tauottaja
    # TODO: think of a more efficient way to do this
    tauottajas = [tauottaja["name"] for tauottaja in final_tauotuslista]
    for tauottaja in final_tauotuslista:
        for break_ in tauottaja["breaks"]:
            if break_["name"] in tauottajas and break_["name"] != tauottaja["name"]:
                tauottaja["breaks"].remove(break_)
                break_belonging_to_tauottaja_found = False
                for tauottaja_ in final_tauotuslista:
                    if tauottaja_["name"] == break_["name"]:
                        break_belonging_to_tauottaja_found = True
                        # check if the tauottaja break and the break that the tauottaja should let the cashier have overlap, if they overlap, then move the break to be held by themselves
                        for index, break__ in enumerate(tauottaja_["breaks"]):
                            if break_["start_time"] < break__["start_time"] and break_["end_time"] > break__["start_time"]:
                                # if there is no dict with the tauottaja name "itse", then create one, remove the break from the tauottaja and add it to the dict with the tauottaja name "itse", else just remove the break from the tauottaja and add it to the dict with the tauottaja name "itse"¨
                                tauottaja_["breaks"].remove(break__)
                                for tauottaja in final_tauotuslista:
                                    if tauottaja["name"] == "itse":
                                        tauottaja["breaks"].append(break__)
                                break
                            elif break__["start_time"] >= break_["end_time"]:
                                tauottaja_["breaks"].insert(index, break_)
                                break

                        else:
                            tauottaja_["breaks"].append(break_)
                        if break_belonging_to_tauottaja_found:
                            break

    return final_tauotuslista


def get_cashiers_availability(cashiers, breaks_list_with_assigned_tauottajat):
    cashiers_availability = []
    for cashier in cashiers["cashiers"]:
        availability = [{"start_time": cashier["shift_start"],
                         "end_time": cashier["shift_end"]}]
        for tauottaja in breaks_list_with_assigned_tauottajat:
            if tauottaja["name"] == "itse" or tauottaja["name"] == cashier["name"]:
                for break_ in tauottaja["breaks"]:
                    if break_["name"] == cashier["name"]:
                        for availability_time in availability:
                            if break_["start_time"] >= availability_time["start_time"] and break_["end_time"] <= availability_time["end_time"]:
                                split_time_ranges = split_time_range(availability_time["start_time"], availability_time["end_time"], break_[
                                                                     "start_time"], break_["end_time"], "start_time", "end_time")
                                availability.remove(availability_time)
                                availability.extend(split_time_ranges)
        cashiers_availability.append(
            {"name": cashier["name"], "availability": availability})
    return cashiers_availability


def split_time_range(current_start_time_from, current_end_time_to, time_to_split_from, time_to_split_to, time_start_key, time_end_key):
    if current_start_time_from <= time_to_split_from and current_end_time_to >= time_to_split_from:
        time_range_1 = {
            time_start_key: current_start_time_from, time_end_key: time_to_split_from}
        time_range_2 = {
            time_start_key: time_to_split_to, time_end_key: current_end_time_to}
        return [time_range_1, time_range_2]
    elif time_to_split_from <= current_start_time_from and time_to_split_to < current_end_time_to:
        return [{time_start_key: time_to_split_to, time_end_key: current_end_time_to}]
    elif time_to_split_from > current_start_time_from and time_to_split_to >= current_end_time_to:
        return [{time_start_key: current_start_time_from, time_end_key: time_to_split_from}]


def create_seating_arrangement(cashiers_availability, amount_of_checkout_lanes, most_popular_checkouts, least_popular_checkouts, self_service_checkouts, extra_checkouts):
    pass
