from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

# --- SQLite 設定 ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedules.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- モデル ---
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)  # 'YYYY-MM-DD'
    end_date = db.Column(db.String(10), nullable=False)    # 'YYYY-MM-DD'
    start_time = db.Column(db.String(5), nullable=False)   # 'HH:MM'
    end_time = db.Column(db.String(5), nullable=False)     # 'HH:MM'
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "title": self.title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "completed": self.completed,
        }

# --- ユーティリティ ---
def date_range(start_date_str: str, end_date_str: str):
    """'YYYY-MM-DD' 文字列の範囲を date オブジェクトで順に返す"""
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

# --- 初期画面 ---
@app.route("/")
def index():
    # DBテーブル作成（初回のみ）
    db.create_all()
    return render_template("index.html")

# --- 予定CRUD ---
@app.route("/schedules", methods=["GET", "POST", "PUT", "DELETE"])
def handle_schedules():
    if request.method == "POST":
        data = request.json
        item = Schedule(
            title=data.get("title", "").strip(),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            completed=False,
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(success=True)

    elif request.method == "PUT":
        data = request.json
        # 旧情報でレコードを1件特定
        target = (
            Schedule.query.filter_by(
                title=data.get("old_title"),
                start_date=data.get("old_start_date"),
                end_date=data.get("old_end_date"),
                start_time=data.get("old_start_time"),
            )
            .order_by(Schedule.id.asc())
            .first()
        )
        if not target:
            return jsonify(success=False, message="Schedule not found"), 404

        # 更新（既仕様：completed は維持したまま）
        target.title = data.get("new_title", target.title).strip()
        target.start_date = data.get("new_start_date", target.start_date)
        target.end_date = data.get("new_end_date", target.end_date)
        target.start_time = data.get("new_start_time", target.start_time)
        target.end_time = data.get("new_end_time", target.end_time)
        db.session.commit()
        return jsonify(success=True)

    elif request.method == "DELETE":
        data = request.json
        target = (
            Schedule.query.filter_by(
                title=data.get("title"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                start_time=data.get("start_time"),
            )
            .order_by(Schedule.id.asc())
            .first()
        )
        if not target:
            return jsonify(success=False, message="Schedule not found"), 404

        db.session.delete(target)
        db.session.commit()
        return jsonify(success=True)

    # --- GET: フロント互換の形 {date: [予定, ...]} に展開して返す ---
    out = {}
    for sched in Schedule.query.all():
        for d in date_range(sched.start_date, sched.end_date):
            key = d.strftime("%Y-%m-%d")
            out.setdefault(key, []).append(sched.to_dict())
    return jsonify(out)

# --- 完了トグル ---
@app.route("/complete_schedule", methods=["POST"])
def complete_schedule():
    data = request.json
    date_str = data.get("date")         # クリックされた日（範囲内かの目安）
    title = data.get("title")
    start_time = data.get("start_time")

    # 範囲内に date_str を含み、title & start_time が一致する1件を探す
    candidates = Schedule.query.filter_by(title=title, start_time=start_time).all()
    target = None
    for s in candidates:
        if s.start_date <= date_str <= s.end_date:
            target = s
            break

    if not target:
        return jsonify(success=False, message="Schedule not found"), 404

    # 1件だけトグル → 表示時に全日へ反映（展開表示方式）
    target.completed = not target.completed
    db.session.commit()
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
