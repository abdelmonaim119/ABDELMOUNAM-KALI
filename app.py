import base64
import json
import os
import time
from functools import wraps
from email.mime.text import MIMEText

from flask import Flask, jsonify, redirect, request, send_from_directory, session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-me-in-production')

OWNER_EMAIL = 'monaimabdel119@gmail.com'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/tasks',
]
CREDENTIALS_FILE = 'googleCredintails.json'
TOKEN_FILE = 'token.json'


def retry_api(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HttpError as error:
                    last_error = error
                    if attempt == max_retries - 1:
                        break
                    time.sleep(base_delay * (2 ** attempt))
            raise last_error

        return wrapper

    return decorator


def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r', encoding='utf-8') as token:
        data = json.load(token)
    return Credentials.from_authorized_user_info(data, SCOPES)


def save_credentials(credentials):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
        token.write(credentials.to_json())


@retry_api()
def send_admin_email(credentials, name, email, message):
    gmail_service = build('gmail', 'v1', credentials=credentials)
    content = f"New portfolio contact message\n\nFrom: {name} <{email}>\n\n{message}"
    mime_message = MIMEText(content)
    mime_message['to'] = OWNER_EMAIL
    mime_message['from'] = OWNER_EMAIL
    mime_message['subject'] = f'Portfolio contact from {name}'

    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    gmail_service.users().messages().send(
        userId='me', body={'raw': raw_message}
    ).execute()


@retry_api()
def create_followup_task(credentials, name, email, message):
    tasks_service = build('tasks', 'v1', credentials=credentials)
    task_lists = tasks_service.tasklists().list(maxResults=1).execute()
    items = task_lists.get('items', [])
    if not items:
        raise RuntimeError('No Google Tasks list available.')

    task_data = {
        'title': f'Follow up with {name}',
        'notes': f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
    }
    tasks_service.tasks().insert(tasklist=items[0]['id'], body=task_data).execute()


@app.route('/')
def serve_home():
    return send_from_directory('.', 'index.html')


@app.route('/<path:page>')
def serve_pages(page):
    allowed_pages = {'about.html', 'contact.html', 'admin.html', 'instructure.md', 'rules.md'}
    if page in allowed_pages:
        return send_from_directory('.', page)
    if page.startswith('projects/'):
        return send_from_directory('.', page)
    return jsonify({'error': 'Not found'}), 404


@app.route('/auth/login')
def auth_login():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=request.url_root.rstrip('/') + '/auth/callback',
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/auth/callback')
def auth_callback():
    state = session.get('oauth_state')
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.url_root.rstrip('/') + '/auth/callback',
    )

    authorization_response = request.url
    if request.headers.get('X-Forwarded-Proto') == 'https':
        authorization_response = authorization_response.replace('http://', 'https://', 1)

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    oauth2_service = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2_service.userinfo().get().execute()
    if user_info.get('email') != OWNER_EMAIL:
        return jsonify({'error': 'Unauthorized account. Only the project owner can authenticate. Others are view-only.'}), 403

    save_credentials(credentials)
    return redirect('/admin.html?auth=success')


@app.route('/api/status')
def api_status():
    return jsonify({'authenticated': os.path.exists(TOKEN_FILE), 'owner': OWNER_EMAIL, 'policy': 'owner-only changes; others view-only'})


@app.route('/api/contact', methods=['POST'])
def api_contact():
    payload = request.get_json(silent=True) or {}
    name = payload.get('name', '').strip()
    email = payload.get('email', '').strip()
    message = payload.get('message', '').strip()

    if not all([name, email, message]):
        return jsonify({'error': 'name, email and message are required'}), 400

    credentials = load_credentials()
    if not credentials:
        return jsonify({'error': 'Service unavailable: admin is not authenticated'}), 503

    try:
        send_admin_email(credentials, name, email, message)
        create_followup_task(credentials, name, email, message)
    except Exception as error:
        return jsonify({'error': f'Failed to process message: {error}'}), 500

    return jsonify({'success': True, 'message': 'Message sent successfully'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
