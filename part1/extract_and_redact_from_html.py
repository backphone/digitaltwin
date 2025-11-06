import os
import re
from bs4 import BeautifulSoup

def redact(text):
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b", "[REDACTED_NAME]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3,4}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
    return text

def extract_from_html(msg_folder, output_file):
    html_path = os.path.join(msg_folder, "Message.html")
    if not os.path.exists(html_path):
        return False

    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        redacted = redact(text)

        with open(output_file, "w", encoding="utf-8") as out:
            out.write(redacted)
        return True
    except Exception as e:
        print(f"Error processing {msg_folder}: {e}")
        return False

def walk_and_extract(base_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    count = 0
    for root, dirs, files in os.walk(base_path):
        if "Message.html" in files:
            msg_id = os.path.basename(root)
            output_file = os.path.join(output_folder, f"{msg_id}.txt")
            if extract_from_html(root, output_file):
                count += 1
    print(f"✅ Extracted and redacted {count} emails.")

# Run it:
walk_and_extract(
    "/home/ubuntu/libpff/extracted_emails.export/Top of Outlook data file/Sent Items",
    "/home/ubuntu/redacted_emails"
)
