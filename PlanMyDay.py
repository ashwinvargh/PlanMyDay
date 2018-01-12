from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
from dateutil import parser

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
SLEEP_TIME = {"hour" : 3, "minute" : 30, "second" : 0, "microsecond" : 0} # UTC format
CLEAR_PRECISION = {"second" : 0, "microsecond" : 0}


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

def get_sleep_time():
    curr_time = datetime.datetime.utcnow()
    sleep_time = curr_time.replace(**SLEEP_TIME)
    # Add an if statemnet is beyond 7 PM 
    sleep_time = sleep_time.replace(day=sleep_time.day+1)  #UTC format it's next day
    return sleep_time

def get_free_time(service, now):
    """Goes through each event on the calendar for the day and removes that time block"""
    upper_bound = get_sleep_time().isoformat() + 'Z'
    interval = get_sleep_time() - datetime.datetime.utcnow()
    eventsResult = service.events().list( # creates an HttpRequest object
        calendarId=CALENDAR_ID,
        timeMin=now, timeMax=upper_bound, singleEvents=True,
        orderBy='startTime').execute() #.execute() gets the response
    events = eventsResult.get('items', []) # return empty if items doesn't exist.

    for event in events:
        start = event['start'].get('dateTime', "12:00") # ignores all-day events
        end = event['end'].get('dateTime', "12:00")
        event_start = parser.parse(start)
        event_end =parser.parse(end)
        interval = interval - (event_end - event_start)


    return interval
def get_tasks():
    tasks = {}
    task = raw_input("What do you need to do? (Hit ENTER if that's it.) ")
    tasks[task] = 0
    while (task != ""):
        task = raw_input("What do you need to do? (Hit ENTER if that's it.) ")
        if (task != ""):
            tasks[task] = 0
    return tasks
def update_times(tasks):
    for key in tasks:
        time = input("How much time would you like to spend on " + key + " (minutes) ? ")
        task_duration = datetime.timedelta(minutes=time)
        tasks[key] = task_duration
def main():
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

    free_time = get_free_time(service, now)
    tasks = get_tasks()
    update_times(tasks)

    for key in tasks:
        free_time -= tasks[key]
        
    print("Scheduling tasks... ")

    # inserting an event
    # service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

    # reading the next 10 events
    # print('Getting the upcoming 10 events...')
    # eventsResult = service.events().list( # creates an HttpRequest object
    #     calendarId=CALENDAR_ID,
    #     timeMin=now, maxResults=10, singleEvents=True,
    #     orderBy='startTime').execute() #.execute() gets the response
    # events = eventsResult.get('items', []) # return empty if items doesn't exist.

    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date')) # the DNE case is for all-day events
    #     print(start, event['summary'])


if __name__ == '__main__':
    main()
