from flask import Flask, redirect, url_for, session, jsonify, send_from_directory, request
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
import json
import requests
from pymongo import MongoClient
from flask_cors import CORS

static_path = os.getenv('STATIC_PATH','static')
template_path = os.getenv('TEMPLATE_PATH','templates')
app = Flask(__name__, static_folder=static_path, template_folder=template_path)

client_secret = os.getenv('CLIENT_SECRET')
client_id = os.getenv("CLIENT_ID")

app.secret_key = os.urandom(24)

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
)

oauth = OAuth(app)

nonce = generate_token()

oauth.register(
    name='dex',
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    # DON'T use server_metadata_url - it returns localhost URLs
    # server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    
    # Manually specify endpoints with 'dex' hostname for container-to-container
    authorization_endpoint='http://localhost:5556/auth',  # Browser-accessible
    token_endpoint='http://dex:5556/token',               # Backend-to-Dex
    userinfo_endpoint='http://dex:5556/userinfo',         # Backend-to-Dex
    jwks_uri='http://dex:5556/keys',                      # Backend-to-Dex
    client_kwargs={'scope': 'openid email profile'}
)
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])


# google = oauth.register(
#     name='google',
#     client_id=client_id,
#     client_secret=client_secret,
#     access_token_url='https://oauth2.googleapis.com/token',
#     access_token_params=None,
#     authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
#     authorize_params=None,
#     userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#     client_kwargs={'scope': 'openid email profile'},
# )

# Mongo connection
mongo_uri = os.getenv("MONGO_URI")
mongo = MongoClient(mongo_uri)
db = mongo.get_database()

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path,path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

# @app.route('/home')
# def home():
#     user = session.get('user')
#     if user:
#         return f"<h2>Logged in as {user['email']}</h2><a href='http://localhost:8000/logout'>Logout</a>"
#     return '<a href="http://localhost:8000/login" id="login">Login with Dex</a>'

# @app.route('/login')
# def login():
#     session['nonce'] = nonce
#     redirect_uri = 'http://localhost:8000/authorize'
#     return oauth.flask_app.authorize_redirect(redirect_uri, nonce=nonce)

# @app.route('/authorize')
# def authorize():
#     token = oauth.flask_app.authorize_access_token()
#     nonce = session.get('nonce')

#     user_info = oauth.flask_app.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
#     session['user'] = user_info
#     session['user_type'] = user_info['name']
#     return redirect('http://localhost:5173')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return jsonify({"message": "Logged out"}), 200

@app.route('/api/me')
def get_current_user():
    user = session.get('user')
    if user:
        return jsonify(user)
    return jsonify({"error": "Not logged in"}), 401

# @app.route('/login')
# def login():
#     redirect_uri = url_for('auth', _external=True)
#     session['nonce'] = nonce
#     return google.authorize_redirect(redirect_uri, nonce=nonce)

# @app.route('/auth')
# def auth():
#     token = google.authorize_access_token()
#     nonce = session.get('nonce')
#     user_info = google.parse_id_token(token, nonce=nonce)
#     session['user'] = user_info
#     return redirect('http://localhost:5173/')

# @app.route('/logout')
# def logout():
#     # session.pop('user', None)
#     session.clear()
#     return redirect('http://localhost:5173')
#-----
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    session['nonce'] = nonce
    return oauth.dex.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/auth')
def auth():
    token = oauth.dex.authorize_access_token()
    nonce = session.get('nonce')
    user_info = oauth.dex.parse_id_token(token, nonce=nonce)
    session['user'] = user_info
    session['user_type'] = user_info.get('name', user_info.get('email'))
    return redirect('http://localhost:5173/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('http://localhost:5173')
#-----

@app.route("/is_signed_in")
def is_signed_in():
    if 'user' in session:
        return jsonify({"signed_in": True})
    return jsonify({"signed_in": False})

@app.route("/get_user_type")
def get_user_type():
    if 'user' in session:
        return jsonify({"user_type": session.get("user_type")})
    return jsonify({"error": "not signed in"})

@app.route("/test-mongo")
def test_mongo():
    return jsonify({"collections": db.list_collection_names()})

def convert_objectid(doc):
    doc['_id'] = str(doc['_id'])
    return doc

def normalize_quotes(s):
    return s.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')

def find_user(user_id):
    comments_cursor = db.notes.find({"ID": user_id})
    return [convert_objectid(doc) for doc in comments_cursor]

@app.route("/get_notes/<user_id>", methods=["GET"])
def get_notes(user_id):
    user = find_user(user_id)
    if len(user) == 0:
        return jsonify({"notes": {}})
    else:
        notes = user[0]["notes"]
        return jsonify({"notes": notes})

@app.route("/get_tasks/<user_id>", methods=["GET"])
def get_tasks(user_id):
    user = find_user(user_id)
    if len(user) == 0:
        return jsonify({"tasks": {}})
    else:
        tasks = user[0]['tasks']
        return jsonify({"tasks": tasks})
    
@app.route("/get_teams/<user_id>", methods=["GET"])
def get_teams(user_id):
    user = find_user(user_id)
    if len(user) == 0:
        return jsonify({"teams": {}})
    else:
        teams = user[0]['teams']
        return jsonify({"teams": teams})

@app.route("/create_note", methods=["POST"])
def create_note():
    request_dictionary = request.get_json()
    user_id = request_dictionary['user_id']
    note = str(request_dictionary['note'])
    title = str(request_dictionary['note_title'])
    user = find_user(user_id)
    if len(user) == 0:
        db.notes.insert_one({"ID": user_id, "notes": {}, "tasks": {}, "teams": {}})
        db.notes.update_one({"ID": user_id}, {"$set": {f"notes.{title}": note}})
    else:
        db.notes.update_one({"ID": user_id}, {"$set": {f"notes.{title}": note}})
    return jsonify({"success": "note added successfully"})

@app.route("/create_task", methods=["POST"])
def create_task():
    request_dictionary = request.get_json()
    user_id = request_dictionary['user_id']
    task_name = request_dictionary['task_name']
    task_description = request_dictionary['task_description']
    task_location = request_dictionary['task_location']
    task_color = request_dictionary['task_color']
    task_label = request_dictionary['task_label']
    task_start_time = request_dictionary['task_start_time']
    task_end_time = request_dictionary['task_end_time']
    task_date = request_dictionary['task_date']
    task_tags = request_dictionary['task_tags']
    task_priority = request_dictionary['task_priority']
    user = find_user(user_id)
    if len(user) == 0:
        db.notes.insert_one({"ID": user_id, "tasks": {}, "notes": {}, "teams": {}})
        db.notes.update_one({"ID": user_id}, {"$set": {f"tasks.{task_name}": {"task_description": task_description, "task_location": task_location, "task_color": task_color, "task_label": task_label, "task_start_time": task_start_time, "task_end_time": task_end_time, "task_date": task_date, "task_tags": task_tags, "task_priority": task_priority}}})
    else:
        db.notes.update_one({"ID": user_id}, {"$set": {f"tasks.{task_name}": {"task_description": task_description, "task_location": task_location, "task_color": task_color, "task_label": task_label, "task_start_time": task_start_time, "task_end_time": task_end_time, "task_date": task_date, "task_tags": task_tags, "task_priority": task_priority}}})
    return jsonify({"success": "event created successfully"})

@app.route("/create_team_task", methods=["POST"])
def create_team_task():
    request_dictionary = request.get_json()
    user_id = request_dictionary['user_id']
    task_name = request_dictionary['task_name']
    task_description = request_dictionary['task_description']
    task_team = request_dictionary['task_team']
    task_assignees = request_dictionary['task_assignees']
    task_priority = request_dictionary['task_priority']
    task_due_date = request_dictionary['task_due_date']
    user = find_user(user_id)
    if len(user) == 0:
        db.notes.insert_one({"ID": user_id, "tasks": {}, "notes": {}, "teams": {}})
        db.notes.update_one({"ID": user_id}, {"$set": {f"teams.{task_team}": {task_name: {"task_description": task_description, "task_assignees": task_assignees, "task_priority": task_priority, "task_due_date": task_due_date}}}})
    else:
        db.notes.update_one({"ID": user_id}, {"$set": {f"teams.{task_team}": {task_name: {"task_description": task_description, "task_assignees": task_assignees, "task_priority": task_priority, "task_due_date": task_due_date}}}})
    return jsonify({"success": "team task created successfully"})

@app.route("/delete_note", methods=["POST"])
def delete_note():
    request_dictionary = request.get_json()
    note_title = request_dictionary['note_title']
    user_id = request_dictionary['user_id']
    db.notes.update_one({"ID": user_id}, {"$unset": {f"notes.{note_title}": 1}})
    return jsonify({"success": "note deleted successfully"})

@app.route("/delete_task", methods=["POST"])
def delete_task():
    request_dictionary = request.get_json()
    task_title = request_dictionary['task_title']
    user_id = request_dictionary['user_id']
    db.notes.update_one({"ID": user_id}, {"$unset": {f"tasks.{task_title}": 1}})
    return jsonify({"success": "task deleted successfully"})

@app.route("/delete_team_task", methods=["POST"])
def delete_team_task():
    request_dictionary = request.get_json()
    team = request_dictionary['team']
    task_name = request_dictionary['task_name']
    user_id = request_dictionary['user_id']
    db.notes.update_one({"ID": user_id}, {"$unset": {f"teams.{team}.{task_name}": 1}})
    return jsonify({"success": "team task deleted successfully"})

@app.route("/update_task_status", methods=["POST"])
def update_task_status():
    """Update the status of a task (task, in-progress, completed)"""
    request_dictionary = request.get_json()
    user_id = request_dictionary['user_id']
    task_name = request_dictionary['task_name']
    new_status = request_dictionary['new_status']
    
    user = find_user(user_id)
    
    if len(user) == 0:
        return jsonify({"error": "User not found"}), 404
    
    db.notes.update_one(
        {"ID": user_id}, 
        {"$set": {f"tasks.{task_name}.task_status": new_status}}
    )
    
    return jsonify({"success": "task status updated successfully", "new_status": new_status})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
