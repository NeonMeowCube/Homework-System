from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from datetime import datetime
from tinydb import TinyDB, Query
from icalendar import Calendar
from datetime import datetime, timedelta
import os

os.environ["FLASK_ENV"] = "production"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
Entry = Query()
db = TinyDB('db/hw.json')

# 設定 API Key
API_KEY = "your-secure-api-key"  # 請替換為你的安全 API Key

def verify_api_key(): ##API verify function not yet done
    """驗證請求中的 API Key"""
    #key = request.headers.get("X-API-Key")
    #if key != API_KEY:
    #    return jsonify({"error": "未授權的請求"}), 403
    return None

@app.route('/items/<string:date>', methods=['GET'])
def get_item(date):
    # 移除 API Key 驗證
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "日期格式錯誤，請使用 YYYY-MM-DD"}), 400
    results = db.search(Entry.DueDate == date)
    return jsonify(results), 200

@app.route('/items/all', methods=['GET'])
def get_all_items():
    # 移除 API Key 驗證
    all_data = db.all()
    return jsonify(all_data), 200

# 新增功課的路由
@app.route('/items/add', methods=['POST'])
def add_homework():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    required_fields = ["Subject", "Homework", "DueDate", "CreatedAt"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "缺少必要欄位"}), 400

    try:
        datetime.strptime(data["DueDate"], "%Y-%m-%d")  # 驗證日期格式
    except ValueError:
        return jsonify({"error": "日期格式錯誤，請使用 YYYY-MM-DD"}), 400

    db.insert(data)
    return jsonify({"status": "success", "message": "功課已新增"}), 200

# 編輯功課的路由
@app.route('/items/<int:item_id>', methods=['PUT'])
def edit_homework(item_id):
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    if not data:
        return jsonify({"error": "請提供更新的資料"}), 400

    try:
        if "DueDate" in data:
            datetime.strptime(data["DueDate"], "%Y-%m-%d")  # 驗證日期格式
    except ValueError:
        return jsonify({"error": "日期格式錯誤，請使用 YYYY-MM-DD"}), 400

    updated = db.update(data, doc_ids=[item_id])
    if updated:
        return jsonify({"status": "success", "message": "功課已更新"}), 200
    else:
        return jsonify({"error": "找不到指定的功課"}), 404

# 刪除功課的路由
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_homework(item_id):
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    deleted = db.remove(doc_ids=[item_id])
    if deleted:
        return jsonify({"status": "success", "message": "功課已刪除"}), 200
    else:
        return jsonify({"error": "找不到指定的功課"}), 404

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
