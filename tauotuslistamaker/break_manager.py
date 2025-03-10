from cashier import Cashier
import copy
import heapq

class BreakManager:
    BREAKS_SEGMENT_KEY = "breaks_segment"
    BREAKS_KEY = "breaks"
    BREAK_MAX_POSTPONE_MINUTES = 30

    def __init__(self, cashiers: list[Cashier]) -> None:
        self.cashiers = copy.deepcopy(cashiers)
        self.breaks_list = self.create_breaks_list()

    def create_breaks_list(self):
        min_heap = []
        for cashier in self.cashiers:
            for cashier_break in cashier.break_times:
                    heapq.heappush(min_heap, (cashier_break))
        breaks_list = [{self.BREAKS_SEGMENT_KEY: 1, self.BREAKS_KEY: []}]

        while len(min_heap) > 0:
            # get the earliest break of all cashiers
            current_earliest_break = heapq.heappop(min_heap)

            # find a segment where the break can be added
            # the maximum time for moving a break is stored in BREAK_MAX_POSTPONE_MINUTES
            # if the break cannot be added to any segment, create a new segment
            for i, breaks_segment in enumerate(breaks_list):
                
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
                elif i == len(breaks_list) - 1:
                    breaks_list.append(
                        {self.BREAKS_SEGMENT_KEY: breaks_list[-1][self.BREAKS_SEGMENT_KEY] + 1, self.BREAKS_KEY: [current_earliest_break]})
                    break
                    

        return breaks_list
        