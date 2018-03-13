from langdetect import detect
import re
from .languages_codes import languages as lang


def text_to_language(text: str):
    text = re.sub('```[^```]+```', '', text).replace("/n", "")
    language = detect(text)
    return lang[language]
