# Template format

Each template is Markdown with YAML frontmatter. Required frontmatter: `name`,
`default_word_count`, and `default_tone`. Prompt text can use `{{keyword}}`,
`{{word_count}}`, `{{tone}}`, `{{audience}}`, and `{{internal_links_block}}`.
The JSON output contract is appended by the application.
