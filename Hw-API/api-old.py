from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from tinydb import TinyDB, Query
from icalendar import Calendar
from datetime import datetime, timedelta
import json
import sys
import os

os.environ["FLASK_ENV"] = "production"

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
Entry = Query()
db = TinyDB('db/hw.json')

@app.before_request
def log_request():
    path = request.path
    if path.startswith("/calendar"):
        return  # Skip logging for /calendar paths
    ip = request.remote_addr
    if ip.startswith("192.168.1."):
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {ip} requested {path}\n"
    with open("request_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

@app.route('/items/<string:date>', methods=['GET'])
def get_item(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "日期格式錯誤，請使用 YYYY-MM-DD"
    results = db.search(Entry.DueDate == date)
    print("Equired Homework for date:", date)
    return jsonify(results)

@app.route('/items/all', methods=['GET'])
def get_all_items():
    all_data = db.all()
    print("Returning all homework entries")
    return jsonify(all_data)

@app.route('/calendar/<string:caldate>', methods=['GET'])
def get_summary_for_date(caldate):
    file_path='calendar/calendar.ics'
    # Convert string to date object
    try:
        target_date = datetime.strptime(caldate, "%Y-%m-%d").date()
    except ValueError:
        return "日期格式錯誤，請使用 YYYY-MM-DD"
    try:
        with open('cache/'+ caldate, 'r', encoding='utf-8') as file:
            content = file.read()  # Reads the entire content of the file
            return jsonify(content.splitlines())
    except FileNotFoundError:
        with open(file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
            summaries = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    summary = component.get('SUMMARY')
                    dtstart = component.get('DTSTART').dt
                    dtend = component.get('DTEND').dt
                    # Normalize to date if datetime
                    start_date = dtstart.date() if isinstance(dtstart, datetime) else dtstart
                    end_date = dtend.date() if isinstance(dtend, datetime) else dtend

                    # .ics end date is exclusive, so include up to end_date - 1
                    current_date = start_date
                    while current_date < end_date:
                        if current_date == target_date:
                            summaries.append(str(summary))
                        current_date += timedelta(days=1)
            with open('cache/'+ caldate, 'w', encoding='utf-8') as file:
                file.write('\n'.join(summaries))
                file.close()
            return summaries

if __name__ == '__main__':
    app.run(debug=True)
