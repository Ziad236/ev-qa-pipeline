"""
Question-Answer Pair Generation Module.

Generates Q&A pairs from text chunks using Groq API.
Features:
- JSON output parsing with error handling
- Rate limiting protection
- CSV output for generated pairs
"""
import requests
import json
import time
import os
import csv
import random
from config import FILE_PATHS, PARAMS, API_CONFIG

CSV_FILE = "chunks_500.csv"
QA_CSV_FILE = "chunk_qa.csv"
GROQ_API_KEY = API_CONFIG['groq']['api_key']
GROQ_MODEL = "gemma2-9b-it"


def generate_questions_groq(chunk, num_questions=PARAMS['num_questions_per_chunk'], retries=PARAMS['retry_attempts']):
    """
    Generate Q&A pairs from text using Groq API.

    Args:
        chunk (str): Text to generate questions from
        num_questions (int): Number of Q&A pairs to generate
        retries (int): Max retry attempts

    Returns:
        list: Generated Q&A pairs as dictionaries

    Raises:
        RuntimeError: If all retries fail
    """
    prompt = f"""
Generate {num_questions} question-and-answer pairs from the following text. 
Each pair should be a dictionary with "question" and "answer" keys. 
Return the full output as a JSON array like this:

[
  {{"question": "What is ...?", "answer": "The ..."}},
  ...
]

Text:
\"\"\"{chunk}\"\"\"
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates Q&A pairs from technical content."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload, headers=headers, timeout=30
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]

                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print("⚠️ JSON decode failed. Attempting to fix...")
                    if content.strip().endswith("}"):
                        fixed_content = content.strip() + "]"
                        try:
                            return json.loads(fixed_content)
                        except:
                            pass
                    print("❌ Could not fix JSON. Raw output:")
                    print(content)
                    return []

            else:
                print(f"⚠️ Groq API error {response.status_code}: {response.text}")
                time.sleep(2 ** attempt + random.uniform(0.5, 1.5))  # backoff

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt + random.uniform(0.5, 1.5))

    raise RuntimeError("❌ Failed to get response from Groq after retries.")


if __name__ == "__main__":
    # Initialize output file
    if not os.path.exists(FILE_PATHS['qa_pairs_csv']):
        with open(FILE_PATHS['qa_pairs_csv'], mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Chunk Index", "Question", "Answer"])


    with open(FILE_PATHS['chunks_csv'], newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            chunk_text = row.get("Chunk Text") or row.get("chunk_text") or list(row.values())[0]

            if not chunk_text or not chunk_text.strip():
                print(f"⏭️ Skipping empty chunk {i}")
                continue

            print(f"🧠 Generating Q&A for Chunk {i}...")

            try:
                qa_pairs = generate_questions_groq(chunk_text, num_questions=3)

                with open(QA_CSV_FILE, mode='a', newline='', encoding='utf-8') as qa_file:
                    writer = csv.writer(qa_file)
                    for pair in qa_pairs:
                        writer.writerow([i, pair.get("question", "").strip(), pair.get("answer", "").strip()])

                print(f"✅ Saved Q&A for Chunk {i}")
                time.sleep(random.uniform(3, 5))  # Delay to avoid rate limits

            except Exception as e:
                print(f"❌ Failed to generate Q&A for Chunk {i}: {e}")
