from dotenv import load_dotenv
load_dotenv()

import os
import time
import requests
import datetime
from zoneinfo import ZoneInfo

from helpers.db_helpers import get_creds_from_db, update_strava_tokens_in_db

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_API = 'https://www.strava.com/api/v3/athlete/activities'

def get_access_token():
    doc = get_creds_from_db()
    if not doc:
        raise Exception("Strava credentials not found in DB.")

    access_token = doc.get("access_token")
    expires_at = doc.get("access_token_expires_at", 0)
    refresh_token = doc.get("refresh_token")

    current_time = int(time.time())

    # If access token exists and hasn't expired, use it
    if access_token and current_time < expires_at:
        print("✅ Using cached access token.")
        return access_token

    # Otherwise, refresh the token
    print("🔄 Access token missing or expired. Refreshing...")

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    response.raise_for_status()
    token_data = response.json()

    new_access_token = token_data['access_token']
    new_refresh_token = token_data.get('refresh_token', refresh_token)
    expires_at = token_data['expires_at']  # UNIX timestamp

    # Save tokens back to DB
    update_strava_tokens_in_db(new_access_token, new_refresh_token, expires_at)

    print("✅ New access token saved to DB.")
    return new_access_token


def last_week_range_london(now: datetime.datetime | None = None):
    """Return previous week [Mon 00:00, Sun 23:59:59.999999] in Europe/London."""
    tz = ZoneInfo('Europe/London')
    now = now or datetime.datetime.now(tz)

    # Start of this week (Monday 00:00)
    this_monday = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    # Previous week range
    start = this_monday - datetime.timedelta(days=7)
    end = this_monday - datetime.timedelta(microseconds=1)
    return start, end


def get_activities_in_range(access_token: str, start_dt: datetime.datetime, end_dt: datetime.datetime):
    """Fetch all activities between start_dt and end_dt (inclusive), paging as needed."""
    after = int(start_dt.astimezone(datetime.timezone.utc).timestamp())
    before = int(end_dt.astimezone(datetime.timezone.utc).timestamp())

    headers = {'Authorization': f'Bearer {access_token}'}
    page = 1
    per_page = 200  # max per Strava API; reduces calls
    all_acts = []

    while True:
        resp = requests.get(
            STRAVA_API,
            headers=headers,
            params={'after': after, 'before': before, 'page': page, 'per_page': per_page},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        all_acts.extend(batch)
        if len(batch) < per_page:
            break
        page += 1

    return all_acts


def get_today_activities(access_token):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    after_epoch = int(today.timestamp())
    response = requests.get(
        STRAVA_API,
        headers={'Authorization': f'Bearer {access_token}'},
        params={'after': after_epoch}
    )
    response.raise_for_status()
    return response.json()