from flask import Flask, jsonify
from datetime import datetime
from tinydb import TinyDB, Query

app = Flask(__name__)
Entry = Query()
db = TinyDB('db/hw.json')

if db.search(Entry.LastUpdate.exists()):
    db.remove(Entry.LastUpdate.exists())
db.insert({'LastUpdate': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

def insert_homework():
    subject = SelectSubject()
    hw = input("請輸入功課名稱: ")
    due_date = input("請輸入功課截止日期 (YYYY-MM-DD): ")
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        print("日期格式錯誤，請使用 YYYY-MM-DD")
        return
    db.insert({'Subject': subject, 'Homework': hw, 'DueDate': due_date, 'CreatedAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

def SelectSubject():
    subjects = ["中文", "英文", "數學", "公社", "物理", "化學", "生物", "地理", "ICT","會計", "經濟", "西史", "中史", "中國文學", "M2", "CS", "其他"]
    print("請選擇科目:")
    for idx, subject in enumerate(subjects, 1):
        print(f"{idx}. {subject}")
    choice = input("請輸入科目編號: ")
    try:
        choice_idx = int(choice) - 1
        return subjects[choice_idx]
    except (ValueError, IndexError):
        print("無效選擇")
        SelectSubject()
   
def remove_homework():
    date = input("請輸入要查詢/編輯/刪除的功課日期 (YYYY-MM-DD): ")
    entries = db.search(Entry.DueDate == date)
    if not entries:
        print("沒有找到該日期的功課")
        return

    print("找到以下功課：")
    for idx, entry in enumerate(entries, 1):
        print(f"{idx}. Subject: {entry.get('Subject', '')}, Homework: {entry.get('Homework', '')}, DueDate: {entry.get('DueDate', '')}")

    choice = input("請輸入要編輯或刪除的編號 (或按 Enter 取消): ")
    if not choice:
        return

    try:
        choice_idx = int(choice) - 1
        selected_entry = entries[choice_idx]
    except (ValueError, IndexError):
        print("無效選擇")
        return

    action = input("輸入 'e' 編輯, 'd' 刪除: ").lower()
    if action == 'd':
        db.remove(doc_ids=[selected_entry.doc_id])
        print("已刪除該功課")
    elif action == 'e':
        new_subject = input(f"新Subject (原: {selected_entry.get('Subject', '')}): ") or selected_entry.get('Subject', '')
        new_homework = input(f"新Homework (原: {selected_entry.get('Homework', '')}): ") or selected_entry.get('Homework', '')
        new_due_date = input(f"新DueDate (原: {selected_entry.get('DueDate', '')}): ") or selected_entry.get('DueDate', '')
        db.update({'Subject': new_subject, 'Homework': new_homework, 'DueDate': new_due_date}, doc_ids=[selected_entry.doc_id])
        print("已更新該功課")
    else:
        print("操作取消")
#UI
main_menu = """
請選擇操作:
    1. 新增功課
    2. 編輯/刪除功課
    3. 離開
"""
def main():
    option = input(main_menu)
    match option:
        case '1':
            insert_homework()
        case '2':
            remove_homework()
        case '3':
            exit()
        case _:
            print("無效選項，請重新選擇")
            main()

while True:
	main()
