from .managers import DataManager, BreakManager, CheckoutManager


def main():
    data_manager = DataManager()
    data_manager.load_data("cashiers.json")
    data_manager.load_config("config.json")
    cashiers = data_manager.cashiers
    config = data_manager.config
    all_breaks = data_manager.all_breaks
    checkouts = data_manager.checkouts
    break_manager = BreakManager(cashiers, all_breaks)
    break_manager.generate_breaks_list()
    checkout_manager = CheckoutManager(cashiers, checkouts, config)
    checkout_manager.assign_checkouts_to_cashiers()
    checkouts = data_manager.checkouts

    # Print breaks list schedule
    print("\n\n--- Breaks List Schedule ---")
    for i, assignment in enumerate(break_manager.breaks_schedule_list, 1):
        tauottaja_name = assignment['tauottaja'].name if assignment['tauottaja'] else "None"
        print(f"Tauottaja {i}: {tauottaja_name} (total_minutes={assignment['total_minutes']})")
        for break_item in assignment['breaks_covered']:
            print(f"  - covers: {break_item.cashier.name} | {break_item.start_time} -> {break_item.end_time}")

    # Print each cashier's individual schedule
    print("\n\n--- All Cashiers' Personal Schedules ---")
    for cashier in cashiers:
        print(f"\nCASHIER: {cashier.name}")
        print("-" * 40)
        if not cashier.schedule.all_events:
            print("   No scheduled events")
        else:
            print("   Schedule:")
            for idx, event in enumerate(cashier.schedule.all_events, 1):
                event_type = type(event).__name__
                if event_type == "BreakAssignment":
                    if event.cashier == cashier:
                        event_type = "Own Break"
                    elif event.tauottaja == cashier:
                        event_type = f"Break Coverage (for {event.cashier.name})"
                    else:
                        event_type = "Break"
                elif event_type == "CheckoutAssignment":
                    event_type = "Checkout"
                start_time = event.start_time.strftime("%H:%M")
                end_time = event.end_time.strftime("%H:%M")
                duration = (event.end_time - event.start_time).total_seconds() / 60
                print(f"     {idx}. {start_time}-{end_time} ({duration:.0f} min) - {event_type}")
    print("\n--- End of Cashiers' Schedules ---")

    # Print each checkout's individual schedule
    print("\n\n--- Checkout Assignment Schedule ---")
    if not checkouts:
        print("No checkouts found.")
    else:
        for checkout in checkouts:
            print(f"\nCHECKOUT {checkout.identifier}")
            if checkout.is_tobacco_checkout:
                print("   Type: Tobacco Checkout")
            else:
                print("   Type: Regular Checkout")
            if checkout.is_mandatory_open:
                print("   Status: Mandatory Open")
            else:
                print("   Status: Optional")
            print("-" * 40)
            if not checkout.schedule.all_events:
                print("   No assignments")
            else:
                print("   Assignments:")
                for assignment in checkout.schedule.all_events:
                    cashier_name = assignment.cashier.name if hasattr(assignment, 'cashier') and assignment.cashier else "None"
                    start_time = assignment.start_time.strftime("%H:%M")
                    end_time = assignment.end_time.strftime("%H:%M")
                    duration = (assignment.end_time - assignment.start_time).total_seconds() / 60
                    assignment_type = type(assignment).__name__
                    if assignment_type == "BreakAssignment":
                        assignment_type = "Break"
                    elif assignment_type == "CheckoutAssignment":
                        assignment_type = "Checkout"
                    print(f"     {start_time}-{end_time} ({duration:.0f} min) - {cashier_name} ({assignment_type})")
                    if hasattr(assignment, 'tauottaja') and assignment.tauottaja:
                        print(f"       Tauottaja: {assignment.tauottaja.name}")
    print("\n--- End of Checkout Assignment Schedule ---")

if __name__ == "__main__":
    main()