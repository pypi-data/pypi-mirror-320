import os
import json
from datetime import datetime
from typing import List, Dict


class CorrectionsHandler:
    """
    Handles the storage and management of translation corrections.
    """

    def __init__(self, corrections_dir: str = "corrections"):
        """
        Initialize the corrections handler.

        Args:
            corrections_dir (str, optional): Directory to store corrections. Defaults to "corrections".
        """
        self.corrections_dir = corrections_dir
        os.makedirs(corrections_dir, exist_ok=True)

    def save_corrections(
        self,
        source_texts: List[str],
        translations: List[str],
        reviews: List[Dict],
        source_lang: str,
        target_lang: str,
        context: str = None
    ) -> str:
        """
        Save translation corrections to a file.

        Args:
            source_texts (List[str]): Original texts
            translations (List[str]): Translated texts
            reviews (List[Dict]): Review results
            source_lang (str): Source language code
            target_lang (str): Target language code
            context (str, optional): Additional context (e.g., file name, column). Defaults to None.

        Returns:
            str: Path to the corrections file
        """
        # Create corrections data
        corrections = []
        for src, trs, rev in zip(source_texts, translations, reviews):
            if not rev.get('is_correct', True):
                correction = {
                    'source_text': src,
                    'original_translation': trs,
                    'errors': rev.get('errors', []),
                    'correction': rev.get('suggested_correction', ''),
                    'explanation': rev.get('explanation', '')
                }
                corrections.append(correction)

        if not corrections:
            return None

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"corrections_{source_lang}_to_{target_lang}_{timestamp}.json"
        if context:
            # Clean context string to be filesystem-friendly
            clean_context = "".join(c if c.isalnum() else '_' for c in context)
            filename = f"corrections_{clean_context}_{timestamp}.json"

        filepath = os.path.join(self.corrections_dir, filename)

        # Save corrections to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'source_language': source_lang,
                'target_language': target_lang,
                'context': context,
                'timestamp': timestamp,
                'corrections': corrections
            }, f, ensure_ascii=False, indent=2)

        return filepath
