from telegram.constants import MessageLimit


def split_message(text: str, max_len: int = MessageLimit.TEXT_LENGTH):
    parts = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut == -1:
            cut = text.rfind(" ", 0, max_len)
        if cut == -1:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:]
    parts.append(text)
    return parts
