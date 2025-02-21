import requests
from datetime import datetime, time, timedelta
import json
from msal import ConfidentialClientApplication
import json
import pytz

# we kunnen deze laten lopen als een cron job voor elk uur

with open('config.json','r') as f:
    config = json.load(f)

# Microsoft Graph API credentials
# Azure AD Application registration details
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']
TENANT_ID = config['TENANT_ID']

# Room calendars (email addresses)
ROOM_CALENDARS = config['ROOM_CALENDARS']

# JSON file to store meeting data
MEETINGS_FILE = "meetings.json"
DUMP_FILE = "dump.json"
with open(DUMP_FILE, 'w') as f:
    json.dump([], f, indent=4)
dump = ""

timezone = pytz.timezone(config['timezone'])
current_time = datetime.now(timezone)

def get_access_token():
    """ Authenticate with Microsoft Graph API and get an access token """
    app = ConfidentialClientApplication(CLIENT_ID, CLIENT_SECRET, authority=f"https://login.microsoftonline.com/{TENANT_ID}")
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    
    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        print("Error retrieving token:", token_response.get("error_description"))
        return None

def fetch_calendar_events():
    token = get_access_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    all_meetings = []

    for room, email in ROOM_CALENDARS.items():
        if "cubefd" in email:
            continue
        print(email)
        today = datetime.now(timezone).date()
        start_of_day = timezone.localize(datetime.combine(today, datetime.min.time()))
        end_of_tomorrow = start_of_day + timedelta(days=1)
        start_of_day = start_of_day.isoformat(timespec='seconds').replace('+01:00', 'Z')
        end_of_tomorrow = end_of_tomorrow.isoformat(timespec='seconds').replace('+01:00', 'Z')
        
        url = f"https://graph.microsoft.com/v1.0/users/{email}/calendar/calendarView?startDateTime={start_of_day}&endDateTime={end_of_tomorrow}&$orderby=start/dateTime"

        response = requests.get(url, headers=headers)
        print(response)

        if response.status_code == 200:
            meetings = response.json().get("value", [])
            dump_meetings(meetings)
            for meeting in meetings:
                start_time_str = meeting["start"]["dateTime"]
                start_time = datetime.fromisoformat(start_time_str).replace(tzinfo=pytz.UTC)  # Maak UTC datetime
                start_time_local = start_time.astimezone(timezone)
                
                
                
                all_meetings.append({
                    "room": meeting.get("location").get("displayName"),
                    "datetime": start_time_str,
                    "time": start_time_local.strftime("%H:%M"),
                    "date": start_time_local.strftime("%d/%m/%Y"),
                    "subject": meeting.get("subject"),
                    "attendees": [{"Person": attendee["emailAddress"]} for attendee in meeting.get("attendees", [])]
                })
        else:
            print(f"Fout bij ophalen van meetings voor {room}: {response.status_code} - {response.text}")

    # sort meetings op basis van datetime
    all_meetings.sort(key=lambda x: datetime.fromisoformat(x["datetime"]))
    
    # Sla op als JSON
    save_meetings(all_meetings)
    dump_meetings(dump)

    print("Meetings opgehaald en opgeslagen.")
    
def save_meetings(meetings):
    """schrijf opgehalade meetings naar een JSON-bestand"""
    with open(MEETINGS_FILE, 'w') as f:
        json.dump(meetings, f, indent=4)

def dump_meetings(dump):
    try:
        with open(DUMP_FILE, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    if not isinstance(existing_data, list):
        raise ValueError("Het JSON-bestand moet een lijst bevatten.")

    existing_data.append(dump)

    with open(DUMP_FILE, 'w') as f:
        json.dump(existing_data, f, indent=4)

if __name__ == "__main__":
    fetch_calendar_events()
