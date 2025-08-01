"""
End-to-End Data Pipeline for EV Charging Station QA Generation

This script orchestrates a complete NLP pipeline that:
1. Scrapes EV-related content from websites and PDFs
2. Cleans, chunks, and preprocesses the data into manageable segments
3. Evaluates each chunk using a language model for quality metrics (coherence, overlap, etc.)
4. Generates multiple Q&A pairs for each chunk using an LLM
5. Removes exact and fuzzy duplicate Q&A pairs to ensure uniqueness

Modules Used:
- `scrapper2.py` — Handles web scraping and PDF extraction
- `data_preprocessing.py` — Cleans and chunks raw content
- `chunks_eval2.py` — Evaluates chunks for coherence and structure
- `generate_QA.py` — Generates Q&A pairs using Groq's LLM API
- `cleaning_pairs.py` — Deduplicates Q&A pairs using fuzzy logic

Configuration:
- API keys, data sources, file paths, and thresholds are stored in `config.py`
- Output files:
    - Chunked data: `chunks_500.csv`
    - Chunk metrics: `chunk_metrics_500.csv`
    - Raw Q&A pairs: `chunk_qa.csv`
    - Cleaned Q&A pairs: `chunk_qa_deduplicated.csv`

Usage:
Run the script as a standalone program:
    python run_pipeline.py

Make sure API keys are properly configured before running.
"""

import os
import csv
import time
from scrapper2 import DataCollector
from data_preprocessing import preprocess_data
from config import FILE_PATHS, PARAMS
from chunks_eval2 import safe_evaluate_chunk
from generate_QA import generate_questions_groq
from cleaning_pairs import load_qa_pairs, deduplicate, save_qa_pairs

print("🔍 Scraping data...")
collector = DataCollector({
    'data_sources': {
        'web': FILE_PATHS.get('web', []),
        'pdfs': FILE_PATHS.get('pdfs', [])
    }
})
raw_data = collector.run()

print("🧹 Preprocessing and chunking data...")
processed_data = preprocess_data(raw_data)

with open(FILE_PATHS['chunks_csv'], mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Source", "Type", "Section", "Chunk Text"])
    for item in processed_data:
        writer.writerow([
            item['source'],
            item['type'],
            item['section'],
            item['chunk']
        ])
print(f"✅ Saved {len(processed_data)} chunks to {FILE_PATHS['chunks_csv']}")

print("📊 Evaluating chunks...")
with open(FILE_PATHS['chunk_metrics_csv'], mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Chunk Text", "Coherence", "Incomplete", "Token Count", "Overlap", "Comment"])

for i, item in enumerate(processed_data):
    chunk = item['chunk']
    prev_chunk = processed_data[i - 1]['chunk'] if i > 0 else None
    print(f"🔎 Evaluating chunk {i}...")
    try:
        metrics = safe_evaluate_chunk(chunk, prev_chunk)
        with open(FILE_PATHS['chunk_metrics_csv'], mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                chunk[:3000],
                metrics.get("coherence"),
                metrics.get("incomplete"),
                metrics.get("token_count"),
                metrics.get("overlap", ""),
                metrics.get("comment", "")
            ])
        print(f"✅ Saved evaluation for chunk {i}")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to evaluate chunk {i}: {e}")

print("🧠 Generating Q&A pairs...")
with open(FILE_PATHS['qa_pairs_csv'], mode='w', newline='', encoding='utf-8') as qa_file:
    writer = csv.writer(qa_file)
    writer.writerow(["Chunk Index", "Question", "Answer"])

for i, item in enumerate(processed_data):
    chunk = item['chunk']
    try:
        qa_pairs = generate_questions_groq(chunk)
        with open(FILE_PATHS['qa_pairs_csv'], mode='a', newline='', encoding='utf-8') as qa_file:
            writer = csv.writer(qa_file)
            for pair in qa_pairs:
                writer.writerow([i, pair.get("question", "").strip(), pair.get("answer", "").strip()])
        print(f"✅ Saved Q&A for chunk {i}")
        time.sleep(3)
    except Exception as e:
        print(f"❌ Failed Q&A for chunk {i}: {e}")

print("🧹 Cleaning duplicate Q&A pairs...")
qa_pairs = load_qa_pairs(FILE_PATHS['qa_pairs_csv'])
deduplicated = deduplicate(qa_pairs)
save_qa_pairs(deduplicated, FILE_PATHS['deduplicated_qa_csv'])
print(f"✅ Final deduplicated Q&A saved. Total: {len(deduplicated)}")
