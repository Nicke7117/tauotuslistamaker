from .managers import DataManager, BreakManager, CheckoutManager
from datetime import datetime
from .models import CashierBreak


def print_breaks_segments_pretty(segments):
    """Print segments row-by-row in a user friendly format."""
    for seg_idx, segment in enumerate(segments, start=1):
        print(f"Segment {seg_idx}:")
        for b in segment.intervals:
            cashier = getattr(b, 'cashier', None)
            cashier_name = getattr(cashier, 'name', cashier.get('name') if isinstance(cashier, dict) else repr(cashier))
            start = getattr(b, 'start_time', None)
            end = getattr(b, 'end_time', None)
            duration = None
            try:
                duration = int((end - start).total_seconds() / 60)
            except Exception:
                duration = None
            assigned_checkout = getattr(b, 'assigned_checkout', None)
            print(f"  - Cashier: {cashier_name:20} | {start} -> {end} | {duration} min | assigned_checkout={assigned_checkout}")


def print_tauottajat_pretty(assignments):
    """Print tauottaja assignments and the breaks they will cover."""
    print("\nTauottaja assignments:")
    for idx, a in enumerate(assignments, start=1):
        tau = a.get('tauottaja')
        if tau is None:
            tau_name = "Generic staff"
        else:
            tau_name = getattr(tau, 'name', tau.get('name') if isinstance(tau, dict) else repr(tau))
        total = a.get('total_minutes')
        print(f"Tauottaja {idx}: {tau_name} (total_minutes={total})")
        for b in a.get('breaks_covered', []):
            cashier = getattr(b, 'cashier', None)
            cashier_name = getattr(cashier, 'name', cashier.get('name') if isinstance(cashier, dict) else repr(cashier))
            start = getattr(b, 'start_time', None)
            end = getattr(b, 'end_time', None)
            try:
                dur = int((end - start).total_seconds() / 60)
            except Exception:
                dur = None
            print(f"  - covers: {cashier_name:20} | {start} -> {end} | {dur} min")


def main():
    # TODO make cashiers a list and remove the "cashiers" key
    data_manager = DataManager()
    data_manager.load_data("cashiers.json")
    data_manager.load_config("config.json")
    cashiers = data_manager.cashiers
    config = data_manager.config
    all_breaks = data_manager.all_breaks
    checkouts = data_manager.checkouts
    break_manager = BreakManager(cashiers, all_breaks)
    break_manager.generate_breaks_list()
    checkout_manager = CheckoutManager(cashiers, checkouts)
    print_tauotuslista_pretty(break_manager.breaks_schedule_list)


def print_tauotuslista_pretty(assignments):

    print("\n\n--- Tauottaja Assignment Schedule ---")
    
    # Check if the list is empty
    if not assignments:
        print("No breaks were assigned or covered.")
        return

    for idx, a in enumerate(assignments, start=1):
        tau = a.get('tauottaja')
        breaks_covered = a.get('breaks_covered', [])
        total = a.get('total_minutes')
        
        # Determine the tauottaja's name
        if tau is None:
            tau_name = "UNCOVERED BREAKS (Requires Generic Staff)"
        else:
            # Use getattr to safely get the 'name' attribute, falling back to string representation
            tau_name = getattr(tau, 'name', str(tau))
            
        print(f"\nASSIGNMENT {idx}: {tau_name} 👷")
        print(f"Total Minutes Covered: {total} min")
        print("-" * 40)
        
        if tau is None:
            # Handle uncovered breaks
            if not breaks_covered:
                print("  - This assignment is empty (Error in logic or debugging).")
                continue
                
            print("  📋 Uncovered Breaks:")
            for b in breaks_covered:
                cashier = getattr(b, 'cashier', 'N/A')
                cashier_name = getattr(cashier, 'name', repr(cashier))
                start: datetime = getattr(b, 'start_time', None)
                end: datetime = getattr(b, 'end_time', None)
                
                dur = None
                if start and end:
                    try:
                        dur = int((end - start).total_seconds() / 60)
                    except Exception:
                        dur = "N/A"
                
                start_str = start.strftime('%H:%M') if start else 'N/A'
                end_str = end.strftime('%H:%M') if end else 'N/A'
                
                print(f"    - {cashier_name}'s break: {start_str} - {end_str} | Duration: {dur} min")
        else:
            # Show complete schedule for assigned tauottaja
            print("  📅 Complete Schedule:")
            events = tau.events
            if events:
                for sched_idx, interval in enumerate(sorted(events, key=lambda x: x.start_time), 1):
                    start_time = getattr(interval, 'start_time', None)
                    end_time = getattr(interval, 'end_time', None)
                    
                    dur = None
                    if start_time and end_time:
                        try:
                            dur = int((end_time - start_time).total_seconds() / 60)
                        except Exception:
                            dur = "N/A"
                    
                    start_str = start_time.strftime('%H:%M') if start_time else 'N/A'
                    end_str = end_time.strftime('%H:%M') if end_time else 'N/A'
                    
                    # Determine interval type
                    if isinstance(interval, CashierBreak):
                        if interval.cashier == tau:
                            interval_type = "Own Break"
                            print(f"    {sched_idx}. {start_str}-{end_str} ({dur} min) - {interval_type}")
                        else:
                            interval_type = "Break Coverage"
                            covered_cashier = getattr(interval.cashier, 'name', 'Unknown')
                            print(f"    {sched_idx}. {start_str}-{end_str} ({dur} min) - {interval_type} ({covered_cashier})")
                    else:
                        interval_type = "Work Period"
                        print(f"    {sched_idx}. {start_str}-{end_str} ({dur} min) - {interval_type}")
            else:
                print("    (No scheduled intervals)")
            
            # Show breaks specifically covered by this tauottaja
            print("  💼 Breaks Covered:")
            if breaks_covered:
                for b in breaks_covered:
                    cashier = getattr(b, 'cashier', 'N/A')
                    cashier_name = getattr(cashier, 'name', repr(cashier))
                    start: datetime = getattr(b, 'start_time', None)
                    end: datetime = getattr(b, 'end_time', None)
                    
                    dur = None
                    if start and end:
                        try:
                            dur = int((end - start).total_seconds() / 60)
                        except Exception:
                            dur = "N/A"
                    
                    start_str = start.strftime('%H:%M') if start else 'N/A'
                    end_str = end.strftime('%H:%M') if end else 'N/A'
                    
                    print(f"    - {cashier_name}'s break: {start_str} - {end_str} | Duration: {dur} min")
            else:
                print("    (No breaks covered)")
    
    print("\n--- End of Schedule ---")

if __name__ == "__main__":
    main()
