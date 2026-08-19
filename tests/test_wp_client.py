from wp_ai_publisher.config import Site, Credentials
from wp_ai_publisher.content_parser import Article
from wp_ai_publisher.wp_client import WordPressClient
def test_seo_payload():
    site = Site(id="x", base_url="https://x.example", seo_plugin="yoast", credentials=Credentials(username="u", app_password="p"))
    payload = WordPressClient(site).post_payload(Article(title="t",meta_description="d",focus_keyword="k",body_markdown="b",excerpt="e"), "<p>b</p>", [], [])
    assert payload["meta"]["_yoast_wpseo_focuskw"] == "k"
