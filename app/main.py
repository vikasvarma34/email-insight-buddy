from app.email_reader import get_latest_emails
from app.email_classifier import classify_all_emails
from datetime import datetime


def run():
    print("\n📬 Checking for new unread emails from the last 24 hours...\n")
    emails = get_latest_emails(max_results=10)

    if not emails:
        print("✅ No new unread emails in the last 24 hours.")
        return

    print("🤖 Asking ChatGPT to classify all emails at once...")
    results = classify_all_emails(emails)

    stats = {"very important": 0, "regular": 0, "spam": 0, "error": 0}

    for i, (email, result) in enumerate(zip(emails, results)):
        print(f"\n--- Email {i + 1} ---")
        print("From:", email['from'])
        print("Subject:", email['subject'])
        print("Body (trimmed):", email['body'][:300], "...")
        print("➡️ Classification:", result['category'])
        print("🧠 Reason:", result['reason'])

        category = result['category'].strip().lower()
        if "very important" in category:
            stats["very important"] += 1
            print("⭐ Starring important email...")
            email['service'].users().messages().modify(
                userId='me',
                id=email['id'],
                body={"addLabelIds": ["STARRED"]}
            ).execute()
            print("✅ Starred successfully.")
        elif "regular" in category:
            stats["regular"] += 1
        elif "spam" in category or "promotional" in category:
            stats["spam"] += 1
            print("📦 Archiving and marking spam as read...")
            if 'id' in email:
                email['service'].users().messages().modify(
                    userId='me',
                    id=email['id'],
                    body={"removeLabelIds": ["INBOX", "UNREAD"]}
                ).execute()
                print("✅ Archived and marked as read successfully.")
        else:
            stats["error"] += 1

    print("\n📊 Summary:")
    for key, value in stats.items():
        print(f"{key.title()}: {value}")

    print("\n✅ Done at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    run()