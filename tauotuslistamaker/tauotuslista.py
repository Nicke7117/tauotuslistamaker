from datetime import timedelta, datetime
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
    if current_start_time_from < time_to_split_from and current_end_time_to > time_to_split_to:
        print(f"Time {time_to_split_from} - {time_to_split_to} is within the time {current_start_time_from} - {current_end_time_to}\n")
        time_range_1 = {
            time_start_key: current_start_time_from, time_end_key: time_to_split_from}
        time_range_2 = {
            time_start_key: time_to_split_to, time_end_key: current_end_time_to}
        print(f"Split time into two ranges:\n {time_range_1}\n {time_range_2}\n")
        return [time_range_1, time_range_2]
    elif time_to_split_from <= current_start_time_from and time_to_split_to < current_end_time_to:
        print(f"Time {time_to_split_from} - {time_to_split_to} starts before or at the same time as the time {current_start_time_from} - {current_end_time_to} and ends within the time.\n")
        return [{time_start_key: time_to_split_to, time_end_key: current_end_time_to}]
    elif time_to_split_from > current_start_time_from and time_to_split_to >= current_end_time_to:
        print(f"Time {time_to_split_from} - {time_to_split_to} starts within the time {current_start_time_from} - {current_end_time_to} and ends after or at the same time as the time.\n")
        return [{time_start_key: current_start_time_from, time_end_key: time_to_split_from}]


def create_seating_arrangement(cashiers_availability, checkout_lanes_filling_order, self_service_checkouts):
    # print each cashiers availability in the console with a normal time format
    for cashier in cashiers_availability:
        print("Cashier: ", cashier["name"])
        for availability in cashier["availability"]:
            print("Start: ", availability["start_time"].strftime(
                "%H:%M"), "End: ", availability["end_time"].strftime("%H:%M"))
    seating_arrangement = []

    cashiers_availability_copy = copy.deepcopy(cashiers_availability)
    all_checkouts = copy.deepcopy(self_service_checkouts) + copy.deepcopy(checkout_lanes_filling_order)
    
    for i, checkout in enumerate(all_checkouts):
        print("Processing all checkouts:\n")
        print(all_checkouts)
        checkout_availability = {"start": None, "end": None}
        if isinstance(checkout, dict):
            checkout["availability"] = []
            checkout_availability["start"] = datetime.strptime(checkout["opening_time"], "%H:%M")
            checkout_availability["end"] = datetime.strptime(checkout["closing_time"], "%H:%M")
            # Remove the opening_time and closing_time keys from the checkout dict
            del checkout["opening_time"]
            del checkout["closing_time"]
        elif isinstance(checkout, int):
            # Convert the integer to a dictionary with a default structure
            all_checkouts[i] = {"name": f"Checkout {checkout}", "availability": []}
            checkout = all_checkouts[i]
            checkout_availability["start"] = datetime.min
            checkout_availability["end"] = datetime.max
        else:
            # Handle other unexpected types if necessary
            continue
        
        print(f"Initialized checkout:\n {checkout}\n")
        checkout["availability"].append(checkout_availability)

    while cashiers_availability_copy:
        for checkout in all_checkouts:
            checkout_assigned_cashiers = {"checkout": checkout["name"], "cashiers": []}
            while checkout["availability"]:
                print(f"Checkout full availability:\n {checkout['availability']}\n")
                checkout_availability = checkout["availability"].pop(0)
                

                print(f"Processing checkout availability:\n {checkout_availability}\n")

                print(f"searching suitable cashier for checkout {checkout['name']}...\n")
                selected_cashier, selected_cashier_new_availability = find_cashier_to_fill_available_time_at_checkout_lane(
                    cashiers_availability_copy, 
                    checkout_availability["start"], 
                    checkout_availability["end"]
                )
                if selected_cashier is None:
                    print("No suitable cashier found for this availability.\n")
                    continue
                else:
                    print(f"Selected cashier: {selected_cashier['name']} for checkout: {checkout['name']}\n")
                    checkout_assigned_cashiers["cashiers"].append(selected_cashier)
                    for cashier in cashiers_availability_copy:
                        if cashier["name"] == selected_cashier["name"]:
                            if selected_cashier_new_availability == []:
                                cashiers_availability_copy.remove(cashier)
                            else:
                                cashier["availability"] = selected_cashier_new_availability
                            break
    
                    if selected_cashier["assigned_time_range"]["start_time"] > checkout_availability["start"] or selected_cashier["assigned_time_range"]["end_time"] < checkout_availability["end"]:
                        print(f"Selected cashier has a modified availability:\n {selected_cashier_new_availability}\n")
                        checkout_modified_availability = split_time_range(
                            checkout_availability["start"], 
                            checkout_availability["end"], 
                            selected_cashier["assigned_time_range"]["start_time"], 
                            selected_cashier["assigned_time_range"]["end_time"], 
                            time_start_key="start", 
                            time_end_key="end"
                        )
                        print(f"Modified checkout availability from {checkout_availability['start']} - {checkout_availability['end']} because of cashier {selected_cashier['assigned_time_range']['start_time']} - {selected_cashier['assigned_time_range']['end_time']}:\n {checkout_modified_availability}\n")
                        checkout["availability"].extend(checkout_modified_availability)
                        print(f"Updated checkout availability:\n {checkout['availability']}\n")
            print(f"Appending assigned cashiers {checkout_assigned_cashiers} for checkout {checkout['name']} to the seating arrangement.\n")
            seating_arrangement.append(checkout_assigned_cashiers)
            print(f"Cashiers availability after checkout {checkout['name']}:\n {cashiers_availability_copy}\n")
            print(f"Assigned cashiers for checkout {checkout['name']}:\n {checkout_assigned_cashiers['cashiers']}\n")
    return seating_arrangement

def update_candidate(cashier, start_time, end_time, checkout_start, checkout_end):
    new_availability = copy.deepcopy(cashier["availability"])
    new_availability.remove({"start_time": start_time, "end_time": end_time})
    # only split time ranges if the cashier's availability is not fully within the checkout availability time
    if (start_time != checkout_start) or (end_time != checkout_end):
        split_time_ranges = split_time_range(start_time, end_time, checkout_start, checkout_end, time_start_key="start_time", time_end_key="end_time")
        new_availability.extend(split_time_ranges)
    print(f"checkout unavailable time: {checkout_start} - {checkout_end}, cashier available time: {start_time} - {end_time}\n")
    current_best_cashier_candidate = {
        "name": cashier["name"],
        "assigned_time_range": {
            "start_time": checkout_start,
            "end_time": checkout_end
        }
    }
    print(f"Updated candidate:\n {current_best_cashier_candidate} with new availability:\n {new_availability}\n")
    return current_best_cashier_candidate, new_availability

def find_cashier_to_fill_available_time_at_checkout_lane(cashiers_availability, checkout_availability_start_time, checkout_availability_end_time):
    current_best_cashier_candidate = {
        "name": None,
        "assigned_time_range": {
            "start_time": None,
            "end_time": None
        }
    }
    new_availability = []

    print("Starting search for best cashier candidate...\n")
    print(f"Checkout availability start time: {checkout_availability_start_time}, end time: {checkout_availability_end_time}\n")

    for cashier in cashiers_availability:
        print(f"Checking cashier: {cashier['name']}\n")
        for cashier_availability_time in cashier["availability"]:
            print(f"  Cashier availability:\n {cashier_availability_time}\n")

            if cashier_availability_time["start_time"] <= checkout_availability_start_time and cashier_availability_time["end_time"] >= checkout_availability_end_time:
                print("  Found a perfect match for the entire checkout availability time.\n")
                current_best_cashier_candidate, new_availability = update_candidate(
                    cashier, cashier_availability_time["start_time"], cashier_availability_time["end_time"],
                    checkout_availability_start_time, checkout_availability_end_time
                )
                print(f"  Selected cashier:\n {current_best_cashier_candidate}\n")
                return current_best_cashier_candidate, new_availability

            elif cashier_availability_time["start_time"] >= checkout_availability_start_time and cashier_availability_time["end_time"] <= checkout_availability_end_time:
                print("  Cashier availability is within the checkout availability time.\n")
                if current_best_cashier_candidate["assigned_time_range"]["start_time"] is None or (cashier_availability_time["end_time"] - cashier_availability_time["start_time"]).total_seconds() / 60 > (current_best_cashier_candidate["assigned_time_range"]["end_time"] - current_best_cashier_candidate["assigned_time_range"]["start_time"]).total_seconds() / 60:
                    current_best_cashier_candidate, new_availability = update_candidate(
                        cashier, cashier_availability_time["start_time"], cashier_availability_time["end_time"],
                        cashier_availability_time["start_time"], cashier_availability_time["end_time"]
                    )
                    print(f"  Updated best candidate:\n {current_best_cashier_candidate}\n")
                    continue

            elif cashier_availability_time["start_time"] < checkout_availability_end_time and checkout_availability_start_time < cashier_availability_time["end_time"] < checkout_availability_end_time:
                print("  Cashier availability overlaps with the start of the checkout availability time.\n")
                if current_best_cashier_candidate["assigned_time_range"]["start_time"] is None or (cashier_availability_time["end_time"] - checkout_availability_start_time).total_seconds() / 60 > (current_best_cashier_candidate["assigned_time_range"]["end_time"] - current_best_cashier_candidate["assigned_time_range"]["start_time"]).total_seconds() / 60:
                    current_best_cashier_candidate, new_availability = update_candidate(
                        cashier, cashier_availability_time["start_time"], cashier_availability_time["end_time"],
                        checkout_availability_start_time, cashier_availability_time["end_time"]
                    )
                    print(f"  Updated best candidate:\n {current_best_cashier_candidate}\n")
                    continue

            elif checkout_availability_start_time < cashier_availability_time["start_time"] < checkout_availability_end_time and cashier_availability_time["end_time"] > checkout_availability_end_time:
                print("  Cashier availability overlaps with the end of the checkout availability time.\n")
                if current_best_cashier_candidate["assigned_time_range"]["start_time"] is None or (checkout_availability_end_time - cashier_availability_time["start_time"]).total_seconds() / 60 > (current_best_cashier_candidate["assigned_time_range"]["end_time"] - current_best_cashier_candidate["assigned_time_range"]["start_time"]).total_seconds() / 60:
                    current_best_cashier_candidate, new_availability = update_candidate(
                        cashier, cashier_availability_time["start_time"], cashier_availability_time["end_time"],
                        cashier_availability_time["start_time"], checkout_availability_end_time
                    )
                    print(f"  Updated best candidate:\n {current_best_cashier_candidate}\n")
                    continue

    if current_best_cashier_candidate["name"] is None:
        print("No suitable cashier found.\n")
        return None, None
    else:
        print(f"Best cashier candidate found:\n {current_best_cashier_candidate}\n")
        return current_best_cashier_candidate, new_availability
            

def is_time_range_within(outer_time_range, inner_time_range, start_key="start_time", end_key="end_time"):
    """
    Check if the inner time range is fully within the outer time range.

    Parameters:
    - outer_time_range: Dictionary with the outer time range.
    - inner_time_range: Dictionary with the inner time range.
    - start_key: Key for the start time in the dictionaries.
    - end_key: Key for the end time in the dictionaries.

    Returns:
    - Boolean indicating if the inner time range is fully within the outer time range.
    """
    return ( outer_time_range[start_key] <= inner_time_range[start_key] and
            outer_time_range[end_key] >= inner_time_range[end_key])

def get_time_range_duration(time_range, start_key="start_time", end_key="end_time"):
    """
    Get the duration of a time range in minutes.

    Parameters:
    - time_range: Dictionary with the time range.
    - start_key: Key for the start time in the dictionary.
    - end_key: Key for the end time in the dictionary.

    Returns:
    - Duration of the time range in minutes.
    """
    return (time_range[end_key] - time_range[start_key]).total_seconds() / 60 