"""Takes a events from a google spreadsheet and creates calendar events for them
https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c"""
import math

import pandas as pd

from sheets_functions import read_sheet
from cal_functions import check_event, create_event

def get_weight(sess_type, perc, test_data):
    """
    Takes session type, percentage and test record and returns the weight that has to be added or removed
    :param sess_type: "Finger" or "Pull up"
    :param perc: percentage
    :param test_data: dataframe from google sheet "Testing"
    :return: weight to add or remove e.g. 13 (kg)
    """
    filtered = test_data.loc[test_data["Session"] == sess_type]
    maxrow = filtered["Date"].idxmax()
    result = int(filtered.loc[maxrow, "Result"])
    weight = int(filtered.loc[maxrow, "Weight"])
    output = math.ceil((perc / 100) * result - weight)
    return output


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

    create_event("22/1/21",7,"Floor Core",1)
    # add_weight = get_weight("Finger", 70, testing_data)
    # print(plan_data)
    # print(testing_data)
    # print(f"{add_weight}kg")
