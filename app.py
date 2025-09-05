from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# 仮のデータベース（メモリ上）
schedules = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedules', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_schedules():
    if request.method == 'POST':
        data = request.json
        title = data.get('title')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            if date_str not in schedules:
                schedules[date_str] = []
            
            schedules[date_str].append({
                'title': title,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'start_time': start_time,
                'end_time': end_time,
                'completed': False
            })
            current_date += timedelta(days=1)
        
        return jsonify(success=True)
    
    elif request.method == 'PUT':
        data = request.json
        old_title = data.get('old_title')
        new_title = data.get('new_title')
        old_start_date_str = data.get('old_start_date')
        old_end_date_str = data.get('old_end_date')
        old_start_time = data.get('old_start_time')
        
        new_start_date_str = data.get('new_start_date')
        new_end_date_str = data.get('new_end_date')
        new_start_time = data.get('new_start_time')
        new_end_time = data.get('new_end_time')

        # 古い予定を削除
        start_date_to_remove = datetime.strptime(old_start_date_str, '%Y-%m-%d')
        end_date_to_remove = datetime.strptime(old_end_date_str, '%Y-%m-%d')
        current_date = start_date_to_remove
        while current_date <= end_date_to_remove:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in schedules:
                schedules[date_str] = [s for s in schedules[date_str] if not (s['title'] == old_title and s['start_time'] == old_start_time)]
            current_date += timedelta(days=1)

        # 新しい予定を追加
        new_start_date = datetime.strptime(new_start_date_str, '%Y-%m-%d')
        new_end_date = datetime.strptime(new_end_date_str, '%Y-%m-%d')
        current_date = new_start_date
        while current_date <= new_end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in schedules:
                schedules[date_str] = []
            
            schedules[date_str].append({
                'title': new_title,
                'start_date': new_start_date_str,
                'end_date': new_end_date_str,
                'start_time': new_start_time,
                'end_time': new_end_time,
                'completed': False
            })
            current_date += timedelta(days=1)

        return jsonify(success=True)

    elif request.method == 'DELETE':
        data = request.json
        title = data.get('title')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        start_time = data.get('start_time')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in schedules:
                schedules[date_str] = [s for s in schedules[date_str] if not (s['title'] == title and s['start_time'] == start_time)]
            current_date += timedelta(days=1)
        
        return jsonify(success=True)

    return jsonify(schedules)

@app.route('/complete_schedule', methods=['POST'])
def complete_schedule():
    data = request.json
    date_str = data.get('date')
    title = data.get('title')
    start_time = data.get('start_time')
    
    found = False
    if date_str in schedules:
        for schedule in schedules[date_str]:
            if schedule['title'] == title and schedule['start_time'] == start_time:
                schedule['completed'] = not schedule['completed']
                found = True
                break
    
    if found:
        # 複数日にまたがる予定の完了状態を同期
        start_date_str = [s['start_date'] for s in schedules[date_str] if s['title'] == title and s['start_time'] == start_time][0]
        end_date_str = [s['end_date'] for s in schedules[date_str] if s['title'] == title and s['start_time'] == start_time][0]
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        current_date = start_date
        while current_date <= end_date:
            sync_date_str = current_date.strftime('%Y-%m-%d')
            if sync_date_str in schedules:
                for s in schedules[sync_date_str]:
                    if s['title'] == title and s['start_time'] == start_time:
                        s['completed'] = not s['completed']
            current_date += timedelta(days=1)
        
        return jsonify(success=True)
    
    return jsonify(success=False, message="Schedule not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
