from typing import Optional
from bs4 import BeautifulSoup
import unicodedata
import re

class TextProcessor:
    def __init__(
        self,
        remove_html: bool = True,
        remove_special_chars: bool = True,
        lowercase: bool = True,
        normalize_whitespace: bool = True,
        max_length: Optional[int] = None
    ):
        self.remove_html = remove_html
        self.remove_special_chars = remove_special_chars
        self.lowercase = lowercase
        self.normalize_whitespace = normalize_whitespace
        self.max_length = max_length
    
    def process(self, text: str) -> str:
        if self.remove_html:
            text = self._remove_html_tags(text)
            
        if self.remove_special_chars:
            text = self._remove_special_characters(text)
            
        if self.lowercase:
            text = text.lower()
            
        if self.normalize_whitespace:
            text = self._normalize_whitespace(text)
            
        if self.max_length:
            text = self._truncate(text, self.max_length)
            
        return text
    
    @staticmethod
    def _remove_html_tags(text: str) -> str:
        return BeautifulSoup(text, "html.parser").get_text()
    
    @staticmethod
    def _remove_special_characters(text: str) -> str:
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return " ".join(text.split())
    
    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0]
