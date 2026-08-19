from pathlib import Path
from wp_ai_publisher.pipeline import Pipeline
from wp_ai_publisher.config import Site
from wp_ai_publisher.sheet import SheetRow
from wp_ai_publisher.content_parser import Article

class Gen:
    def generate(self, prompt): return '{"title":"T","meta_description":"D","focus_keyword":"K","body_markdown":"Body","categories":[],"tags":[],"excerpt":"E"}'
class WP:
    def post_payload(self, *args): return {"title":"T"}
def test_dry_run():
    tmp_path = Path(".test-artifacts/pipeline"); tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "default.md").write_text('---\nname: d\ndefault_word_count: 1\ndefault_tone: x\n---\n{{keyword}}')
    output = Pipeline(Gen(), lambda s: WP(), tmp_path).process(SheetRow(2, {"keyword":"topic"}), Site(id="a",base_url="https://a.example"), dry_run=True)
    assert output["payload"]["title"] == "T"
