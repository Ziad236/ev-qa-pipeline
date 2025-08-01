import re

def clean_text(text):
    text = re.sub(r'https?://\S+', '', text)                       # URLs
    text = re.sub(r'<[^>]+>', '', text)                            # HTML tags
    text = re.sub(r'\[\d+(–\d+)?\]', '', text)                     # Citations
    text = re.sub(r'(Figure|Table) \d+[^.\n]*', '', text)          # Figures
    text = re.sub(r'\s+', ' ', text)                               # Normalize whitespace
    return text.strip()


def split_by_sections(text, max_words=300):
    section_pattern = re.compile(r'(?:^|\n)([A-Z][\w\s\-]{3,50})\n')
    sections = section_pattern.split(text)

    result = []
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        body = clean_text(sections[i + 1])
        words = body.split()

        # Hybrid split if section too long
        if len(words) > max_words:
            for j in range(0, len(words), max_words // 2):
                chunk = ' '.join(words[j:j + max_words])
                result.append((heading, chunk))
        else:
            result.append((heading, body))
    return result


def preprocess_data(raw_data):
    processed_chunks = []

    for item in raw_data:
        content = item['content']
        source = item['source']
        type_ = item['type']

        chunks = split_by_sections(content)
        for heading, chunk in chunks:
            processed_chunks.append({
                "source": source,
                "section": heading,
                "chunk": chunk,
                "type": type_
            })

    return processed_chunks
