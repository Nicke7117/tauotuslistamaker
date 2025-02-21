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
    enrich_breaks_list_with_assigned_checkouts(
        breaks_list_with_assigned_tauottajat, cashier_seating_arrangement)
    format_output(cashier_seating_arrangement, breaks_list_with_assigned_tauottajat)

def enrich_breaks_list_with_assigned_checkouts(breaks_list, cashier_seating_arrangement):
    for checkout in cashier_seating_arrangement:
        for cashier in checkout["cashiers"]:
            for tauottaja in breaks_list:
                for break_ in tauottaja["breaks"]:
                    if break_["name"] == cashier["name"] and cashier["assigned_time_range"]["start_time"] <= break_["start_time"] <= cashier["assigned_time_range"]["end_time"]:
                        break_["assigned_checkout"] = checkout["checkout"]


        
                
    

def format_output(cashier_seating_arrangement, tauottajat):
    for checkout in cashier_seating_arrangement:
        print(f"Checkout {checkout['checkout']}:")
        # sort cashiers by assigned time range start time
        checkout["cashiers"].sort(key=lambda x: x["assigned_time_range"]["start_time"])
        for cashier in checkout["cashiers"]:
            print(f"\t{cashier['name']} ({cashier["assigned_time_range"]['start_time'].strftime("%H:%M")} - {cashier["assigned_time_range"]['end_time'].strftime("%H:%M")})")
        print("Tauottajat:")
        print(tauottajat)
        for tauottaja in tauottajat:
            print(f"{tauottaja["name"]}")
            for break_ in tauottaja["breaks"]:
                print(f"\t{break_['name']}, checkout {break_['assigned_checkout']} ({break_['start_time'].strftime("%H:%M")} - {break_['end_time'].strftime("%H:%M")})")
            


if __name__ == "__main__":
    main()
