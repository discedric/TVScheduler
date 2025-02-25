import os
from flask import Flask, render_template
import json
from datetime import datetime
import pytz

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '..', 'Utils', 'config.json')
meeting_path = os.path.join(base_dir, '..', 'Scheduler', 'meetings.json')

with open(config_path,'r') as f:
    config = json.load(f)

timezone = pytz.timezone(config['timezone'])

@app.route('/')
def home():
    today = datetime.now(timezone).date().strftime("%d/%m/%Y")
    with open(meeting_path, 'r') as file:
        meetings = json.load(file)
    return render_template('index.html', meetings=meetings, date= today)

@app.route('/admin')
def admin():
    with open(meeting_path, 'r') as file:
        meetings = json.load(file)
    return render_template('admin.html', meetings=meetings, dev=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
