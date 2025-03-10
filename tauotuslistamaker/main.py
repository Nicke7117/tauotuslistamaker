from tauotuslista import create_breaks_list, assign_tauottajat, create_seating_arrangement, get_cashiers_availability
import copy
from data_manager import DataManager
from break_manager import BreakManager


def main():
    # TODO make cashiers a list and remove the "cashiers" key
    data_manager = DataManager()
    data_manager.load_data("cashiers.json")
    data_manager.load_config("config.json")
    cashiers = data_manager.cashiers
    config = data_manager.config
    break_manager = BreakManager(cashiers)

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
