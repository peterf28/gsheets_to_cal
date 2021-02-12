import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CAL_ID = "ggnc0gnvp4ggokii0o57qp64ho@group.calendar.google.com"


class Calendar:
    def __init__(self):
        self.service = self.get_cal_service()

    def get_cal_service(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('cal_token.pickle'):
            with open('cal_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'cal_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('cal_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('calendar', 'v3', credentials=creds)

    def create_7am_reminder(self, date, name):
        time = date + datetime.timedelta(hours=7)
        if not self.event_exists(time, name):
            print(f"Creating event: {name} on {time.strftime('%d/%m/%Y at %H:%M')}")
            event = {"summary": name,
                     "start": {
                         "dateTime": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "timeZone": "Europe/London",
                     },
                     "end": {
                         "dateTime": (time + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S"),
                         "timeZone": "Europe/London",
                     },
                     "reminders": {
                         "useDefault": False,
                         "overrides": [
                             {"method": "popup", "minutes": 10},
                         ],
                     },
                     }
            self.service.events().insert(calendarId=CAL_ID, body=event).execute()

    def event_exists(self, date, name):
        hour_after = (date + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        time = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        events_result = self.service.events().list(calendarId=CAL_ID, timeMin=time, timeMax=hour_after, maxResults=10,
                                                   singleEvents=True, orderBy='startTime').execute()
        names = [event["summary"] for event in events_result.get('items', [])]
        return name in names


if __name__ == '__main__':
    cal = Calendar()

    test_time = datetime.datetime(2021, 2, 12, 7)
    print(cal.event_exists(test_time, "test"))
