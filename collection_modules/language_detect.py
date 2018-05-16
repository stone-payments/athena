import re

from bs4 import BeautifulSoup
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from markdown import markdown

from .languages_codes import languages as lang


def text_to_language(text: str):
    text = re.sub('```[^```]+```', '', text)
    text = markdown(text, extensions=['markdown.extensions.tables'])
    text = BeautifulSoup(text, 'html.parser')
    [s.extract() for s in text('a')]
    [s.extract() for s in text('code')]
    [s.extract() for s in text('img')]
    [s.extract() for s in text('table')]
    if not text:
        return "undefined"
    try:
        text = detect(text.get_text())
    except LangDetectException:
        return "undefined"
    if text in ["pt", "en"]:
        return lang[text]
    return "undefined"
