import json
from cashier import calculate_optimal_break_times, turn_cashiers_shift_start_and_end_times_to_datetime
from tauotuslista import create_breaks_list


def main():
    try:
        with open("cashiers.json", "r") as json_file:
            cashiers = turn_cashiers_shift_start_and_end_times_to_datetime(
                json.load(json_file))
    except FileNotFoundError:
        print("cashiers.json not found")
        return
    except json.decoder.JSONDecodeError:
        print("cashiers.json is not a valid json file")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    cashiers_optimal_break_times = calculate_optimal_break_times(cashiers)
    breaks_list = create_breaks_list(cashiers_optimal_break_times)


if __name__ == "__main__":
    main()
