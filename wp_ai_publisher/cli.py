from __future__ import annotations
from pathlib import Path
from time import monotonic
import typer
from .config import load_config
from .sheet import KeywordSheet
from .opencode_client import OpenCodeGenerator
from .wp_client import WordPressClient
from .pipeline import Pipeline
from .logging_setup import setup, log_event

app = typer.Typer(help="Generate WordPress drafts using OpenCode as the writer.")

@app.command("list-sites")
def list_sites():
    config = load_config()
    for site in config.sites: typer.echo(f"{site.id:20} {site.seo_plugin:8} {'credentials configured' if site.credentials else 'MISSING credentials'}")

@app.command()
def validate(site: str | None = typer.Option(None, "--site"), allow_insecure: bool = False):
    config = load_config(require_credentials=False)
    targets = [config.site(site)] if site else config.sites
    missing = [s.id for s in targets if not s.credentials]
    if missing: raise typer.BadParameter("Missing WordPress credentials for: " + ", ".join(missing))
    for s in targets:
        client = WordPressClient(s, allow_insecure=allow_insecure)
        try:
            client.request("GET", "/wp-json/")
            if s.seo_plugin != "none":
                routes = client.request("GET", "/wp-json/").json().get("routes", {})
                if "/ai-publisher/v1/seo-meta/(?P<post_id>\\d+)" not in routes:
                    raise RuntimeError("AI Publisher MU-plugin route is not registered")
            typer.echo(f"{s.id}: OK")
        except Exception as exc: raise typer.BadParameter(f"{s.id}: REST/MU-plugin validation failed; install wp_mu_plugin/ai-publisher-seo-meta.php first. {exc}")

@app.command()
def run(sheet: Path = typer.Option(..., "--sheet", exists=True), site: str | None = typer.Option(None, "--site"), limit: int | None = typer.Option(None, "--limit"), dry_run: bool = False, model: str | None = None, classic_html: bool = False, allow_insecure: bool = False):
    config = load_config(require_credentials=not dry_run)
    keyword_sheet = KeywordSheet(sheet); rows = keyword_sheet.pending(site, limit)
    logger, log_path = setup(config.settings.logging.get("log_dir", "logs"))
    generator = OpenCodeGenerator(model or config.settings.opencode.model, config.settings.opencode.server_url, config.settings.opencode.timeout_seconds, config.settings.run.max_retries, config.settings.opencode.use_server)
    pipeline = Pipeline(generator, lambda s: WordPressClient(s, config.settings.run.max_retries, config.settings.run.requests_per_minute_per_site, allow_insecure))
    ok = failed = 0
    for number, row in enumerate(rows, 1):
        started = monotonic(); target = config.site(row.values["site_id"])
        typer.echo(f"[{number}/{len(rows)}] {target.id} | {row.values['keyword']!r} | generating...")
        try:
            result = pipeline.process(row, target, dry_run, classic_html)
            if dry_run:
                typer.echo(str(result["payload"]))
                keyword_sheet.update(row, status="pending", error_message="")
            else:
                post_id = result["id"]; edit_url = result.get("link") or f"{target.base_url}/wp-admin/post.php?post={post_id}&action=edit"
                keyword_sheet.update(row, status="done", post_id=post_id, edit_url=edit_url, error_message="")
                typer.echo(f"done (post {post_id})")
            ok += 1; log_event(log_path, row_index=row.index, site_id=target.id, keyword=row.values["keyword"], duration=monotonic()-started, post_id=result.get("id") if not dry_run else None, status="success")
        except Exception as exc:
            failed += 1; keyword_sheet.update(row, status="error", error_message=str(exc)[:1000])
            typer.echo(f"FAILED: {exc}")
            log_event(log_path, row_index=row.index, site_id=target.id, keyword=row.values["keyword"], duration=monotonic()-started, error=str(exc), status="error")
    typer.echo(f"Summary: total={len(rows)} succeeded={ok} failed={failed} skipped=0; log: {log_path}")

@app.command("init-site")
def init_site(site_id: str):
    typer.echo(f"Add {site_id} to config/sites.yaml and its credentials to .env or config/sites.local.yaml.")

if __name__ == "__main__":
    app()
