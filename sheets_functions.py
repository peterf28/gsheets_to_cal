import os
import pickle

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def read_sheet(sh_id, sh_range):
    """Get a dataframe of the contents of a google sheet from it's ID and range"""
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    # Get credentials from pickle file
    if os.path.exists('sheets_token.pickle'):
        with open('sheets_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # put creds from json into pickle file
            flow = InstalledAppFlow.from_client_secrets_file('sheets_credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        with open('sheets_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=sh_id, range=sh_range).execute()
    values_input = result_input.get('values', [])

    if not values_input:
        print('No data found in sheet.')
        return None
    df = pd.DataFrame(values_input[1:], index=None, columns=values_input[0])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df
