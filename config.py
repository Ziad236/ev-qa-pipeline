"""
Configuration for the EV Charging Data Pipeline.

This module contains all configuration settings for:
- Data sources (websites and PDFs)
- API keys
- File paths
- Model parameters
"""

# Data sources
DATA_SOURCES = {
    'web': [
        'https://afdc.energy.gov/fuels/electricity-infrastructure-trends',
        'https://driveelectric.gov/stations',
        'https://www.plugshare.com/',
        'https://www.eco-movement.com/',
        'https://datarade.ai/data-categories/electric-vehicle-charging-stations-data/providers',
        'https://en.wikipedia.org/wiki/Tesla_Supercharger',
        'https://en.wikipedia.org/wiki/IONITY',
        'https://en.wikipedia.org/wiki/Blink_Charging',
        'https://en.wikipedia.org/wiki/Pod_Point'
    ],
    'pdfs': [
        'https://www.nrel.gov/docs/fy24osti/90288.pdf',
        'https://docs.nrel.gov/docs/fy24osti/89896.pdf',
        'https://arxiv.org/pdf/2108.07772.pdf',
        'https://arxiv.org/pdf/2404.14452v1.pdf',
        'https://arxiv.org/pdf/2505.12145.pdf',
        'https://arxiv.org/pdf/2507.15718.pdf',
        'https://iea-pvps.org/wp-content/uploads/2025/01/IEA-PVPS-T17-04-2025-REPORT-Charging-Stations.pdf'
    ]
}

# API configurations
API_CONFIG = {
    'openrouter': {
        'api_base': "https://openrouter.ai/api/v1",
        'api_key': "your_openrouter_api_key",  # Replace with actual key
        'model': "deepseek/deepseek-r1-0528:free"
    },
    'groq': {
        'api_key': "your_groq_api_key",  # Replace with actual key
        'model': "gemma2-9b-it",
        'endpoint': "https://api.groq.com/openai/v1/chat/completions"
    }
}

# File paths
FILE_PATHS = {
    'chunks_csv': "chunks_500.csv",
    'chunk_metrics_csv': "chunk_metrics_500.csv",
    'qa_pairs_csv': "chunk_qa.csv",
    'deduplicated_qa_csv': "chunk_qa_deduplicated.csv"
}

# Processing parameters
PARAMS = {
    'max_words_per_chunk': 500,
    'num_questions_per_chunk': 3,
    'retry_attempts': 3,
    'fuzzy_match_threshold': 90
}