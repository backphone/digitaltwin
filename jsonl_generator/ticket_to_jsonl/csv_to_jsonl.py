import pandas as pd
import json
import re

def extract_body(text):
    # If the first line looks like a subject/RE/FWD/ticket, skip it and return the rest as the body
    lines = text.strip().split('\n')
    if lines and any(k in lines[0].lower() for k in ['subject:', 're:', 'fwd:', 'bsubject:', 'ticket', 'case']):
        return '\n'.join(lines[1:]).strip()
    return text.strip()

def desensitize(text):
    # Replace email addresses with [EMAIL]
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)
    # Replace phone numbers with [PHONE]
    text = re.sub(r'(\+\d{1,3}[- ]?)?(\d{2,4}[- ]?)?\d{6,12}', '[PHONE]', text)
    # Keep ticket/case number for reference! (Do NOT replace ticket/case IDs)
    # Vessel names in signature block (Vessel Name: XXX, Ship: YYY, Call Sign: ZZZ)
    text = re.sub(r'^(Vessel Name|Ship|Call Sign|IMO No\.?)\s*[:：]?\s*[\w\- ]+\n?', r'\1: [VESSEL]\n', text, flags=re.I|re.M)
    # Generic English company name ending, e.g., "SK TELINK CORPORATION", "ABC SHIPPING LTD", etc.
    text = re.sub(
        r'\b([A-Z][A-Za-z0-9&,\.\- ]{2,}\s+(CORPORATION|LTD|LIMITED|CO\.|PTE LTD|INC|LLC|GMBH|SDN BHD|BV|AG|S\.A\.))\b',
        '[COMPANY]', text)
    # All uppercase vessel names (2 or more words, fallback rule)
    text = re.sub(r'\b([A-Z]{2,}(?:\s+[A-Z0-9\-]{2,}){1,})\b', '[VESSEL]', text)
    # Remove common email signature lines
    text = re.sub(
        r'^(Regards,|Best regards,|Kind regards,|Sincerely,|Yours truly,|Yours sincerely,|Respectfully,|Yours faithfully,|Thank you,|Cheers,).*\n?',
        '', text, flags=re.I|re.M)
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Main workflow
df = pd.read_csv('data_cleaned.csv')
with open('qa_pairs_bodyonly_desensitized.jsonl', 'w', encoding='utf-8') as f:
    for i, row in df.iterrows():
        # Extract only the email body for Q and A
        question = desensitize(extract_body(str(row['CleanIncoming'])))
        answer = desensitize(extract_body(str(row['CleanOutgoing'])))
        if not question or not answer:
            continue
        qa = {
            "question": question,
            "answer": answer
        }
        f.write(json.dumps(qa, ensure_ascii=False) + '\n')

print("Desensitized Q/A pairs (with ticket numbers kept) saved to qa_pairs_bodyonly_desensitized.jsonl")
