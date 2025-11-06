import pandas as pd
from bs4 import BeautifulSoup
import re
import os

def clean_email_html(html):
    soup = BeautifulSoup(str(html), "html.parser")
    # Remove images, links, and style tags completely
    for tag in soup(['img', 'a', 'style']):
        tag.decompose()
    # Unwrap all other tags to keep their content only
    for tag in soup.find_all(True):
        if tag.name not in ['img', 'a', 'style']:
            tag.unwrap()
    text = soup.get_text(separator="\n")

    # =========== 强制移除所有<img ...>标签（如果还有残留） ===========
    text = re.sub(r'<img.*?>', '', text, flags=re.IGNORECASE)
    # =========== 强制移除所有base64图片字符串 ===========
    text = re.sub(r'data:image/[^;]+;base64,[^\s"\'>]+', '', text) 

    text = re.sub(r'https?://\S+', '', text)          # Remove URLs
    text = re.sub(r'-{5,}', '', text)                 # Remove repeated dashes
    text = re.sub(r'\|', '', text)                    # Remove pipe characters
    text = re.sub(r'\n\s*\n+', '\n', text)            # Remove multiple empty lines
    # Remove header-like info (Imported/Sent/From/To/CC lines)
    text = re.sub(r'(?i)Imported:.*\n?', '', text)
    text = re.sub(r'(?i)Sent:.*\n?', '', text)
    text = re.sub(r'(?i)MessageID:.*\n?', '', text)
    text = re.sub(r'(?i)From:.*\n?', '', text)
    text = re.sub(r'(?i)To:.*\n?', '', text)
    text = re.sub(r'(?i)CC:.*\n?', '', text)
    # Remove leftover HTML entities if any
    text = re.sub(r'&[a-z]+;', '', text)
    return text.strip()

# File path
INPUT_CSV = os.path.expanduser('~/ai_env/documents/AI_Training_Material/Ticket_Example/data.csv')
OUTPUT_CSV = 'data_cleaned.csv'
OUTPUT_XLSX = 'data_cleaned.xlsx'

# Read CSV
df = pd.read_csv(INPUT_CSV)

# Clean both columns (handling empty or NaN cases)
df['CleanIncoming'] = df['CleanIncoming'].fillna('').apply(clean_email_html)
df['CleanOutgoing'] = df['CleanOutgoing'].fillna('').apply(clean_email_html)

#df['CleanIncoming'] = df['IncomingAction'].fillna('').apply(clean_email_html)
#df['CleanOutgoing'] = df['OutgoingAction'].fillna('').apply(clean_email_html)

# Save to new Excel and CSV files for further use
df.to_excel(OUTPUT_XLSX, index=False)
df.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaning completed! Results saved to {OUTPUT_CSV} and {OUTPUT_XLSX}")
