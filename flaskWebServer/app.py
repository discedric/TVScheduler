from flask import Flask, render_template
import json
import time
import pychromecast
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
cast_name = "THE BARN TV"

# Configureer de Chrome-opties (bijvoorbeeld om headless te draaien)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)


@app.route('/')
def home():
    with open('../Scheduler/meetings.json', 'r') as file:
        meetings = json.load(file)
    return render_template('index.html', meetings=meetings, dev=True)


@app.route('/cast')
async def cast_to_chromecast():
    driver.get("http://localhost:5000/")
    time.sleep(5)

    chromecasts, browser = pychromecast.get_chromecasts()
    print(chromecasts)
    cast = next((cc for cc in chromecasts if cc.device.friendly_name == cast_name), None)
    if cast is None:
        return f"Geen Chromecast met naam '{cast_name}' gevonden!"
    cast.wait()
    
    driver.quit()
    return f"Meetings getoond op {cast_name}!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
