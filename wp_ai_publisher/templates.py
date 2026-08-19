from __future__ import annotations
from pathlib import Path
import re, yaml
from .config import Site

OUTPUT_SCHEMA = '''\nReturn ONLY a JSON object (no code fence) with exactly these fields:\n{"title":"string","meta_description":"string <=155 chars","focus_keyword":"string","body_markdown":"string","categories":["string"],"tags":["string"],"excerpt":"string"}\n'''

def load_template(name: str, template_dir: Path = Path("templates")) -> tuple[dict, str]:
    path = template_dir / f"{name}.md"
    if not path.exists(): raise ValueError(f"Template not found: {name}")
    raw = path.read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    return yaml.safe_load(front), body.strip()

def build_prompt(row: dict, site: Site, template_dir: Path = Path("templates")) -> str:
    meta, body = load_template(row.get("template") or site.template, template_dir)
    links = [x.strip() for x in str(row.get("internal_links") or "").split(",") if x.strip()]
    values = {"keyword": row["keyword"], "word_count": row.get("word_count") or meta["default_word_count"], "tone": row.get("tone") or meta["default_tone"], "audience": row.get("audience") or "the site's readers", "internal_links_block": ("Use these internal links where relevant: " + ", ".join(links)) if links else ""}
    rendered = re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), "")), body)
    if row.get("title_override"): rendered += f'\nUse this exact title: "{row["title_override"]}".'
    return rendered + OUTPUT_SCHEMA
