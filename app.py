from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 🌟 請執行 pip install flask-cors
import datetime

app = Flask(__name__)
CORS(app)  # 🌟 讓 React 能夠跨網域呼叫 API

# 1. 資料庫設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_6rVtxG4oBcfE@ep-autumn-glade-a1dw4ll8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(50))

with app.app_context():
    db.create_all()

# --- 新增：給 React 使用的 JSON 數據接口 ---

@app.route('/api/messages', methods=['GET'])
def get_messages():
    # 抓取最新留言
    msgs = Message.query.order_by(Message.id.desc()).all()
    return jsonify([{
        'id': m.id,
        'nickname': m.nickname,
        'content': m.content,
        'time': m.time
    } for m in msgs])

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if data.get('nickname') and data.get('content'):
        new_msg = Message(nickname=data['nickname'], content=data['content'], time=now)
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'fail'}), 400

# --- 你原本的功能 (保留) ---

@app.route('/api/message_count')
def message_count():
    count = Message.query.count()
    return jsonify({'count': count})

@app.route('/clear_all_messages_midnight')
def clear_messages():
    user_pwd = request.args.get('pwd')
    if user_pwd == 'admin123':
        try:
            db.session.query(Message).delete()
            db.session.commit()
            return "SUCCESS: 留言板已清空", 200
        except Exception as e:
            db.session.rollback()
            return f"ERROR: {str(e)}", 500
    return "DENIED", 403

if __name__ == '__main__':
    app.run(debug=True, port=5000)