import os
import re
import json

def load_and_clean_email(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Optional: remove headers or greetings if needed
    text = re.sub(r"(Subject:.*?)\n+", r"\1\n", text, flags=re.I)
    return text.strip()

def make_prompt(filename, body_text):
    subject = re.search(r"Subject:\s*(.*)", body_text)
    subject_line = subject.group(1).strip() if subject else "No subject"

    return f"Write a professional email response regarding the following topic:\nSubject: {subject_line}\nContext: ..."

def make_jsonl(input_folder, output_file):
    count = 0
    with open(output_file, "w", encoding="utf-8") as out:
        for fname in os.listdir(input_folder):
            if not fname.endswith(".txt"):
                continue
            path = os.path.join(input_folder, fname)
            body = load_and_clean_email(path)
            if len(body) < 50:
                continue  # skip short replies

            prompt = make_prompt(fname, body)
            record = {
                "prompt": prompt,
                "completion": body.strip()
            }
            out.write(json.dumps(record) + "\n")
            count += 1

    print(f"✅ Saved {count} fine-tuning samples to {output_file}")

# Run it
# make_jsonl("/home/ubuntu/redacted_emails", "/home/ubuntu/fine_tune_emails.jsonl")
make_jsonl("/home/ubuntu/original_emails_fulltext", "/home/ubuntu/fine_tune_emails_original.jsonl")

