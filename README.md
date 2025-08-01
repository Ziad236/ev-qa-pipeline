# 🔌 EV Charging QA Pipeline

An end-to-end NLP pipeline for extracting information from electric vehicle (EV) charging infrastructure sources and generating question-answer (Q&A) pairs. It scrapes data from websites and PDFs, chunks the content, evaluates chunk quality using LLMs, generates Q&A pairs, and deduplicates them using fuzzy logic.

---

## 📦 Features

- ✅ Scrape data from web pages and PDFs
- 🧼 Preprocess and chunk content into manageable sections
- 🧠 Evaluate chunk quality (coherence, overlap, etc.) using LLMs
- 🤖 Generate Q&A pairs using Groq’s LLM (Gemma 2)
- ✂️ Remove duplicate and similar Q&A pairs using fuzzy matching

---

## 🧰 Tech Stack

- Python 3.10+
- OpenRouter + Groq APIs
- `requests`, `beautifulsoup4`, `pdfplumber`, `nltk`, `rapidfuzz`
- CSV-based data flow

---

## 📁 Directory Structure

