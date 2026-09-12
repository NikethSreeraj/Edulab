def word_count(text):
    return len(text.split())


def char_count(text):
    return len(text)


def summarize_notes(text):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    return "\n".join(f"• {sentence}" for sentence in sentences[:5]) if sentences else "No text available."
