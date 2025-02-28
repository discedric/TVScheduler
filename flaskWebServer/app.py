import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'CKVN270225'

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '..', 'Utils', 'config.json')
meeting_path = os.path.join(base_dir, '..', 'Scheduler', 'meetings.json')

with open(config_path,'r') as f:
    config_file = json.load(f)

timezone = pytz.timezone(config_file['timezone'])

def save_config(data):
    with open(config_path,'r') as f:
        config_file = json.load(f)
    # Update de configuratie met de gewijzigde velden
    print(data)
    for key, value in data.items():
        if key in config_file:
            if isinstance(value, list):
                if key == "ROOM_CALENDARS":
                    # Update ROOM_CALENDARS
                    config_file[key] = {}
                    for entry in value:
                        config_file[key][entry['room']] = entry['email']
                else:
                    # Update andere lijstvelden (indien van toepassing)
                    config_file[key] = value
            else:
                config_file[key] = value
    with open(config_path, 'w') as f:
        json.dump(config_file, f, indent=4)
    return jsonify({"status": "success", "config": config_file})

@app.route('/')
def home():
    today = datetime.now(timezone).date().strftime("%d/%m/%Y")
    with open(config_path,'r') as f:
        config_file = json.load(f)
    with open(meeting_path, 'r') as file:
        meetings = json.load(file)
    return render_template('index.html', meetings=meetings, config=config_file, date= today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == config_file["password"]:
            session['logged_in'] = True
            return redirect(url_for('config'))
        else:
            return 'Invalid password, try again!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('home'))

@app.before_request
def require_login():
    if (request.path.startswith('/config') or request.path.startswith('/admin')) and not session.get('logged_in'):
        return redirect(url_for('login'))

@app.route('/admin')
def admin():
    with open(meeting_path, 'r') as file:
        meetings = json.load(file)
    return render_template('admin.html', meetings=meetings, dev=True)

@app.route('/config')
def config():
    timezones = pytz.all_timezones
    with open(config_path,'r') as f:
        config_file = json.load(f)
    return render_template('config.html', config=config_file, timezones=timezones)

@app.route('/save-config', methods=['POST'])
def update_config():
    try:
        new_config = request.json
        return save_config(new_config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
