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

timezone = pytz.timezone(config['timezone'])

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
    """ Fetches meetings from Microsoft Graph API and saves them in a JSON file """
    token = get_access_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    all_meetings = []
    
    for room, email in ROOM_CALENDARS.items():
        today = datetime.now(timezone).date()
        #print(start_of_day, end_of_day)
        url = f"https://graph.microsoft.com/v1.0/users/{email}/calendar/events?$filter=start/dateTime ge '{today}'&$orderby=start/dateTime"
    
        response = requests.get(url, headers=headers)

        print(f"Meetings from :{room}")
        print(response)

        if response.status_code == 200:
            meetings = response.json().get("value", [])
            for meeting in meetings:
                start_time_str = meeting["start"]["dateTime"]
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00")) 
                
                if timezone.localize(start_time) < datetime.now(timezone):  # Compare in UTC
                    print(f"Meeting in history: {meeting['subject']} - Start time: {start_time_str}")
                    continue  # Skip historical meetings
                
                all_meetings.append({
                    "room": room,
                    "start_time": start_time_str,
                    "subject":meeting.get("subject"),
                    "attendees":meeting.get("attendees")
                })
    
    # Save meetings to a JSON file
    save_meetings(all_meetings)
    
    print(f"Meetings saved to {MEETINGS_FILE}")
    
def save_meetings(meetings):
    """schrijf opgehalade meetings naar een JSON-bestand"""
    with open(MEETINGS_FILE, 'w') as f:
        json.dump(meetings, f, indent=4)

if __name__ == "__main__":
    fetch_calendar_events()
