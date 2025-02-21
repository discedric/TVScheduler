import json
import time
import datetime
import schedule
import wakeonlan
import json
import sys
import signal

# Schedule WOL packets for meetings
# deze loopt constant in de achtergrond
 
with open('config.json','r') as f:
    config = json.load(f)

# MAC addresses of TVs in each room
ROOM_MACS = config['ROOM_MACS']

# JSON file containing meeting data
MEETINGS_FILE = "meetings.json"
scheduled_meetings = set()

def send_wol(room):
    """ Sends a Wake-on-LAN packet to the TV in the specified room """
    print("Try sending a wol-package")
    mac_address = ROOM_MACS.get(room)
    if mac_address:
        wakeonlan.send_magic_packet(mac_address)
        print(f"WOL sent to {room} ({mac_address})")
    else:
        print(f"MAC address for {room} not found!")
    return schedule.CancelJob

def schedule_wol():
    """ Reads meetings.json and schedules WOL packets 5 minutes before meetings """
    try:
        with open(MEETINGS_FILE, "r") as f:
            meetings = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ {MEETINGS_FILE} not found!")
        return
    
    for meeting in meetings:
        room = meeting["room"]
        start_time = datetime.datetime.fromisoformat(meeting["datetime"].replace("Z", ""))
        notify_time = start_time - datetime.timedelta(minutes=5)
        notify_str = notify_time.strftime("%H:%M")
        
        if (room, notify_str) in scheduled_meetings:
            continue  # Skip duplicates
        
        if start_time < datetime.datetime.now():
            continue
        
        scheduled_meetings.add((room, notify_str))
        schedule.every().day.at(notify_str).do(send_wol, room)
        schedule.every().day.at(start_time.strftime("%H:%M")).do(send_wol, room)
        print(f"WOL scheduled for {room} at {notify_str}")
        
def handle_exit(signum,frame):
    print("\n Shutdown requested... Exiting")
    sys.exit(1)

def print_scheduled():
    for job in schedule.get_jobs():
        print(f"Taak:{job.job_func}, Geplant voor: {job.next_run}")

def run_scheduler():
    """ Runs the scheduler continuously """
    while True:
        schedule_wol()
        schedule.run_pending()
        time.sleep(30)
    
        
if __name__ == "__main__":
    # Register signal handler for CTRL + C
    signal.signal(signal.SIGINT, handle_exit)

    if len(sys.argv) != 2:
        try:
            # Run the scheduler loop
            run_scheduler()
        except KeyboardInterrupt:
            handle_exit(None, None)

    room_name = sys.argv[1]
    try:
        send_wol(room_name)
    except KeyboardInterrupt:
        handle_exit(None, None)


