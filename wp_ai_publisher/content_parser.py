from __future__ import annotations
import json, re
from pydantic import BaseModel, Field, field_validator
from .errors import ContentError

class Article(BaseModel):
    title: str = Field(min_length=1)
    meta_description: str = Field(min_length=1, max_length=155)
    focus_keyword: str = Field(min_length=1)
    body_markdown: str = Field(min_length=1)
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    excerpt: str = Field(min_length=1)

def parse_article(raw: str) -> Article:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S | re.I)
    candidate = fenced.group(1) if fenced else text[text.find("{"):text.rfind("}") + 1]
    try: return Article.model_validate(json.loads(candidate))
    except Exception as exc: raise ContentError(f"Invalid article JSON: {exc}") from exc
