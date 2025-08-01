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
ev-qa-pipeline/
-  ├── cleaning_pairs.py         
-  ├── chunks_eval2.py          
-  ├── config.py                 
-  ├── data_preprocessing.py     
-  ├── generate_QA.py           
-  ├── main.py                   
-  ├── run_pipeline.py           
-  ├── scrapper2.py            
-  ├── README.md                 
-  ├── .gitignore               
-  └── requirements.txt          


---

## 🚀 Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
---
2. **Set API keys in config.py**:

-  API_CONFIG['openrouter']['api_key']
-  API_CONFIG['groq']['api_key']
  
---

3. **Run the pipeline**:
- python run_pipeline.py

---

## 📊 Output Files
chunks_500.csv: All preprocessed chunks

chunk_metrics_500.csv: Quality evaluation for each chunk

chunk_qa.csv: Raw generated Q&A pairs

chunk_qa_deduplicated.csv: Cleaned Q&A pairs

---
## 🧠 Example Use Cases
Fine-tuning LLMs on Q&A datasets

QA bots for EV charging companies

Domain-specific educational material generation

   
