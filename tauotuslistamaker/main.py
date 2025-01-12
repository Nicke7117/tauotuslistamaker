import json
from cashier import calculate_optimal_break_times, turn_cashiers_shift_start_and_end_times_to_datetime
from tauotuslista import create_breaks_list, assign_tauottajat, create_seating_arrangement, get_cashiers_availability
import copy


def main():
    # TODO make cashiers a list and remove the "cashiers" key
    try:
        with open("cashiers.json", "r") as json_file:
            cashiers = turn_cashiers_shift_start_and_end_times_to_datetime(
                json.load(json_file))
            cashiers_shift_start_and_end_times = copy.deepcopy(cashiers)
    except FileNotFoundError:
        print("cashiers.json not found")
        return
    except json.decoder.JSONDecodeError:
        print("cashiers.json is not a valid json file")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

    try:
        with open("config.json", "r") as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        print("config.json not found")
        return
    except json.decoder.JSONDecodeError:
        print("config.json is not a valid json file")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    cashiers_optimal_break_times = calculate_optimal_break_times(cashiers)
    breaks_list = create_breaks_list(cashiers_optimal_break_times)
    breaks_list_with_assigned_tauottajat = assign_tauottajat(
        breaks_list, cashiers)
    cashiers_availability = get_cashiers_availability(
        cashiers, breaks_list_with_assigned_tauottajat)
    cashier_seating_arrangement = create_seating_arrangement(cashiers_availability,
                                                           config["checkout_lanes_filling_order"], config["self_service_checkouts"])
#what dis?
"""    for lane in cashier_seating_arrangement:
        sorted_cashiers = sorted(
            lane["cashiers"], key=lambda x: x["assigned_time_range"]["start_time"])
    for cashier in cashiers_availability:

        for availability in cashier["availability"]:
            start_time = availability["start_time"].strftime("%H:%M")
            end_time = availability["end_time"].strftime("%H:%M")

        for break_ in breaks_list_with_assigned_tauottajat:
            for break_time in break_["breaks"]:
                if break_time["name"] == cashier["name"]:
                    start_time = break_time["start_time"].strftime("%H:%M")
                    end_time = break_time["end_time"].strftime("%H:%M")

        for lane in cashier_seating_arrangement:
            if cashier["name"] in [c["name"] for c in lane["cashiers"]]:
                for assigned_cashier in lane["cashiers"]:
                    if assigned_cashier["name"] == cashier["name"]:
                        start_time = assigned_cashier["assigned_time_range"]["start_time"].strftime(
                            "%H:%M")
                        end_time = assigned_cashier["assigned_time_range"]["end_time"].strftime(
                            "%H:%M") """


if __name__ == "__main__":
    main()
