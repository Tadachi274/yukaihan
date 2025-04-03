import sqlite3

# データベースに接続
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# テーブル一覧を取得
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# 特定のテーブルの中身を取得
cursor.execute("SELECT * FROM players;")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 接続を閉じる
conn.close()
