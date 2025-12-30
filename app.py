from flask import Flask, render_template, request, redirect, url_for, send_file
import json, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "tasks.json"

# ======= LOAD & SAVE =======

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ======= HOME + FILTER + SORT =======

@app.route("/")
def index():
    tasks = load_tasks()

    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    sort = request.args.get("sort", "")
    edit_index = request.args.get("edit")
    if priority == "thap":
        priority = "thấp"

    # filter trạng thái
    if status == "done":
        tasks = [t for t in tasks if t["done"]]
    elif status == "todo":
        tasks = [t for t in tasks if not t["done"]]

    # filter ưu tiên
    if priority in ["cao", "trung", "thấp"]:
        tasks = [t for t in tasks if t.get("priority") == priority]

    # sort theo ngày
    if sort == "date":
        def get_date(x):
            try:
                return datetime.strptime(x.get("due_date", "9999-12-31"), "%Y-%m-%d")
            except:
                return datetime(9999, 12, 31)
        tasks.sort(key=get_date)

    total = len(tasks)
    done = len([t for t in tasks if t["done"]])

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        done=done,
        q_status=status,
        q_priority=priority,
        q_sort=sort,
        edit_index=edit_index
    )


# ======= ADD TASK =======

@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text", "").strip()
    due_date = request.form.get("due_date", "").strip()
    priority = request.form.get("priority", "").strip()

    if text:
        tasks = load_tasks()
        tasks.append({
            "text": text,
            "done": False,
            "due_date": due_date,
            "priority": priority
        })
        save_tasks(tasks)

    return redirect(url_for("index"))


# ======= UPDATE (INLINE EDIT) =======

@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["text"] = request.form.get("text", "")
        tasks[index]["due_date"] = request.form.get("due_date", "")
        tasks[index]["priority"] = request.form.get("priority", "")
        save_tasks(tasks)
    return redirect(url_for("index"))


# ======= TOGGLE =======

@app.route("/toggle/<int:index>")
def toggle(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index]["done"]
        save_tasks(tasks)
    return redirect(url_for("index"))


# ======= DELETE =======

@app.route("/delete/<int:index>")
def delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect(url_for("index"))


# ======= EXPORT TXT =======

@app.route("/export_txt")
def export_txt():
    tasks = load_tasks()
    filename = "tasks_export.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("===== DANH SÁCH CÔNG VIỆC =====\n\n")
        for i, t in enumerate(tasks):
            f.write(f"ID: {i}\n")
            f.write(f"Công việc: {t['text']}\n")
            f.write(f"Hạn: {t.get('due_date','')}\n")
            f.write(f"Ưu tiên: {t.get('priority','')}\n")
            f.write(f"Trạng thái: {'Hoàn thành' if t['done'] else 'Chưa xong'}\n")
            f.write("-" * 40 + "\n")

    return send_file(filename, as_attachment=True)


# ======= RUN =======

if __name__ == "__main__":
    app.run(debug=True)
