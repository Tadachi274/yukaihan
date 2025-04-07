from flask import Flask, render_template, request, jsonify,redirect,url_for
import sqlite3

app = Flask(__name__)

# 部署の順序を定義
DEPARTMENT_ORDER = {
    '演出': 0,
    '舞台監督': 1,
    '制作': 2,
    '音響': 3,
    '照明': 4,
    '道具': 5,
    '衣装': 6,
    '宣伝美術': 7,
    '広報': 8,
    '映像': 9,
    '新歓': 10,
    'その他': 11
}

# オーダー表表示
@app.route('/')
def index():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # プレイヤー基本情報の取得
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    
    # 各プレイヤーの忙しさとモチベーションデータを取得
    player_stats = {}
    for player in players:
        # 忙しさスコアの取得
        cursor.execute('''
            SELECT 部署, 役者, 大学, 他団体, バイト, その他 
            FROM busy_scores 
            WHERE name = ? 
            ORDER BY id DESC 
            LIMIT 1
        ''', (player[1],))
        busy_score = cursor.fetchone()
        
        # モチベーションスコアの取得
        cursor.execute('''
            SELECT score 
            FROM motivation 
            WHERE name = ? 
            ORDER BY id DESC 
            LIMIT 1
        ''', (player[1],))
        motivation_score = cursor.fetchone()
        
        # 平均忙しさを計算
        if busy_score:
            avg_busy = sum(busy_score) / len(busy_score)
        else:
            avg_busy = 0
            
        player_stats[player[1]] = {
            'busy_score': avg_busy,
            'motivation': motivation_score[0] if motivation_score else 50
        }
    
    # プレイヤーリストを部署の順序でソート
    sorted_players = sorted(players, key=lambda x: DEPARTMENT_ORDER.get(x[2], 999))
    
    conn.close()
    return render_template('index.html', players=sorted_players, player_stats=player_stats)

# 選手追加ページ
@app.route('/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        role = request.form['role']  
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO players (name, position, role) VALUES (?, ?, ?)', 
                      (name, position, role))  
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_player.html')

# 選手詳細ページ
@app.route('/player/<int:player_id>')
def player_detail(player_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # プレイヤー基本情報の取得
    cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
    player = cursor.fetchone()
    
    if not player:
        conn.close()
        return "選手が見つかりません", 404
    
    # busy_scoresテーブルから最新のデータを取得
    cursor.execute('''
        SELECT 部署, 役者, 大学, 他団体, バイト, その他 
        FROM busy_scores 
        WHERE name = ? 
        ORDER BY id DESC 
        LIMIT 1
    ''', (player[1],))  # player[1]は名前
    
    scores = cursor.fetchone()
    player_data = None
    if scores:
        player_data = {
            '部署': scores[0],
            '役者': scores[1],
            '大学': scores[2],
            '他団体': scores[3],
            'バイト': scores[4],
            'その他': scores[5]
        }
    
    # motivationテーブルから最新のスコアを取得
    cursor.execute('''
        SELECT score 
        FROM motivation 
        WHERE name = ? 
        ORDER BY id DESC 
        LIMIT 1
    ''', (player[1],))
    
    motivation_score = cursor.fetchone()
    motivation = motivation_score[0] if motivation_score else 50
    
    # タスクの取得
    cursor.execute('''
        SELECT id, position, task, done 
        FROM tasks 
        WHERE name = ?
        ORDER BY created_at DESC
    ''', (player[1],))
    tasks = cursor.fetchall()
    
    conn.close()
    return render_template('player_detail.html', 
                         player=player, 
                         player_data=player_data, 
                         motivation=motivation,
                         tasks=tasks)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    with sqlite3.connect("data.db") as conn:
        c = conn.cursor()
        name = data['name']
        c.execute('''SELECT EXISTS(SELECT name FROM busy_scores WHERE name = ?)''',(data['name'],))
        result = c.fetchone()[0]
        d = conn.cursor()
        if result == 1:
            d.execute('''UPDATE busy_scores SET 部署 = ?, 役者 = ?, 大学 =?, 他団体=?, バイト=?, その他=? WHERE name = ?''',(data['部署'], data['役者'], data['大学'], data['他団体'], data['バイト'], data['その他'],data['name']))
            print(f"{name}の忙しさを更新しました")
        else:
            d.execute('''INSERT INTO busy_scores (name, 部署, 役者, 大学, 他団体, バイト, その他) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (data['name'], data['部署'], data['役者'], data['大学'], data['他団体'], data['バイト'], data['その他']))
            print(f"{name}の忙しさ追加しました")
        conn.commit()
    return jsonify(data)

@app.route('/save_motivation', methods=['POST'])
def save_motivation():
    data = request.json
    with sqlite3.connect("data.db") as conn:
        c = conn.cursor()
        name = data['name']
        c.execute('''SELECT EXISTS(SELECT name FROM motivation WHERE name = ?)''',(data['name'],))
        result = c.fetchone()[0]
        d = conn.cursor()
        if result == 1:
            d.execute('''UPDATE motivation SET score = ? WHERE name = ?''',(data['motivation'], data['name'],))
            print(f"{name}のモチベーションを更新しました")
        else:
            d.execute('''INSERT INTO motivation (name, score) VALUES (?, ?)''',(data['name'], data['motivation']))
            print(f"{name}のモチベーションを追加しました")
        conn.commit()
    return jsonify({"success": True})

@app.route('/save_task', methods=['POST'])
def save_task():
    data = request.json
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (name, position, task) 
            VALUES (?, ?, ?)
        ''', (data['name'], data['position'], data['task']))
        conn.commit()
    return jsonify({"success": True})

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET done = NOT done WHERE id = ?', (task_id,))
        conn.commit()
    return jsonify({"success": True})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
    return jsonify({"success": True})

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        # プレイヤーの名前を取得
        cursor.execute('SELECT name FROM players WHERE id = ?', (player_id,))
        player_name = cursor.fetchone()[0]
        
        # 関連するデータを削除
        cursor.execute('DELETE FROM busy_scores WHERE name = ?', (player_name,))
        cursor.execute('DELETE FROM motivation WHERE name = ?', (player_name,))
        cursor.execute('DELETE FROM tasks WHERE name = ?', (player_name,))
        cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))
        conn.commit()
    return jsonify({"success": True})

@app.route('/edit_player/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        role = request.form['role']
        
        cursor.execute('''
            UPDATE players 
            SET name = ?, position = ?, role = ? 
            WHERE id = ?
        ''', (name, position, role, player_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
    player = cursor.fetchone()
    conn.close()
    
    if player is None:
        return "選手が見つかりません", 404
        
    return render_template('edit_player.html', player=player)

if __name__ == '__main__':
    app.run(debug=True)