import re
from typing import Dict, Tuple

class PIIAnonymizer:
    """In-memory PII obfuscation and re-hydration engine for GDPR/EBA compliance."""
    
    def __init__(self):
        self.iban_pattern = re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b')
        self.card_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

    def sanitize(self, text: str) -> Tuple[str, Dict[str, str]]:
        mapping = {}
        counter = 1

        def replace_iban(match):
            nonlocal counter
            placeholder = f"[MASKED_IBAN_{counter}]"
            mapping[placeholder] = match.group(0)
            counter += 1
            return placeholder

        def replace_card(match):
            nonlocal counter
            placeholder = f"[MASKED_CARD_{counter}]"
            mapping[placeholder] = match.group(0)
            counter += 1
            return placeholder

        sanitized_text = self.iban_pattern.sub(replace_iban, text)
        sanitized_text = self.card_pattern.sub(replace_card, sanitized_text)
        return sanitized_text, mapping

    def rehydrate(self, text: str, mapping: Dict[str, str]) -> str:
        for placeholder, original in mapping.items():
            text = text.replace(placeholder, original)
        return text
