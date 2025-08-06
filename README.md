# Extreme Accountability

**If I don't log an activity in Strava by the end of the day, this bot will send an email to my friends to inform them of my shame.**

The script uses the Strava API to retrieve user data, then sends an email via SMTP server with the user's credentials. 
The script can be scheduled using Github Actions with a cron job. 

It's currently a naive implementation.  It requires an `.env` file with the following parameters:
```
STRAVA_CLIENT_ID = 'your_client_id'
STRAVA_CLIENT_SECRET = 'your_client_secret'
STRAVA_REFRESH_TOKEN = 'your_refresh_token'
TO_EMAIL = 'accountability@friend.com'
FROM_EMAIL = 'your_email@example.com'
EMAIL_PASSWORD = 'your_email_password'
OPENAI_KEY='sk-proj-abc...'
```

The current functionality could probably be achieved using Zapier instead, but I'd like to keep iterating until it's (ideally) packaged as an app. Future iterations will include:
- A frontend with a dashboard 
- Strava and GMail OAuth logins
- Integrating new sources of shame (e.g. Duolingo)


## Roadmap

Milestone 1: MVP
1. Hardcoded email
2. LLM-generated email
3. Emails keep getting worse the longer the dry spell gets

Milestone 2: Frontend
1. Set up DB
2. Frontend with dashboard and email input
3. Display streak, history
4. Shareable QR code to add yourself to the mailing list
5. Package as app

Milestone 3: Multithread
1. Allow user to input Strava credentials
2. Allow user to input openAI creds
3. Allow user to input email creds
4. Allow user to launch the scheduler

Milestone 4: Prod
1. Log in with Strava via OAuth
2. Log in with email OAuth
3. Option to log in with openAI via OAuth
4. Optimised UX

Milestone 5: Beyond
1. Integrate new tasks (Duolingo? Goodreads? Common productivity apps?)
