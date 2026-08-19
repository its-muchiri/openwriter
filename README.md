# WP AI Publisher

`wp-ai-publisher` is the **orchestrator**: it reads a keyword workbook and calls WordPress. OpenCode is the separate **writer**, invoked headlessly with `opencode run` for each article.

## Setup

Use Python 3.11+: `pip install -e .`. Copy `.env.example` to `.env`, or copy `config/sites.local.yaml.example` to `config/sites.local.yaml`; fill each site's WordPress username and Application Password. Generate an Application Password at **Users → Profile → Application Passwords**. Never use a normal account password.

Populate `config/sites.yaml` with real HTTPS URLs and accurate `seo_plugin` values. The committed 30-site registry is placeholders only. Copy `wp_mu_plugin/ai-publisher-seo-meta.php` into every site's `wp-content/mu-plugins/` directory. It enables Yoast/Rank Math fields through REST; no activation is required.

Run `wp-ai-publisher validate --site site-demo-01`, then use `wp-ai-publisher run --sheet sheets/keywords.xlsx --limit 3 --dry-run`. A real run is `wp-ai-publisher run --sheet sheets/keywords.xlsx`. Add `--classic-html` for Classic Editor sites. Dry run generates content and prints the post payload but performs no WordPress writes.

The workbook requires `keyword` and `site_id`; optional input columns are `template`, `title_override`, `category`, `tags`, `word_count`, `tone`, and `internal_links`. Managed columns are added automatically: `status`, `post_id`, `edit_url`, `last_run_at`, and `error_message`. Completed rows are skipped; failures are resumable.

Templates use YAML frontmatter and `{{keyword}}`, `{{word_count}}`, `{{tone}}`, `{{audience}}`, and `{{internal_links_block}}` placeholders. See `templates/_schema.md`.

If a credential leaks, immediately revoke its Application Password in the user's Profile screen, generate a new one, and replace it in the secret store. Do not put secrets in `sites.yaml`, logs, or workbooks. The tool refuses HTTP URLs unless `--allow-insecure` is explicit.
