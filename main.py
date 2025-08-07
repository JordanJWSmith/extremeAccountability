import os
import smtplib
import requests
import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText

from generate_message import generate_shame_message

# Load environment variables
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

FROM_EMAIL = os.getenv('FROM_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')

def get_access_token():
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': STRAVA_REFRESH_TOKEN
        }
    )
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data['access_token']
    new_refresh_token = token_data.get('refresh_token')

    # this won't work when deployed in github?
    if new_refresh_token and new_refresh_token != STRAVA_REFRESH_TOKEN:
        print("🔄 New refresh token received. Updating .env file...")
        update_env_file('STRAVA_REFRESH_TOKEN', new_refresh_token)

    return access_token

def update_env_file(key, value, env_path=".env"):
    # Load current .env content
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break

    if not key_found:
        lines.append(f"{key}={value}\n")

    with open(env_path, 'w') as f:
        f.writelines(lines)

    # Update in-memory environment for the current run
    os.environ[key] = value


def get_today_activities(access_token):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    after_epoch = int(today.timestamp())
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'after': after_epoch}
    )
    response.raise_for_status()
    return response.json()

def send_shame_email():
    response_obj = generate_shame_message()
    msg_text = response_obj['body']       # HTML body
    msg_subject = response_obj['subject'] # Plaintext subject

    msg = MIMEText(msg_text, 'html')  # Tell MIMEText this is HTML
    msg['Subject'] = msg_subject
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    token = get_access_token()
    activities = get_today_activities(token)
    if not activities:
        send_shame_email()
    else:
        print("Workout complete. No shame needed!")
        print(activities)

if __name__ == "__main__":
    main()
