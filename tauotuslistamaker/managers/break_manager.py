from ..models import Cashier
from ..models import Tauottaja
import copy
import heapq

class BreakManager:
    BREAKS_SEGMENT_KEY = "breaks_segment"
    BREAKS_KEY = "breaks"
    BREAK_MAX_POSTPONE_MINUTES = 30

    def __init__(self, cashiers: list[Cashier]) -> None:
        self.cashiers = cashiers
        self.breaks_segments_list = self.create_breaks_segments_list()
        self.tauotuslista = self.assign_tauottajat()

    def create_breaks_segments_list(self):
        min_heap = []
        for cashier in self.cashiers:
            for cashier_break in cashier.break_times:
                    heapq.heappush(min_heap, (cashier_break))
        breaks_segment_list = [{self.BREAKS_SEGMENT_KEY: 1, self.BREAKS_KEY: []}]

        while len(min_heap) > 0:
            # get the earliest break of all cashiers
            current_earliest_break = heapq.heappop(min_heap)

            # find a segment where the break can be added
            # the maximum time for moving a break is stored in BREAK_MAX_POSTPONE_MINUTES
            # if the break cannot be added to any segment, create a new segment
            for i, breaks_segment in enumerate(breaks_segment_list):
                
                breaks_segment_latest_break = breaks_segment[self.BREAKS_KEY][-1] if breaks_segment[self.BREAKS_KEY] else None
                if breaks_segment[self.BREAKS_KEY] == []:
                    breaks_segment[self.BREAKS_KEY].append(current_earliest_break)
                    break
                elif breaks_segment_latest_break.ends_before_or_at(current_earliest_break.start_time):
                    breaks_segment[self.BREAKS_KEY].append(current_earliest_break)
                    break
                elif breaks_segment_latest_break.ends_after(current_earliest_break.start_time):
                    minutes_difference = breaks_segment_latest_break.end_time_overlap_in_min(
                        current_earliest_break.start_time)
                    if minutes_difference <= self.BREAK_MAX_POSTPONE_MINUTES:
                        current_earliest_break.move_break(minutes_difference)
                        breaks_segment[self.BREAKS_KEY].append(current_earliest_break)
                        break
                elif i == len(breaks_segment_list) - 1:
                    breaks_segment_list.append(
                        {self.BREAKS_SEGMENT_KEY: breaks_segment_list[-1][self.BREAKS_SEGMENT_KEY] + 1, self.BREAKS_KEY: [current_earliest_break]})
                    break
                    

        return breaks_segment_list
    
    def assign_tauottajat(self):
        # sort the breaks list by the amount of breaks in each segment
        sorted_breaks_segments_list = sorted(
            self.breaks_segments_list, key=lambda x: len(x[self.BREAKS_KEY]))
        cashiers_copy = copy.deepcopy(self.cashiers)
        # Assign the tauottaja roles to the cashiers that are able to let as many cashiers as possible to have their breaks
        final_tauotuslista = []
        # Algoritm to find the best tauottajas
        #find the cashier that is able to let the most cashiers have their breaks
        while sorted_breaks_segments_list != []:
            current_best_tauottaja_candidate = None
            for cashier in cashiers_copy:
                # Change the cashier instance to a tauottaja instance temporarily
                cashier.__class__ = Tauottaja
                current_tauottaja_candidate = cashier
                for breaks_segment in sorted_breaks_segments_list:
                    for break_ in breaks_segment[self.BREAKS_KEY]:
                        # not sure if should be current_best_tauottaja_candidate or current_tauottaja_candidate                            
                        if current_tauottaja_candidate.shift_interval.contains_interval(break_) and current_tauottaja_candidate.cashier.name is not break_.cashier.name:
                            if not current_tauottaja_candidate.scheduled_cashiers_breaks or current_tauottaja_candidate.get_latest_break().ends_before_or_at(break_.start_time):
                                current_tauottaja_candidate.add_break(break_)

                    if current_best_tauottaja_candidate is None:
                        current_best_tauottaja_candidate = current_tauottaja_candidate
                    elif current_tauottaja_candidate.breaks_in_minutes > current_best_tauottaja_candidate.breaks_in_minutes:
                        current_best_tauottaja_candidate = current_tauottaja_candidate
            # append the tauottaja to the final_tauotuslista, remove the breaks that the tauottaja is able to let the cashiers have from the sorted_breaks_list and remove breaks_able_to_let_cashiers_have_in_minutes from the dict put in the final list
            if current_best_tauottaja_candidate.get_breaks_amount() < 3:
                    # remove the cashier instance variable from the 
                    empty_tauottaja_exists = False
                    for tauottaja in final_tauotuslista:
                        if tauottaja.name is None:
                            tauottaja.add_breaks(current_best_tauottaja_candidate.scheduled_cashiers_breaks)
                            empty_tauottaja_exists = True
                            break
                    if not empty_tauottaja_exists:
                        # Create a new tauottaja instance for cashiers that go to their breaks by themselves
                        empty_tauottaja = Tauottaja()
                        empty_tauottaja.add_breaks(current_best_tauottaja_candidate.scheduled_cashiers_breaks)
                        final_tauotuslista.append(current_best_tauottaja_candidate)

                    # Revert the cashier instance to a cashier instance
                    current_best_tauottaja_candidate.__class__ = Cashier
                    # delete all attributes that are not in the cashier class
                    del current_best_tauottaja_candidate.scheduled_cashiers_breaks
                    del current_best_tauottaja_candidate.breaks_in_minutes


            else:
                final_tauotuslista.append(current_best_tauottaja_candidate)
                
                cashiers_copy.remove(current_best_tauottaja_candidate.cashier)

            #REMove the breaks that the tauottaja is able to let the cashiers have from the sorted_breaks_list
            for break_ in current_best_tauottaja_candidate.scheduled_cashiers_breaks:
                for breaks_segment in sorted_breaks_segments_list:
                    if break_ in breaks_segment[self.BREAKS_KEY]:
                        breaks_segment[self.BREAKS_KEY].remove(break_)
                        if breaks_segment[self.BREAKS_KEY] == []:
                            sorted_breaks_segments_list.remove(breaks_segment)
            print("Sorted breaks segments list: ", sorted_breaks_segments_list)
            print("Final tauotuslista: ", final_tauotuslista)
            print("Cashiers copy: ", cashiers_copy)

        # check if the tauottaja has their own breaks in the final list and if not then move the breaks from other tauottajas to the tauottaja
        # TODO: think of a more efficient way to do this

        return final_tauotuslista