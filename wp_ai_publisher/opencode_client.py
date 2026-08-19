from __future__ import annotations
import socket, subprocess
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .errors import ContentError

class ArticleGenerator:
    def generate(self, prompt: str) -> str: raise NotImplementedError

class OpenCodeGenerator(ArticleGenerator):
    def __init__(self, model: str, server_url: str, timeout: int, retries: int = 3, use_server: bool = True):
        self.model, self.server_url, self.timeout, self.retries, self.use_server = model, server_url, timeout, retries, use_server
        self.server_process = None

    def start_server(self):
        if not self.use_server: return
        parsed = urlparse(self.server_url); host, port = parsed.hostname or "localhost", parsed.port or 4096
        try: socket.create_connection((host, port), 0.5).close(); return
        except OSError: pass
        self.server_process = subprocess.Popen(["opencode", "serve", "--port", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generate(self, prompt: str) -> str:
        self.start_server()
        return self._run(prompt)

    @retry(retry=retry_if_exception_type((subprocess.TimeoutExpired, OSError)), stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=15), reraise=True)
    def _run(self, prompt: str) -> str:
        cmd = ["opencode", "run", "--model", self.model, "--print-logs"]
        if self.use_server: cmd += ["--attach", self.server_url]
        cmd.append(prompt)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        if result.returncode:
            message = (result.stderr or result.stdout).strip()
            if "policy" in message.lower() or "refus" in message.lower(): raise ContentError(f"OpenCode refused request: {message}")
            raise OSError(f"OpenCode exited {result.returncode}: {message}")
        return result.stdout
