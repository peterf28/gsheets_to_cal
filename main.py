"""Takes a events from a google spreadsheet and creates calendar events for them
https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c"""
import datetime
import math
import re

import pandas as pd

from cal_functions import Calendar
from sheets_functions import read_sheet


def get_stats(test_data):
    """
    Takes session type, percentage and test record and returns the weight that has to be added or removed
    :param sess_type: "Finger" or "Pull up"
    :param perc: percentage
    :param test_data: dataframe from google sheet "Testing"
    :return: weight to add or remove e.g. 13 (kg)
    """
    stat_dict = {}
    for sess_type in ("Finger", "Pull up"):
        filtered = test_data.loc[test_data["Session"] == sess_type]
        maxrow = filtered["Date"].idxmax()
        result = int(filtered.loc[maxrow, "Result"])
        weight = int(filtered.loc[maxrow, "Weight"])
        stat_dict[sess_type] = {"result": result, "weight": weight}

    return stat_dict


def check_weight(activity_string, stat_dict):
    if "%" in activity_string:
        perc = int(re.findall(r"(\d+?)%", activity_string)[0])
        sess = "Pull up" if "Pull" in activity_string else "Finger"
        add_weight = math.ceil((perc / 100) * stat_dict[sess]["result"] - stat_dict[sess]["weight"])
        sign = '+' if add_weight > 0 else ''
        activity_string += f" ({sign}{add_weight}kg)"
    return activity_string


def update_from_source():
    """Fetches data from google sheet and saves locally"""
    sheet_id = "1ret94M18UH4XID4GZ5-igJwQ_eNygVwyTG08PY1N8Mg"
    plan = read_sheet(sheet_id, 'Plan!A1:J200')
    test = read_sheet(sheet_id, 'Testing!A1:F14')
    plan.to_pickle("plan_data")
    test.to_pickle("testing_data")


if __name__ == "__main__":
    refresh = False
    if refresh:
        update_from_source()

    plan_data = pd.read_pickle("plan_data")
    testing_data = pd.read_pickle("testing_data")
    test_stats = get_stats(testing_data)
    cal = Calendar()
    event_list = []

    plan_data["compiled"] = [list(filter(None, i)) for i in plan_data.iloc[:, 2:9].values]

    for idx, row in plan_data.iterrows():
        for activity in row["compiled"]:
            activity = check_weight(activity, test_stats)
            day = row["Date"].to_pydatetime()
            if day.date() >= datetime.datetime.now().date():
                cal.create_7am_reminder(day, activity)
