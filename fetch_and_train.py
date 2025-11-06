import os
import requests
import subprocess
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

TXT_DIR = '/home/ubuntu/ai_env/documents/txt/'
PDF_DIR = '/home/ubuntu/ai_env/documents/AI Training Material/'
LOG_FILE = '/home/ubuntu/ai_env/logs/auto_training_log.txt'
CHUNK_THRESHOLD = 100000
DEFAULT_CHUNK_SIZE = 1000
MAX_PDF_DOWNLOAD = 10
BASE_URL = 'https://intelliantech.com'

os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

crawled_urls = set()
pdf_downloaded = 0

def fetch_web_content(url):
    try:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.extract()
        text = soup.get_text(separator='\n')
        cleaned_text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        print(f"✅ Fetched content from {url}")
        return cleaned_text, soup
    except Exception as e:
        print(f"❌ Failed to fetch {url} | Error: {e}")
        return None, None

def save_text_to_file(content, filename):
    filepath = os.path.join(TXT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Saved content to {filepath}")
    return filepath

def download_pdf(pdf_url):
    global pdf_downloaded
    if pdf_downloaded >= MAX_PDF_DOWNLOAD:
        print(f"⚠️ PDF download limit reached ({MAX_PDF_DOWNLOAD})")
        return None
    try:
        pdf_filename = os.path.basename(pdf_url.split('?')[0])
        local_pdf_path = os.path.join(PDF_DIR, pdf_filename)
        response = requests.get(pdf_url, timeout=30)
        if response.status_code == 200:
            with open(local_pdf_path, 'wb') as f:
                f.write(response.content)
            pdf_downloaded += 1
            print(f"✅ Downloaded PDF: {pdf_url}")
            return local_pdf_path
        else:
            print(f"❌ Failed to download PDF: {pdf_url}")
            return None
    except Exception as e:
        print(f"❌ Error downloading PDF {pdf_url}: {e}")
        return None

def convert_pdf_to_txt(pdf_path):
    try:
        txt_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.txt'
        output_txt_path = os.path.join(TXT_DIR, txt_filename)
        subprocess.run(['pdftotext', pdf_path, output_txt_path], check=True)
        print(f"✅ Converted PDF to TXT: {output_txt_path}")
        return output_txt_path
    except subprocess.CalledProcessError:
        print(f"❌ Failed to convert PDF: {pdf_path}")
        return None

def train_on_text_file(txt_file_path):
    txt_file = Path(txt_file_path)
    if not txt_file.exists():
        print(f"❌ Training skipped, file not found: {txt_file_path}")
        return
    text = txt_file.read_text(encoding='utf-8', errors='ignore')
    chunk_size = DEFAULT_CHUNK_SIZE if len(text) <= CHUNK_THRESHOLD else 500
    print(f"✅ Training on: {txt_file.name} | Size: {len(text)} chars | Chunk size: {chunk_size}")
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.now()} | Trained from: {txt_file.name} | Size: {len(text)} chars | Chunk size: {chunk_size}\n")

def crawl_page(url, depth_remaining):
    global crawled_urls
    if url in crawled_urls or depth_remaining < 0:
        return
    crawled_urls.add(url)

    content, soup = fetch_web_content(url)
    if content:
        filename = "main_page.txt" if url == BASE_URL + '/en/home' else f"page_{len(crawled_urls)}.txt"
        main_txt = save_text_to_file(content, filename)
        train_on_text_file(main_txt)

    if not soup or depth_remaining == 0:
        return

    for link in soup.find_all('a', href=True):
        href = link['href']
        print(f"🔗 Found link: {href}")

        # PDF download check
        if href.lower().endswith('.pdf'):
            pdf_url = BASE_URL + href if href.startswith('/') else href
            local_pdf = download_pdf(pdf_url)
            if local_pdf:
                txt_from_pdf = convert_pdf_to_txt(local_pdf)
                if txt_from_pdf:
                    train_on_text_file(txt_from_pdf)
            continue

        # Internal crawl depth control
        if href.startswith('/en/') or BASE_URL in href:
            next_url = BASE_URL + href if href.startswith('/') else href
            print(f"🔄 Crawling deeper into: {next_url} | Depth remaining: {depth_remaining - 1}")
            crawl_page(next_url, depth_remaining - 1)

if __name__ == '__main__':
    start_urls = [BASE_URL + '/en/home']
    MAX_DEPTH = 2  # ✅ Set your desired depth here

    for url in start_urls:
        crawl_page(url, MAX_DEPTH)

    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.now()} | ✅ Full Web Crawl & PDF Training Completed | PDFs downloaded: {pdf_downloaded}\n")
    print(f"✅ Full Web Crawl & PDF Training Completed at {datetime.now()}")
    print(f"✅ Total PDFs downloaded: {pdf_downloaded}")
