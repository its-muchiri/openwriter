import json, logging
from pathlib import Path
from datetime import datetime

def setup(log_dir="logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    path = Path(log_dir) / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
    logger = logging.getLogger("wp_ai_publisher"); logger.setLevel(logging.INFO)
    logger.handlers.clear(); logger.addHandler(logging.StreamHandler())
    return logger, path

def log_event(path, **event):
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps(event, default=str) + "\n")
