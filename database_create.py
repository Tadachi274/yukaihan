import sqlite3

# データベースに接続
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 既存のテーブルを削除
cursor.execute("DROP TABLE IF EXISTS players")

# 新しいテーブルを作成
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        position TEXT,
                        role TEXT
                    )''')

# 変更を保存
conn.commit()

# 接続を閉じる
conn.close()
