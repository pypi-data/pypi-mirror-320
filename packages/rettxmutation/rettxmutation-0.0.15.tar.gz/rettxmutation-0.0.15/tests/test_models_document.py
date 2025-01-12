import pytest
from pydantic import ValidationError
from rettxmutation.analysis.models import Document, WordData, Keyword


# Tests for the Document model
def test_document_initialization():
    # Test successful initialization
    word_data = [
        WordData(word="test", confidence=0.9, page_number=1),
        WordData(word="example", confidence=0.8, page_number=1)
    ]
    keywords = [
        Keyword(value="key1", type="variant"),
        Keyword(value="key2", type="gene_name")
    ]
    doc = Document(
        raw_text="Sample text",
        cleaned_text="Clean text",
        summary="Summary",
        language="en",
        words=word_data,
        keywords=keywords,
        text_analytics_result=keywords,
    )
    assert doc.raw_text == "Sample text"
    assert doc.cleaned_text == "Clean text"
    assert doc.language == "en"
    assert len(doc.words) == 2
    assert len(doc.keywords) == 2


def test_document_invalid_data():
    # Test validation errors
    with pytest.raises(ValidationError):
        Document(raw_text="Sample", language="en", words="invalid_type")


def test_find_word_confidence():
    word_data = [
        WordData(word="test", confidence=0.9, page_number=1),
        WordData(word="example", confidence=0.8, page_number=1)
    ]
    doc = Document(raw_text="Sample", language="en", words=word_data)

    assert doc.find_word_confidence("test") == 0.9
    assert doc.find_word_confidence("example") == 0.8
    assert doc.find_word_confidence("missing") is None


def test_dump_keywords():
    keywords = [
        Keyword(value="key1", type="variant"),
        Keyword(value="key2", type="gene_name")
    ]
    doc = Document(raw_text="Sample", language="en", words=[], keywords=keywords)

    assert doc.dump_keywords() == "key1\nkey2"
    assert doc.dump_keywords(separator=", ") == "key1, key2"

    # Test with no keywords
    doc_no_keywords = Document(raw_text="Sample", language="en", words=[])
    assert doc_no_keywords.dump_keywords() == ""


def test_dump_text_analytics_keywords():
    text_analytics_result = [
        Keyword(value="analytics1", type="variant"),
        Keyword(value="analytics2", type="gene_name")
    ]
    doc = Document(raw_text="Sample", language="en", words=[], text_analytics_result=text_analytics_result)

    assert doc.dump_text_analytics_keywords() == "analytics1\nanalytics2"
    assert doc.dump_text_analytics_keywords(separator=", ") == "analytics1, analytics2"

    # Test with no text analytics keywords
    doc_no_analytics = Document(raw_text="Sample", language="en", words=[])
    assert doc_no_analytics.dump_text_analytics_keywords() == ""


def test_dump_all_content():
    keywords = [
        Keyword(value="key1", type="variant"),
        Keyword(value="key2", type="gene_name")
    ]
    doc = Document(
        raw_text="Sample",
        cleaned_text="Clean text",
        language="en",
        words=[],
        keywords=keywords,
    )

    content = doc.dump_all_content()
    assert content["cleaned_text"] == "Clean text"
    assert content["language"] == "en"
    assert content["keywords"] == "key1\nkey2"


def test_dump_plain_text():
    keywords = [
        Keyword(value="key1", type="variant"),
        Keyword(value="key2", type="gene_name")
    ]
    doc = Document(
        raw_text="Sample",
        cleaned_text="Clean text",
        language="en",
        words=[],
        keywords=keywords,
    )

    assert doc.dump_plain_text() == "Clean text key1 key2"

    # Test with no keywords
    doc_no_keywords = Document(raw_text="Sample", cleaned_text="Clean text", language="en", words=[])
    assert doc_no_keywords.dump_plain_text() == "Clean text"
