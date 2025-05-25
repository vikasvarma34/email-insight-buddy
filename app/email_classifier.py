import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_all_emails(emails):
    prompt = """
You are an intelligent email assistant. Below are several emails. For each email, classify it into one of the following categories:

1. Very Important
2. Regular
3. Spam or Promotional

Return the results in this format:
Email 1: [Category] - [One-line Reason]
Email 2: [Category] - [One-line Reason]
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
            max_tokens=1000
        )

        content = response['choices'][0]['message']['content']
        lines = content.strip().split("\n")

        results = []
        for line in lines:
            if not line.startswith("Email"):
                continue
            parts = line.split(":", 1)[-1].strip().split("-", 1)
            category = parts[0].strip() if len(parts) > 0 else "Unknown"
            reason = parts[1].strip() if len(parts) > 1 else "No reason given"
            results.append({"category": category, "reason": reason})

        while len(results) < len(emails):
            results.append({"category": "Unknown", "reason": "Missing result"})

        return results

    except Exception as e:
        print("⚠️ Error in ChatGPT call:", str(e))
        return [{"category": "Error", "reason": str(e)} for _ in emails]
