"""
Web and PDF Scraper for EV Charging Station Data.

This module handles:
- Scraping content from websites and PDFs
- Cleaning extracted text
- Splitting content into manageable chunks
- Saving results to CSV

Key Components:
- DataCollector: Main class coordinating scraping operations
- Text cleaning utilities
- Content splitting algorithms (by sections and sentences)
"""
from config import DATA_SOURCES, FILE_PATHS, PARAMS
import requests
from bs4 import BeautifulSoup
import pdfplumber
import os
import re
from nltk.tokenize import sent_tokenize
import csv
# Ensure NLTK sentence tokenizer is available
# nltk.download('punkt_tab')


def clean_text(text):
    """
    Clean raw text by removing unwanted elements.

    Args:
        text (str): Raw input text

    Returns:
        str: Cleaned text with URLs, HTML tags, citations, etc. removed
    """
    text = re.sub(r'https?://\S+', '', text)                       # Remove URLs
    text = re.sub(r'<[^>]+>', '', text)                            # Remove HTML tags
    text = re.sub(r'\[\d+(–\d+)?\]', '', text)                     # Remove citations like [1], [1–3]
    text = re.sub(r'(Figure|Table) \d+[^.\n]*', '', text)          # Remove figure/table captions
    text = re.sub(r'\s+', ' ', text)                               # Normalize whitespace
    return text.strip()


def split_section_into_chunks(heading, text, max_words=PARAMS['max_words_per_chunk']):
    """
    Split a section of text into smaller chunks based on sentences.

    Args:
        heading (str): Section heading
        text (str): Content to split
        max_words (int): Maximum words per chunk

    Returns:
        list: Tuples of (heading, chunk) pairs
    """
    sentences = sent_tokenize(text)
    current_chunk = []
    word_count = 0
    result = []

    for sent in sentences:
        current_chunk.append(sent)
        word_count += len(sent.split())
        if word_count >= max_words:
            result.append((heading, ' '.join(current_chunk)))
            current_chunk = []
            word_count = 0

    if current_chunk:
        result.append((heading, ' '.join(current_chunk)))

    return result


def split_web_with_headings(soup, max_words=PARAMS['max_words_per_chunk']):
    chunks = []
    current_heading = "Intro"
    current_text = []

    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if tag.name in ['h1', 'h2', 'h3']:
            if current_text:
                content = ' '.join(current_text).strip()
                chunks.extend(split_section_into_chunks(current_heading, content, max_words))
                current_text = []
            current_heading = tag.get_text(strip=True)
        elif tag.name == 'p':
            text = tag.get_text(strip=True)
            if text:
                current_text.append(text)

    if current_text:
        content = ' '.join(current_text).strip()
        chunks.extend(split_section_into_chunks(current_heading, content, max_words))

    return chunks


def split_pdf_with_nlp(text, max_words=PARAMS['max_words_per_chunk']):
    text = clean_text(text)
    section_pattern = re.compile(r'\n?\s*(\d{0,2}\.?\s*[A-Z][^\n:\.]{3,80})[:\n]')
    matches = list(re.finditer(section_pattern, text))

    if not matches:
        # Fallback
        return split_section_into_chunks("Generic", text, max_words)

    results = []
    for i in range(len(matches)):
        heading = matches[i].group(1).strip()
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_body = text[start:end].strip()
        results.extend(split_section_into_chunks(heading, section_body, max_words))

    return results


class DataCollector:
    """Main data collection class that coordinates scraping operations."""
    def __init__(self, config):
        """
        Initialize the DataCollector.

        Args:
            config (dict): Configuration dictionary containing data sources
        """
        self.config = config
        self.raw_data = []

    def scrape_websites(self):
        """Scrape configured websites and extract structured content."""
        for url in self.config['data_sources']['web']:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                if 'datarade.ai' in url:
                    providers = soup.select('div.provider-card')
                    for provider in providers:
                        name = provider.find('h3')
                        desc = provider.find('p')
                        content = f"{name.get_text(strip=True) if name else ''}: {desc.get_text(strip=True) if desc else ''}"
                        self.raw_data.append({
                            'source': url,
                            'section': name.get_text(strip=True) if name else 'Provider',
                            'content': content,
                            'type': 'web'
                        })
                else:
                    chunks = split_web_with_headings(soup)
                    for heading, chunk in chunks:
                        self.raw_data.append({
                            'source': url,
                            'section': heading,
                            'content': chunk,
                            'type': 'web'
                        })

            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")

    def extract_pdfs(self):
        """Download and extract text from configured PDF files."""
        for pdf_path in self.config['data_sources']['pdfs']:
            try:
                # Determine if it's a URL or local file
                if pdf_path.startswith("http://") or pdf_path.startswith("https://"):
                    local_path = f"temp_{os.path.basename(pdf_path)}"
                    with requests.get(pdf_path, stream=True) as r:
                        r.raise_for_status()
                        with open(local_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    cleanup = True
                else:
                    local_path = pdf_path
                    cleanup = False

                with pdfplumber.open(local_path) as pdf:
                    content = '\n'.join([page.extract_text() or '' for page in pdf.pages])
                    chunks = split_pdf_with_nlp(content)

                    for heading, chunk in chunks:
                        self.raw_data.append({
                            'source': pdf_path,
                            'section': heading,
                            'content': chunk,
                            'type': 'pdf'
                        })

                if cleanup:
                    os.remove(local_path)

            except Exception as e:
                print(f"Error processing PDF {pdf_path}: {str(e)}")

    def run(self):
        """
        Execute full data collection pipeline.

        Returns:
            list: Collected raw data items with source metadata
        """
        self.scrape_websites()
        self.extract_pdfs()
        return self.raw_data


if __name__ == "__main__":
    collector = DataCollector({'data_sources': DATA_SOURCES})
    data = collector.run()

    # Save to CSV
    with open(FILE_PATHS['chunks_csv'], mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Type", "Section", "Chunk Text"])
        for item in data:
            writer.writerow([
                item.get("source", ""),
                item.get("type", ""),
                item.get("section", ""),
                item.get("content", "")
            ])
    print(f"✅ Saved {len(data)} chunks to {FILE_PATHS['chunks_csv']}")