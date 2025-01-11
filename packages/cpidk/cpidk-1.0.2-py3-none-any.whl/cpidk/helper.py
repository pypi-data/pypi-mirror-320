import re


def clean_text(text: str) -> str:
    text = text.upper()

    text = re.sub(r"[^A-Z0-9ŻÓŁĆĘŚĄŹŃ]", "", text)

    text = (text.replace("Ż", "Z")
            .replace("Ó", "O")
            .replace("Ł", "L")
            .replace("Ć", "C")
            .replace("Ę", "E")
            .replace("Ś", "S")
            .replace("Ą", "A")
            .replace("Ź", "Z")
            .replace("Ń", "N"))

    return text