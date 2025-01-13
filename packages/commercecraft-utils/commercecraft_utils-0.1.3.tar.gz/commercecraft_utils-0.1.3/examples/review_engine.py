import os
import pandas as pd
from typing import List, Dict, Optional
from .review_service import ReviewService


class ReviewEngine:
    """
    Engine for reviewing translations in CSV files using the ReviewService.
    """

    def __init__(self, review_service: Optional[ReviewService] = None):
        """
        Initialize the review engine.

        Args:
            review_service (Optional[ReviewService], optional): Review service instance. 
            If None, creates a new one.
        """
        self.review_service = review_service or ReviewService()

    async def process_file(
        self,
        file_path: str,
        source_lang: str = 'en-US',
        target_langs: List[str] = None,
        exclude_columns: List[str] = None,
    ) -> Dict[str, Dict]:
        """
        Process a CSV file to review translations.

        Args:
            file_path (str): Path to the CSV file.
            source_lang (str, optional): Source language code. Defaults to 'en-US'.
            target_langs (List[str], optional): List of target language codes.
                If None, detects from column names.
            exclude_columns (List[str], optional): Columns to exclude from review.

        Returns:
            Dict[str, Dict]: Dictionary containing review results for each language pair.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Get columns that contain translations
        if target_langs is None:
            target_langs = []
            for col in df.columns:
                if '.' in col:
                    lang = col.split('.')[-1]
                    if lang != source_lang and lang not in target_langs:
                        target_langs.append(lang)

        exclude_columns = exclude_columns or []
        review_results = {}

        # Process each target language
        for target_lang in target_langs:
            print(f'\nReviewing translations for {target_lang}...')
            source_texts = []
            translated_texts = []

            # Collect text pairs for review
            for col in df.columns:
                if '.' not in col or col in exclude_columns:
                    continue

                base_col, lang = col.rsplit('.', 1)
                if lang == target_lang:
                    source_col = f'{base_col}.{source_lang}'
                    if source_col in df.columns:
                        # Get non-null pairs
                        valid_rows = df[df[col].notna() & df[source_col].notna()]
                        source_texts.extend(valid_rows[source_col].astype(str).tolist())
                        translated_texts.extend(valid_rows[col].astype(str).tolist())

            if source_texts and translated_texts:
                # Review translations
                reviews = await self.review_service.review_translations(
                    source_texts, translated_texts, source_lang, target_lang
                )

                # Generate report
                report = self.review_service.generate_review_report(
                    reviews, source_texts, translated_texts
                )

                review_results[target_lang] = {
                    'reviews': reviews,
                    'report': report
                }

                # Save report to file
                report_path = f'{os.path.splitext(file_path)[0]}_review_{target_lang}.txt'
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f'Review report saved to: {report_path}')

        return review_results
