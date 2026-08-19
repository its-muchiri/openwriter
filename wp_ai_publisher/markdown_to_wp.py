from __future__ import annotations
import re
try:
    import markdown
except ImportError:  # Keeps basic dry-runs usable before dependencies are installed.
    markdown = None

def _minimal_markdown(source: str) -> str:
    chunks = []
    for part in source.strip().split("\n\n"):
        if part.startswith("# "): chunks.append(f"<h1>{part[2:]}</h1>")
        elif part.startswith("## "): chunks.append(f"<h2>{part[3:]}</h2>")
        elif all(line.startswith("- ") for line in part.splitlines()): chunks.append("<ul>" + "".join(f"<li>{x[2:]}</li>" for x in part.splitlines()) + "</ul>")
        else: chunks.append(f"<p>{part}</p>")
    return "\n".join(chunks)

def to_wordpress_html(source: str, classic_html: bool = False) -> str:
    html = markdown.markdown(source, extensions=["extra"]) if markdown else _minimal_markdown(source)
    if classic_html: return html
    def wrap(match):
        tag, attrs, content = match.groups(); attrs = attrs or ""
        block = {"p":"paragraph", "h1":"heading", "h2":"heading", "h3":"heading", "h4":"heading", "ul":"list", "ol":"list", "blockquote":"quote"}.get(tag)
        if not block: return match.group(0)
        options = f' {{"level":{tag[1:]}}}' if tag.startswith("h") else ""
        return f"<!-- wp:{block}{options} -->\n<{tag}{attrs}>{content}</{tag}>\n<!-- /wp:{block} -->"
    return re.sub(r"<(p|h[1-4]|ul|ol|blockquote)([^>]*)>(.*?)</\1>", wrap, html, flags=re.S)
