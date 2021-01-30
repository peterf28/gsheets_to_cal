"""Takes a events from a google spreadsheet and creates calendar events for them
https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c"""
import os
import pickle
import math

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def read_sheet(sh_id, sh_range):
    """Get a dataframe of the contents of a google sheet from it's ID and range"""
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    # Get credentials from pickle file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # put creds from json into pickle file
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=sh_id, range=sh_range).execute()
    values_input = result_input.get('values', [])

    if not values_input:
        print('No data found.')
        return None
    df = pd.DataFrame(values_input[1:], index=None, columns=values_input[0])
    df["Date"] = pd.to_datetime(df["Date"])
    return df


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

    add_weight = get_weight("Finger", 70, testing_data)
    print(plan_data)
    print(testing_data)
    print(f"{add_weight}kg")
