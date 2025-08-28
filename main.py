from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
from email.mime.text import MIMEText

from helpers.generate_message import generate_shame_message
from helpers.db_helpers import get_email_recipients_from_db, get_active_status_from_db
from helpers.strava_helpers import get_access_token, get_today_activities, last_week_range_london, get_activities_in_range

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
                # server.send_message(msg)
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")


def main():
    active = get_active_status_from_db()
    if not active:
        print("User is inactive")
        return

    token = get_access_token()
    week_start, week_end = last_week_range_london()

    activities = get_activities_in_range(token, week_start, week_end)
    count = len(activities)
    print(f"Last week ({week_start.date()} to {week_end.date()}): {count} activities")

    if count < 10:
        # TODO: pass count/dates to the LLM to make the email extra spicy
        send_shame_email()
    else:
        print("Workouts complete. No shame required.")


if __name__ == "__main__":
    main()
