import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import BinaryIO, Optional, List, Dict, Any
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult
from rettxmutation.analysis.models import Document, WordData


logger = logging.getLogger(__name__)


class OcrExtractor:
    """
    Handles extraction of text from documents via Azure Form Recognizer
    (a.k.a. Document Analysis).
    """
    def __init__(self, endpoint: str, key: str):
        self._client = DocumentAnalysisClient(endpoint=endpoint,
                                              credential=AzureKeyCredential(key))

    def extract_text(self, file_stream: BinaryIO) -> Document:
        """
        Extracts text from a document and infers language (if available).
        """
        try:
            logger.debug("Processing stream with Form Recognizer")

            poller = self._client.begin_analyze_document(
                "prebuilt-read",
                document=file_stream,
                features=[DocumentAnalysisFeature.LANGUAGES]
            )
            result: AnalyzeResult = poller.result()

            if not result:
                logger.error("No valid document found by Form Recognizer")
                return "", None

            # Infer language
            inferred_language = None
            if result.languages:
                inferred_language = self._infer_language(result.languages)
                logger.debug(f"Detected language: {inferred_language}")

            # Save the words data in a structured format (using WordData model)
            words_data = self._extract_words(result)
            words = [WordData(**word) for word in words_data]

            logger.debug(f"Pages processed: {len(result.pages)}")

            return Document(raw_text=result.content, language=inferred_language, words=words)

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise

    def _extract_words(self, result: AnalyzeResult) -> List[Dict[str, Any]]:
        """
        Extracts word-level details (content, confidence, bounding box, etc.) from an AnalyzeResult.
        """
        words_data = []

        for page in result.pages:
            for word in page.words:
                words_data.append({
                    "word": word.content,
                    "confidence": word.confidence,
                    "page_number": page.page_number,
                    "offset": word.span.offset if word.span else None,
                    "length": word.span.length if word.span else None
                })

        logger.debug(f"Extracted {len(words_data)} words across {len(result.pages)} pages.")
        return words_data

    def _infer_language(self, languages) -> Optional[str]:
        """
        Private helper to infer the most likely language from a list of language detections.
        """
        language_confidences = {}
        for language in languages:
            lang = language.locale
            conf = language.confidence
            language_confidences[lang] = language_confidences.get(lang, 0) + conf
        if not language_confidences:
            return None
        return max(language_confidences, key=language_confidences.get)
