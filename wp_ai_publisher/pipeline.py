from __future__ import annotations
from .content_parser import parse_article
from .markdown_to_wp import to_wordpress_html
from .templates import build_prompt
from .errors import ContentError

class Pipeline:
    def __init__(self, generator, wp_factory, template_dir="templates"):
        self.generator, self.wp_factory, self.template_dir = generator, wp_factory, template_dir
    def process(self, row, site, dry_run=False, classic_html=False):
        prompt = build_prompt(row.values, site, self.template_dir)
        raw = self.generator.generate(prompt)
        try: article = parse_article(raw)
        except ContentError:
            article = parse_article(self.generator.generate(prompt + "\nYour last response was invalid JSON. Return ONLY the JSON object."))
        html = to_wordpress_html(article.body_markdown, classic_html)
        client = self.wp_factory(site)
        categories = [x.strip() for x in str(row.values.get("category") or ",".join(article.categories) or site.default_category).split(",") if x.strip()]
        tags = [x.strip() for x in str(row.values.get("tags") or ",".join(article.tags)).split(",") if x.strip()]
        if dry_run: return {"article": article.model_dump(), "payload": client.post_payload(article, html, [], [])}
        payload = client.post_payload(article, html, [client.term_id("categories", x) for x in categories], [client.term_id("tags", x) for x in tags])
        return client.create_post(payload)
