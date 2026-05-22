def generate_title(message: str) -> str:
    text = " ".join(message.strip().split())
    if not text:
        return "New conversation"
    if len(text) <= 42:
        return text
    return f"{text[:39].rstrip()}..."
