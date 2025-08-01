"""
Chunk Evaluation Module.

Evaluates text chunks on multiple metrics using LLM:
- Coherence
- Completeness
- Token count
- Semantic overlap with previous chunk

Features:
- Safe evaluation with retries
- CSV output for metrics
- Configurable evaluation parameters
"""
from scrapper2 import DataCollector
import json
import openai
import time
import csv
import os
import random
from config import API_CONFIG, FILE_PATHS, PARAMS, DATA_SOURCES

openai.api_base = API_CONFIG['openrouter']['api_base']
openai.api_key = API_CONFIG['openrouter']['api_key']

CSV_FILE = "chunk_metrics_500.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Chunk Text", "Coherence", "Incomplete", "Token Count", "Overlap", "Comment"])


def build_eval_prompt(chunk, previous_chunk=None):
    """
        Construct evaluation prompt for LLM.

        Args:
            chunk (str): Current text chunk to evaluate
            previous_chunk (str, optional): Previous chunk for overlap comparison

        Returns:
            str: Formatted evaluation prompt
        """
    return f"""
Evaluate the following text chunk on the following metrics:
1. **Coherence (1–5)**: Does the text flow well and make sense on its own?
2. **Incomplete Sentences (Yes/No)**: Does it look like the chunk ends or begins mid-sentence?
3. **Token Count**: How many tokens approximately?
{f"4. **Semantic Overlap (1–5)** with the previous chunk: Compare and rate overlap." if previous_chunk else ""}

Chunk:
\"\"\"{chunk}\"\"\"

{f"Previous Chunk:\n\"\"\"{previous_chunk}\"\"\"" if previous_chunk else ""}

Return only the result as raw JSON. Do not add any extra explanation or formatting:
{{
  "coherence": int (1-5),
  "incomplete": "Yes" or "No",
  "token_count": int,
  {"\"overlap\": int (1-5)," if previous_chunk else ""}
  "comment": brief explanation
}}
"""


def evaluate_chunk(chunk, previous_chunk=None):
    """
    Evaluate a text chunk using LLM.

    Args:
        chunk (str): Text to evaluate
        previous_chunk (str, optional): Previous chunk for comparison

    Returns:
        str: Raw LLM response with evaluation metrics
    """
    prompt = build_eval_prompt(chunk, previous_chunk)
    response = openai.ChatCompletion.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message['content']


def safe_evaluate_chunk(chunk, prev, retries=PARAMS['retry_attempts'], delay=2):
    """
    Safely evaluate chunk with retry logic.

    Args:
        chunk (str): Text to evaluate
        prev (str): Previous chunk
        retries (int): Max retry attempts
        delay (int): Initial delay between retries

    Returns:
        dict: Parsed evaluation metrics

    Raises:
        Exception: If all retries fail
    """
    for attempt in range(1, retries + 1):
        try:
            llm_response = evaluate_chunk(chunk, prev)
            metrics = json.loads(llm_response)
            return metrics
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt == retries:
                raise
            time.sleep(delay * (2 ** (attempt - 1)) + random.uniform(0, 1))


if __name__ == "__main__":
    # Initialize CSV file
    if not os.path.exists(FILE_PATHS['chunk_metrics_csv']):
        with open(FILE_PATHS['chunk_metrics_csv'], mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Chunk Text", "Coherence", "Incomplete", "Token Count", "Overlap", "Comment"])

    # Load and process data
    collector = DataCollector({'data_sources': DATA_SOURCES})
    data = collector.run()

    for i, item in enumerate(data[:10]):
        chunk = item['content']
        prev = data[i - 1]['content'] if i > 0 else None

        print(f"🔎 Evaluating Chunk {i}...")
        try:
            metrics = safe_evaluate_chunk(chunk, prev)

            # Save to CSV
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    chunk[:3000],
                    metrics.get("coherence"),
                    metrics.get("incomplete"),
                    metrics.get("token_count"),
                    metrics.get("overlap", ""),
                    metrics.get("comment", "")
                ])

            print(f"✅ Saved Chunk {i}")
            time.sleep(2)  # avoid rate limits

        except Exception as e:
            print(f"❌ Final failure with Chunk {i}: {e}")
