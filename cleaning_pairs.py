"""
Q&A Pair Deduplication Module.

Removes duplicate and near-duplicate Q&A pairs using fuzzy matching.
Features:
- Exact duplicate detection
- Fuzzy string matching for similar questions
- Configurable similarity threshold
"""
import csv
from rapidfuzz import fuzz
from config import FILE_PATHS, PARAMS

INPUT_CSV = "chunk_qa.csv"
OUTPUT_CSV = "chunk_qa_deduplicated.csv"

def load_qa_pairs(filename):
    """
    Load Q&A pairs from CSV file.

    Args:
        filename (str): Path to input CSV

    Returns:
        list: List of dictionaries containing Q&A pairs
    """
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def is_fuzzy_duplicate(q1, q2, threshold=PARAMS['fuzzy_match_threshold']):
    """
    Check if two questions are fuzzy duplicates.

    Args:
        q1 (str): First question
        q2 (str): Second question
        threshold (int): Similarity threshold (0-100)

    Returns:
        bool: True if questions are similar above threshold
    """
    return fuzz.token_set_ratio(q1.lower(), q2.lower()) >= threshold

def deduplicate(pairs):
    """
    Remove duplicate and near-duplicate Q&A pairs.

    Args:
        pairs (list): List of raw Q&A pairs

    Returns:
        list: Deduplicated pairs
    """
    seen_exact = set()
    unique_pairs = []

    for current in pairs:
        q = current['Question'].strip()
        a = current['Answer'].strip()

        key = (q.lower(), a.lower())
        if key in seen_exact:
            continue  # skip exact duplicate
        seen_exact.add(key)

        # Fuzzy check against already accepted questions
        is_duplicate = any(
            is_fuzzy_duplicate(q, other['Question']) for other in unique_pairs
        )

        if not is_duplicate:
            unique_pairs.append(current)

    return unique_pairs

def save_qa_pairs(pairs, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Chunk Index', 'Question', 'Answer'])
        writer.writeheader()
        for row in pairs:
            writer.writerow(row)


if __name__ == "__main__":
    qa_pairs = load_qa_pairs(FILE_PATHS['qa_pairs_csv'])
    deduplicated = deduplicate(qa_pairs)
    save_qa_pairs(deduplicated, FILE_PATHS['deduplicated_qa_csv'])
    print(f"✅ Deduplicated Q&A pairs saved to {FILE_PATHS['deduplicated_qa_csv']}. Total kept: {len(deduplicated)}")
