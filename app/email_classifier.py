import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_all_emails(emails):
    prompt = """
You are an intelligent email assistant. Below are several emails. For each email, carefully analyze the sender, subject, and body to determine its category. Follow these steps:

1. Check the sender: Is it from a known contact, an authority (e.g., CRA, landlord, employer), or a generic/marketing source?
2. Review the subject: Does it indicate urgency (e.g., "Urgent," "Notice") or promotional content (e.g., "Sale," "Offer")?
3. Read the body: Look for critical information (e.g., deadlines, personal messages, documents) or promotional content (e.g., ads, newsletters).
4. Think carefully: Consider all factors before deciding to ensure accurate classification.

Classify each email into one of these categories:
1. Very Important
2. Regular
3. Spam or Promotional

Return the results in this format, with only the category and no additional text or reasons:
Email 1: [Category]
Email 2: [Category]
...

Here are the emails:
"""

    for i, email in enumerate(emails):
        prompt += f"""

Email {i+1}:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body'][:1000]}
"""

    try:
        print("⏳ Waiting for ChatGPT response...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        content = response['choices'][0]['message']['content']
        lines = content.strip().split("\n")

        results = []
        for line in lines:
            if not line.startswith("Email"):
                continue
            parts = line.split(":", 1)[-1].strip()
            category = parts if parts else "Unknown"
            results.append({"category": category, "reason": "Not provided"})

        while len(results) < len(emails):
            results.append({"category": "Unknown", "reason": "Missing result"})

        return results

    except Exception as e:
        print("⚠️ Error in ChatGPT call:", str(e))
        return [{"category": "Error", "reason": str(e)} for _ in emails]