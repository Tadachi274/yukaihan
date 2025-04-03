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
    '新歓': 10
}

# オーダー表表示
@app.route('/')
def index():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    
    # プレイヤーリストを部署の順序でソート
    sorted_players = sorted(players, key=lambda x: DEPARTMENT_ORDER.get(x[2], 999))
    
    conn.close()
    return render_template('index.html', players=sorted_players)

# 選手追加ページ
@app.route('/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        role = request.form['role']  # 役の情報を取得
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO players (name, position, role) VALUES (?, ?, ?)', 
                      (name, position, role))  # roleを追加
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
    
    conn.close()
    return render_template('player_detail.html', player=player, player_data=player_data, motivation=motivation)


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
            print(f"{name}を更新しました")
        else:
            d.execute('''INSERT INTO busy_scores (name, 部署, 役者, 大学, 他団体, バイト, その他) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (data['name'], data['部署'], data['役者'], data['大学'], data['他団体'], data['バイト'], data['その他']))
            print(f"{name}を追加しました")
        conn.commit()
    return jsonify(data)

@app.route('/save_motivation', methods=['POST'])
def save_motivation():
    data = request.json
    with sqlite3.connect("data.db") as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO motivation (name, score) VALUES (?, ?)''',
                 (data['name'], data['motivation']))
        conn.commit()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)