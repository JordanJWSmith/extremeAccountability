from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
from email.mime.text import MIMEText

from generate_message import generate_shame_message
from helpers.db_helpers import get_email_recipients_from_db
from helpers.strava_helpers import get_access_token, get_today_activities


FROM_EMAIL = os.getenv('FROM_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ENV=os.getenv("ENV")

def send_shame_email():
    recipients = get_email_recipients_from_db()
    response_obj = generate_shame_message()
    msg_text = response_obj['body']
    msg_subject = response_obj['subject']

    for recipient in recipients:
        name = recipient['first_name']
        email = recipient['email']
        formatted_msg_text = msg_text.replace("{{friend}}", name)

        # print(f"sending {formatted_msg_text} to {name} at {email}")

        msg = MIMEText(formatted_msg_text, 'html')
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
