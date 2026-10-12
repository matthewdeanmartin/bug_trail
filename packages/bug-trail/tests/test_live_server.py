"""Check the installed CLI and Uvicorn server over real local HTTP."""

from pathlib import Path
import os
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def test_installed_http_server(tmp_path: Path) -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool.bug_trail]\n", encoding="utf-8")
    environment = {**os.environ, "APPDATA": str(tmp_path), "LOCALAPPDATA": str(tmp_path)}
    with (tmp_path / "server.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "bug_trail", "start", "--host", "127.0.0.1", "--port", str(port), "--db", str(tmp_path / "empty.db"), "--config", str(config)],
            cwd=tmp_path,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 15
            while True:
                try:
                    with urlopen(f"http://127.0.0.1:{port}/help", timeout=1) as response:
                        assert response.status == 200
                        assert "Getting started" in response.read().decode("utf-8")
                    break
                except URLError:
                    assert process.poll() is None, "server exited; see server.log"
                    assert time.monotonic() < deadline, "server did not start; see server.log"
                    time.sleep(0.1)
            with urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
                assert response.status == 200
                assert "No log data yet" in response.read().decode("utf-8")
            with urlopen(f"http://127.0.0.1:{port}/events", timeout=5) as response:
                assert response.headers["Content-Type"].startswith("text/event-stream")
                assert response.readline().strip() == b": connected"
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
