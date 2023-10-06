import json
from cashier import calculate_optimal_break_times


def main():
    try:
        with open("cashiers.json", "r") as json_file:
            cashiers = json.load(json_file)
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


if __name__ == "__main__":
    main()
