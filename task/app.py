from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# データベース接続関数
def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row  # 結果を辞書形式で取得
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        task = request.form.get("task")
        if task:
            cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            conn.commit()

    # タスク一覧を取得
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    
    conn.close()
    return render_template("index.html", tasks=tasks)

# タスク削除のルート
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))  # 削除後、トップページへリダイレクト

if __name__ == "__main__":
    app.run(debug=True)
