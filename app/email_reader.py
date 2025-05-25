import os
import base64
import re
import pickle
import datetime
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def authenticate_gmail(email_id):
    CREDENTIALS_FILE = os.getenv(f"GOOGLE_OAUTH_FILE_{email_id}")
    TOKEN_FILE = f'secrets/token_{email_id}.pickle'

    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_latest_emails(email_id, max_results=5):
    try:
        service = authenticate_gmail(email_id)

        query = 'is:unread newer_than:1d'
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            snippet = msg_data.get('snippet', '')

            body_data = ''
            if 'parts' in msg_data['payload']:
                for part in msg_data['payload']['parts']:
                    if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                        body_data = part['body']['data']
                        break
            elif 'data' in msg_data['payload']['body']:
                body_data = msg_data['payload']['body']['data']

            if body_data:
                decoded_body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8', errors='ignore')
                body = clean_text(decoded_body)
            else:
                body = clean_text(snippet)

            emails.append({
                'from': sender,
                'subject': subject,
                'body': body,
                'id': msg['id'],
                'service': service,
                'email_id': email_id
            })

        return emails

    except Exception as e:
        print(f"⚠️ Error fetching emails for {email_id}:", str(e))
        return []