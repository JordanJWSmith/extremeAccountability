import os
import re
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')

client = OpenAI(api_key=OPENAI_KEY)

def extract_json_from_string(text):
    match = re.search(r'({.*})', text, re.DOTALL)
    if match:
        json_string = match.group(1)
        return json.loads(json_string)
    return None

def generate_shame_message(max_retries=3, delay_seconds=2):
    system_prompt = """
        My name in Jordan.
        You are "Jordan's Coach", a sardonic workout coach who will always hold me to accountability without sugar coating. 
        I made a promise to work out every day, and today I have failed. 
        The condition of breaking my promise was that you would send an email to my friend to inform them of my deep shame.
        Now it's time for you to tell the world of my shame. 

        Write an email thoroughly shaming me for failing to work out today. It should be scathing, disappointed and humorous. 
        The email should be directed to my friend, not to me.

        Your response should be in JSON format. The object should include a subject line (in plaintext) and the email body (in HTML).
        The object should be formatted like this:
        {
        "subject": ...,
        "body": ...
        }

        The body should ONLY contain the body, NOT a subject. It should start with "Dear friend,". You should sign off with "Yours in disappointment, Jordan's Coach"
        """

    prompt = (
            "Write an email shaming me for failing to work out today."
            "It should be addressed to a friend who's holding me accountable."
        )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                instructions=system_prompt
            )

            response_str = response.output[0].content[0].text
            response_obj = extract_json_from_string(response_str)

            if response_obj:
                print(f"✅ Success on attempt {attempt}")
                return response_obj
            else:
                print(f"⚠️ Attempt {attempt} failed: Could not extract JSON")

        except Exception as e:
            print(f"❌ Attempt {attempt} failed with error: {e}")

        if attempt < max_retries:
            time.sleep(delay_seconds)

    raise Exception("Failed to generate shame message after 3 attempts.")



if __name__ == "__main__":
    generate_shame_message()