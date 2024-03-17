from datetime import datetime, timedelta


def round_time_to_nearest_quarter(dt, delta=timedelta(minutes=15)):
    return datetime.min + round((dt - datetime.min) / delta) * delta

"""
tauottajas = [tauottaja["name"] for tauottaja in final_tauotuslista]
for tauottaja in final_tauotuslista:
    for break_ in tauottaja["breaks"]:
        if break_["name"] in tauottajas and break_["name"] != tauottaja["name"]:
            for tauottaja_ in final_tauotuslista:
                if tauottaja_["name"] == break_["name"]:
                    for break__ in tauottaja_["breaks"]:
                        # check if the tauottaja break and the break that the tauottaja should let the cashier have overlap 
                        if break_["start_time"] < break__["start_time"] and break_["end_time"] > break__["start_time"]:
                            # if there is no dict with the tauottaja name "itse", then create one, remove the break from the tauottaja and add it to the dict with the tauottaja name "itse", else just remove the break from the tauottaja and add it to the dict with the tauottaja name "itse"¨
                            if not any(tauottaja["name"] == "itse" for tauottaja in final_tauotuslista):
                                final_tauotuslista.append({"name": "itse", "breaks": [break_]})
                                tauottaja_["breaks"].remove(break_)
                            else:
                                tauottaja_["breaks"].remove(break_)
                                for tauottaja in final_tauotuslista:
                                    if tauottaja["name"] == "itse":
                                        tauottaja["breaks"].append(break_) 
"""
