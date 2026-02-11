from ..models import Checkout, Cashier, TimeInterval, CheckoutAssignment, BreakAssignment, BaseAssignment
from datetime import timedelta
from typing import Dict, List

class CheckoutManager:
    INTERVAL_MINUTES = 15  # Managing time in 15-minute intervals
    TOBACCO_RATIO_MAX_TOTAL_CHECKOUTS_KEY = "max_total_checkouts"
    TOBACCO_RATIO_TOBACCO_CHECKOUTS_KEY = "tobacco_checkouts"

    def __init__(self, cashiers: list[Cashier], checkouts: list[Checkout], checkout_config: dict) -> None:
        self.cashiers = cashiers
        self.checkouts = checkouts

        self.checkout_filling_order = checkout_config.get("checkouts_filling_order")
        # All checkouts that are calculated in the tobacco ratio (e.g., all open checkouts or only those in a specific pool)
        self.tobacco_ratio_pool = checkout_config.get("tobacco_ratio_pool")
        self.tobacco_checkout_ratios = checkout_config.get("tobacco_checkout_ratios")
        # stores {Checkout: CheckoutAssignment or BreakAssignment} assignments for the current interval
        self.latest_assignments = {}

        first_start_dt = checkout_config.get("simulation_start_time")
        last_interval_end_dt = checkout_config.get("simulation_end_time")

        # Handle next-day wrap (e.g., if end time is 00:00 and start time is 08:00)
        if last_interval_end_dt < first_start_dt:
            last_interval_end_dt += timedelta(days=1)
        
        self.simulation_end = last_interval_end_dt
        
        # Start the first interval
        first_end_dt = first_start_dt + timedelta(minutes=self.INTERVAL_MINUTES)
        self.current_interval = TimeInterval(first_start_dt, first_end_dt)


    def assign_checkouts_to_cashiers(self) -> None:
        while self.current_interval.end_time <= self.simulation_end:
            # available_cashiers are those that are tauottajas or available to work in a checkout during the current interval
            available_cashiers = [cashier for cashier in self.cashiers if cashier.is_assigned_to_checkout_or_available_during(self.current_interval)]
            open_checkouts_amount = len(available_cashiers)
            checkouts_to_fill = self._determine_checkouts_to_fill(open_checkouts_amount)

            self._assign_cashiers_to_checkouts(available_cashiers, checkouts_to_fill)
            self._advance_interval()

    def _advance_interval(self) -> None:
        """Advance the current interval by INTERVAL_MINUTES."""  
        self.current_interval.move_by_minutes(self.INTERVAL_MINUTES)

    def _determine_checkouts_to_fill(self, checkouts_needed: int) -> list[Checkout]:
        """
        Determines the required checkouts for the current interval, prioritizing mandatory, 
        continuity, and the tobacco ratio within the defined pool.
        """
        
        # 1. SETUP & FILTERING

        open_checkouts = [c for c in self.checkouts if c.is_within_boundary(self.current_interval)]
        if not open_checkouts or checkouts_needed <= 0:
            return []

        checkouts_needed = min(checkouts_needed, len(open_checkouts))

        # ratio_pool_identifiers is the set of checkout identifiers that are included in the tobacco ratio calculations
        # Could maybe add it as a property to the Checkout class instead of doing this string-based matching here, but for now it works and keeps the Checkout class simpler
        ratio_pool_identifiers = {str(identifier) for identifier in self.tobacco_ratio_pool}
        # check which open checkouts are in the tobacco ratio pool (e.g., all open checkouts or only those in a specific pool defined in config), this determines which checkouts are counted towards the tobacco ratio and which are not
        ratio_pool_checkouts = [c for c in open_checkouts if c.identifier in ratio_pool_identifiers]

        # Candidates is a list of tuples (priority, order_index, Checkout) to facilitate sorting.
        # Priority levels (lower = higher priority):
        #   0 - Mandatory checkouts (must always be staffed)
        #   1 - Break coverage (tauottaja keeps checkout open during cashier's break)
        #   2 - Continuity (same cashier continues at checkout from previous interval)
        #   3 - Tobacco checkout (from filling order, slight preference over regular)
        #   4 - Regular checkout (from filling order)
        #   5 - Other open checkouts (not in ratio pool, not mandatory)
        # Priorities 0-1 are guaranteed selection; 2-5 compete for remaining slots.
        candidates: list[tuple[int, int, Checkout]] = []
        added: set[Checkout] = set()
        order_index = 0

        def add_candidate(checkout: Checkout, priority: int) -> None:
            nonlocal order_index
            if checkout not in added:
                candidates.append((priority, order_index, checkout))
                added.add(checkout)
                order_index += 1

        # A. Mandatory checkouts must always be staffed
        for checkout in open_checkouts:
            if checkout.is_mandatory_open:
                add_candidate(checkout, 0)

        # B. Active break coverage takes precedence after mandatory lanes
        for checkout, assignment in self.latest_assignments.items():
            if checkout in open_checkouts and checkout not in added:
                if isinstance(assignment, BreakAssignment):
                    add_candidate(checkout, 1)
                elif isinstance(assignment, CheckoutAssignment):
                    # Check if the cashier who was at this checkout just went on break
                    break_assignment, is_on_break = assignment.cashier.is_on_break_during(self.current_interval)
                    if is_on_break and break_assignment.tauottaja is not None:
                        add_candidate(checkout, 1)
                    else:
                        add_candidate(checkout, 2)

        # C. Add remaining checkouts respecting the configured filling order
        for checkout_identifier in self.checkout_filling_order:
            checkout = next((c for c in ratio_pool_checkouts if c.identifier == str(checkout_identifier)), None)
            if checkout:
                add_candidate(checkout, 3 if checkout.is_tobacco_checkout else 4)

        # D. Finally add any other open checkouts (e.g. self service lanes already added if mandatory)
        for checkout in open_checkouts:
            if checkout.identifier not in ratio_pool_identifiers:
                add_candidate(checkout, 5 if not checkout.is_mandatory_open else 0)

        if not candidates:
            return []

        # Ensure mandatory and break-coverage lanes fit within available staff
        required_checkouts = [chk for priority, _, chk in candidates if priority <= 1]
        if len(required_checkouts) > checkouts_needed:
            raise ValueError(
                f"Not enough cashiers to cover mandatory or break coverage checkouts at {self.current_interval.start_time.strftime('%H:%M')}."
            )

        candidates.sort(key=lambda item: (item[0], item[1]))
        selected = candidates[:checkouts_needed]
        selected_set = {chk for _, _, chk in selected}

        for checkout in required_checkouts:
            if checkout not in selected_set:
                raise ValueError(
                    f"Not enough cashiers to cover mandatory or break coverage checkouts at {self.current_interval.start_time.strftime('%H:%M')}."
                )

        # Could be better to have a method in data_manager ?
        def required_tobacco(total_pool: int) -> int:
            if total_pool <= 0 or not self.tobacco_checkout_ratios:
                return 0
            sorted_ratios = sorted(
                self.tobacco_checkout_ratios,
                key=lambda cfg: cfg[self.TOBACCO_RATIO_MAX_TOTAL_CHECKOUTS_KEY]
            )
            for ratio in sorted_ratios:
                if total_pool <= ratio[self.TOBACCO_RATIO_MAX_TOTAL_CHECKOUTS_KEY]:
                    return ratio[self.TOBACCO_RATIO_TOBACCO_CHECKOUTS_KEY]
            return sorted_ratios[-1][self.TOBACCO_RATIO_TOBACCO_CHECKOUTS_KEY]

        # Utility to calculate current pool/tobacco counts returned as a tuple (total_pool, tobacco_count) based on the current selection, used for validating ratio and guiding adjustments
        def ratio_snapshot(selection: list[tuple[int, int, Checkout]]) -> tuple[int, int]:
            pool_checkouts = [chk for _, _, chk in selection if chk.identifier in ratio_pool_identifiers]
            total_pool = len(pool_checkouts)
            tobacco_count = sum(1 for chk in pool_checkouts if chk.is_tobacco_checkout)
            return total_pool, tobacco_count

        # Attempt to satisfy tobacco ratio by swapping in tobacco lanes when possible
        max_iterations = len(candidates) * 2
        iterations = 0
        while True:
            iterations += 1
            if iterations > max_iterations:
                break

            total_pool, tobacco_count = ratio_snapshot(selected)
            if total_pool == 0:
                break

            required_tobacco_count = required_tobacco(total_pool)
            if tobacco_count >= required_tobacco_count:
                break

            # Identify potential replacements by finding available tobacco checkouts not currently selected and removable non-tobacco checkouts currently selected (while respecting mandatory and break coverage priorities)
            available_tobacco = [item for item in candidates if item[2].is_tobacco_checkout and item[2] not in selected_set]
            removable = [item for item in selected if item[0] > 1 and not item[2].is_tobacco_checkout]

            if not available_tobacco or not removable:
                raise ValueError(
                    f"Cannot satisfy tobacco checkout ratio with available cashiers at {self.current_interval.start_time.strftime('%H:%M')}."
                )

            # Sort available tobacco by priority (lowest first) and removable by priority (highest first) to ensure we swap in the most impactful tobacco lane and remove the least critical non-tobacco lane
            available_tobacco.sort(key=lambda item: (item[0], item[1]))
            removable.sort(key=lambda item: (-item[0], -item[1]))

            replacement = available_tobacco[0]
            to_remove = removable[0]

            selected.remove(to_remove)
            selected.append(replacement)
            selected_set.remove(to_remove[2])
            selected_set.add(replacement[2])
            selected.sort(key=lambda item: (item[0], item[1]))

        # Final validation after ratio adjustments
        total_pool, tobacco_count = ratio_snapshot(selected)
        if total_pool > 0:
            required_tobacco_count = required_tobacco(total_pool)
            if tobacco_count < required_tobacco_count:
                raise ValueError(
                    f"Cannot satisfy tobacco checkout ratio with available cashiers at {self.current_interval.start_time.strftime('%H:%M')}."
                )

        return [checkout for _, _, checkout in selected]

    def _assign_cashiers_to_checkouts(self, 
                                      available_cashiers: list[Cashier], 
                                      checkouts_to_fill: list[Checkout]) -> None:
        new_latest_assignments: Dict[Checkout, BaseAssignment] = {}
        # 1. maximize continuity by reassigning previous cashiers where possible
        for checkout, assignment in self.latest_assignments.items():
            if checkout in checkouts_to_fill:
                originally_assigned_cashier = assignment.cashier
                if isinstance(assignment, CheckoutAssignment):
                    if originally_assigned_cashier in available_cashiers and originally_assigned_cashier.is_available_during(self.current_interval):
                        assignment.extend(self.INTERVAL_MINUTES)
                        new_latest_assignments[checkout] = assignment
                        checkouts_to_fill.remove(checkout)
                        available_cashiers.remove(originally_assigned_cashier)
                        continue
                    break_assignment, is_on_break = originally_assigned_cashier.is_on_break_during(self.current_interval)
                    if is_on_break and break_assignment.tauottaja is not None:
                        break_assignment.checkout = checkout
                        new_latest_assignments[checkout] = break_assignment
                        checkout.assign_cashier(break_assignment)
                        checkouts_to_fill.remove(checkout)
                        available_cashiers.remove(break_assignment.tauottaja)
                        continue

                elif isinstance(assignment, BreakAssignment):
                    tauottaja = assignment.tauottaja
                    if assignment.end_time <= self.current_interval.start_time:
                        if originally_assigned_cashier in available_cashiers and originally_assigned_cashier.is_available_during(self.current_interval):
                            new_assignment = CheckoutAssignment(
                                start_time=self.current_interval.start_time, 
                                end_time=self.current_interval.end_time,
                                cashier=assignment.cashier,
                                checkout=checkout
                            )
                            new_latest_assignments[checkout] = new_assignment   
                            checkout.assign_cashier(new_assignment)
                            assignment.cashier.add_interval(new_assignment)
                            available_cashiers.remove(originally_assigned_cashier)
                            checkouts_to_fill.remove(checkout)
                    else:
                        checkouts_to_fill.remove(checkout)
                        available_cashiers.remove(tauottaja)
                        new_latest_assignments[checkout] = assignment
    
        # 2. New assignments for remaining checkouts 
        for checkout in checkouts_to_fill:
            for cashier in list(available_cashiers):
                if not cashier.is_available_during(self.current_interval):
                    continue
                new_assignment = CheckoutAssignment(
                    start_time=self.current_interval.start_time, 
                    end_time=self.current_interval.end_time,
                    cashier=cashier,
                    checkout=checkout
                )
                new_latest_assignments[checkout] = new_assignment
                checkout.assign_cashier(new_assignment)
                cashier.add_interval(new_assignment)
                available_cashiers.remove(cashier)
                break

        self.latest_assignments = new_latest_assignments
