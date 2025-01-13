import os
import json
import asyncio
from typing import Dict, List, Tuple
import openai
from dotenv import load_dotenv


class ReviewService:
    """
    A service that reviews translations using OpenAI's GPT model.
    Compares source and translated text to verify accuracy and suggest improvements.
    """

    def __init__(self, dotenv_path: str = None):
        """
        Initialize the review service.

        Args:
            dotenv_path (str, optional): Path to the .env file. Defaults to None.
        """
        if not load_dotenv(dotenv_path=dotenv_path if dotenv_path else '.env'):
            raise ValueError('No .env file found')

        # Load OpenAI configuration
        if (api_key := os.getenv('OPENAI_API_KEY')) is None:
            raise ValueError('OPENAI_API_KEY environment variable is required')
        openai.api_key = api_key

        if (model := os.getenv('OPENAI_MODEL')) is None:
            raise ValueError('OPENAI_MODEL environment variable is required')
        self.__model = model

        if (temperature := os.getenv('TEMPERATURE')) is None:
            raise ValueError('TEMPERATURE environment variable is required')
        self.__temperature = float(temperature)

        if (batch_size := os.getenv('BATCH_SIZE')) is None:
            raise ValueError('BATCH_SIZE environment variable is required')
        self.__batch_size = int(batch_size)

    def _create_system_prompt(self, source_lang: str, target_lang: str) -> str:
        """
        Create the system prompt for the review process.

        Args:
            source_lang (str): Source language code.
            target_lang (str): Target language code.

        Returns:
            str: Formatted system prompt.
        """
        return f"""You are a professional translation reviewer specializing in {source_lang} to {target_lang} translations.

                CRITICAL INSTRUCTIONS - YOU MUST FOLLOW EXACTLY:
                - Review each translation pair (original and translated text)
                - For each pair, provide a JSON response with the following structure:
                  {{
                    "is_correct": boolean,
                    "corrected_translation": "string (only if is_correct is false)",
                    "explanation": "string explaining any issues or confirming correctness",
                    "confidence_score": float between 0 and 1
                  }}
                - Maintain all formatting, numbers, and special characters exactly as they appear
                - Only suggest corrections for actual translation errors
                - Preserve any technical terms, brand names, or specific formatting
                - Consider cultural context and locale-specific terminology
                - Do not modify anything between {{{{}}}}
                """

    def _create_user_prompt(self, source_texts: list[str], translated_texts: list[str]) -> str:
        """
        Create the user prompt containing the text pairs to review.

        Args:
            source_texts (list[str]): Original texts.
            translated_texts (list[str]): Translated texts to review.

        Returns:
            str: Formatted user prompt.
        """
        pairs = []
        for i, (source, translated) in enumerate(zip(source_texts, translated_texts)):
            pairs.append(f"Pair {i + 1}:")
            pairs.append(f"Original: {source}")
            pairs.append(f"Translation: {translated}")
            pairs.append("---")
        return "\n".join(pairs)

    async def _review_batch(
        self,
        source_texts: list[str],
        translated_texts: list[str],
        source_lang: str,
        target_lang: str,
        max_retries: int = 3,
    ) -> List[Dict]:
        """
        Review a batch of translations.

        Args:
            source_texts (list[str]): Original texts.
            translated_texts (list[str]): Translated texts to review.
            source_lang (str): Source language code.
            target_lang (str): Target language code.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.

        Returns:
            List[Dict]: List of review results.
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = await openai.ChatCompletion.acreate(
                    model=self.__model,
                    temperature=self.__temperature,
                    messages=[
                        {
                            "role": "system",
                            "content": self._create_system_prompt(source_lang, target_lang),
                        },
                        {
                            "role": "user",
                            "content": self._create_user_prompt(source_texts, translated_texts),
                        },
                    ],
                )

                reviews = []
                content = response.choices[0].message.content
                for line in content.strip().split('\n'):
                    if line.strip() and not line.startswith('Pair') and not line.startswith('Original') and not line.startswith('Translation') and not line.startswith('---'):
                        try:
                            review = json.loads(line)
                            reviews.append(review)
                        except json.JSONDecodeError:
                            continue

                if len(reviews) != len(source_texts):
                    raise ValueError(
                        f'Expected {len(source_texts)} reviews, got {len(reviews)}'
                    )
                return reviews

            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(2 ** retry_count)
                else:
                    raise e

    async def review_translations(
        self,
        source_texts: list[str],
        translated_texts: list[str],
        source_lang: str,
        target_lang: str,
    ) -> List[Dict]:
        """
        Review multiple translations with batching and rate limiting.

        Args:
            source_texts (list[str]): Original texts.
            translated_texts (list[str]): Translated texts to review.
            source_lang (str): Source language code.
            target_lang (str): Target language code.

        Returns:
            List[Dict]: List of review results.
        """
        if len(source_texts) != len(translated_texts):
            raise ValueError("Number of source and translated texts must match")

        all_reviews = []
        for i in range(0, len(source_texts), self.__batch_size):
            batch_source = source_texts[i : i + self.__batch_size]
            batch_translated = translated_texts[i : i + self.__batch_size]

            try:
                reviews = await self._review_batch(
                    batch_source, batch_translated, source_lang, target_lang
                )
                all_reviews.extend(reviews)

                if i + self.__batch_size < len(source_texts):
                    # Rate limiting between batches
                    await asyncio.sleep(1)
            except Exception as e:
                print(f'Failed to review batch {i//self.__batch_size + 1}: {str(e)}')
                # Return partial reviews up to this point
                return all_reviews

        return all_reviews

    def generate_review_report(self, reviews: List[Dict], source_texts: list[str], translated_texts: list[str]) -> str:
        """
        Generate a human-readable report from the review results.

        Args:
            reviews (List[Dict]): List of review results.
            source_texts (list[str]): Original texts.
            translated_texts (list[str]): Translated texts.

        Returns:
            str: Formatted review report.
        """
        report_lines = ["Translation Review Report", "=" * 50, ""]
        
        total_translations = len(reviews)
        correct_translations = sum(1 for r in reviews if r['is_correct'])
        avg_confidence = sum(r['confidence_score'] for r in reviews) / total_translations
        
        report_lines.extend([
            f"Summary:",
            f"- Total translations reviewed: {total_translations}",
            f"- Correct translations: {correct_translations} ({(correct_translations/total_translations)*100:.1f}%)",
            f"- Average confidence score: {avg_confidence:.2f}",
            "",
            "Detailed Review:",
            "-" * 50,
            ""
        ])

        for i, (review, source, translated) in enumerate(zip(reviews, source_texts, translated_texts)):
            report_lines.extend([
                f"Item {i + 1}:",
                f"Original: {source}",
                f"Translation: {translated}",
                f"Status: {'✓ Correct' if review['is_correct'] else '✗ Needs Correction'}",
                f"Confidence: {review['confidence_score']:.2f}"
            ])
            
            if not review['is_correct']:
                report_lines.extend([
                    f"Suggested Correction: {review['corrected_translation']}",
                    f"Explanation: {review['explanation']}"
                ])
            
            report_lines.extend(["", "-" * 50, ""])

        return "\n".join(report_lines)
