import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

class GoogleCalendar:

    def __init__(self):
        creds_json = "files/creds.json"
        scopes = ['https://www.googleapis.com/auth/calendar']

        creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
        self.service = build('calendar', 'v3', http=creds_service)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            "id": calendar_id
        }
        try:
            return self.service.calendarList().insert(
                body=calendar_list_entry
            ).execute()
        except Exception as ex:
            return False

    def get_events_for_date(self, date, calendar_id):
        return self.service.events().list(calendarId=calendar_id, timeMin=f"{date}T08:30:00+03:00", timeMax=f"{date}T21:30:00+03:00").execute()

    def get_free_times_for_record(self, date, calendar_id):
        events = self.get_events_for_date(date, calendar_id)
        hours_to_record = [str(i) if i >= 10 else f"0{i}" for i in range(9, 22)]
        for event in events["items"]:
            hour = event["start"]["dateTime"].split("T")[-1].split(":")[0]
            if hour in hours_to_record:

                hours_to_record.remove(hour)
        return [f"{hour}:00" for hour in hours_to_record]

    def insert_into_calendar(self, calendar_id, date_from, date_to, summary):
        event = {
            'summary': summary,
            'start': {
                'dateTime': f'{date_from}+03:00',
            },
            'end': {
                'dateTime': f'{date_to}+03:00',
            },
        }

        event = self.service.events().insert(calendarId=calendar_id, body=event).execute()