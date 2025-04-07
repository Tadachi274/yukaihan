import sqlite3

# DB初期化
def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            role TEXT NOT NULL,

        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()