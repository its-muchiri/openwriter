import pytest
from wp_ai_publisher.content_parser import parse_article
from wp_ai_publisher.errors import ContentError

GOOD = '{"title":"T","meta_description":"D","focus_keyword":"K","body_markdown":"Body","categories":["C"],"tags":["t"],"excerpt":"E"}'
def test_fenced_json(): assert parse_article("```json\n" + GOOD + "\n```").title == "T"
def test_invalid_json():
    with pytest.raises(ContentError): parse_article("nope")
