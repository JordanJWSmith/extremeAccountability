from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
from email.mime.text import MIMEText

from generate_message import generate_shame_message
from db_helpers import get_email_recipients_from_db
from strava_helpers import get_access_token, get_today_activities


FROM_EMAIL = os.getenv('FROM_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')


def send_shame_email():
    recipients = get_email_recipients_from_db()
    response_obj = generate_shame_message()
    msg_text = response_obj['body']
    msg_subject = response_obj['subject']

    for email in recipients:
        msg = MIMEText(msg_text, 'html')
        msg['Subject'] = msg_subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(FROM_EMAIL, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")


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
