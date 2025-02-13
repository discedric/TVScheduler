import requests
import datetime
import json
from msal import ConfidentialClientApplication
import json

# Azure AD Application registration details
# we kunnen deze laten lopen als een cron job voor elk uur

with open('config.json','w') as f:
    config = json.load(f)

# Microsoft Graph API credentials
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']
TENANT_ID = config['TENANT_ID']

# Room calendars (email addresses)
ROOM_CALENDARS = config['ROOM_CALENDARS']

# JSON file to store meeting data
MEETINGS_FILE = "meetings.json"

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
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    all_meetings = []
    
    for room, email in ROOM_CALENDARS.items():
        url = f"https://graph.microsoft.com/v1.0/users/{email}/calendar/events?$filter=start/dateTime ge '{now}'&$orderby=start/dateTime&$top=10"
        response = requests.get(url, headers=headers)

        print(response)

        if response.status_code == 200:
            meetings = response.json().get("value", [])
            for meeting in meetings:
                start_time = meeting["start"]["dateTime"]
                all_meetings.append({
                    "room": room,
                    "start_time": start_time
                })
    
    # Save meetings to a JSON file
    with open(MEETINGS_FILE, "w") as f:
        json.dump(all_meetings, f, indent=4)
    
    print(f"✅ Meetings saved to {MEETINGS_FILE}")

if __name__ == "__main__":
    fetch_calendar_events()
