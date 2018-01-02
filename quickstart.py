from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime

try: # here for older python versions (argsparse imported on 2.7 and onwards)
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar' # limit to read/write only.
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
CALENDAR_ID = 'l28ku7sivedk160fdgf0ttnka0@group.calendar.google.com'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path) # Storage class stores and retreives a single Credentials object
    credentials = store.get() # holds refresh and access tokens
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES) # flow object (process -> credentials)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags) # authorization flow in default browser
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """

    event = {
        'summary': 'Google I/O 2018',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2018-01-02T21:00:00-05:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
         'dateTime': '2018-01-02T22:00:00-05:00',
         'timeZone': 'America/Los_Angeles',
        }
    }

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http()) # adds credentials headers to http object
    service = discovery.build('calendar', 'v3', http=http) # creates a discovery service object

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events...')
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    eventsResult = service.events().list( # creates an HttpRequest object
        calendarId=CALENDAR_ID,
        timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute() #.execute() gets the response
    
    events = eventsResult.get('items', []) # return empty if items doesn't exist.

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date')) # the DNE case is for all-day events
        print(start, event['summary'])


if __name__ == '__main__':
    main()
