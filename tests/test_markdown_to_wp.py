from wp_ai_publisher.markdown_to_wp import to_wordpress_html
def test_blocks():
    html = to_wordpress_html("# Hello\n\nA paragraph\n\n- one")
    assert "<!-- wp:heading" in html and "<!-- wp:paragraph -->" in html and "<!-- wp:list -->" in html
