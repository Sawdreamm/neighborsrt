#!/usr/bin/env python3
"""Local web UI for NeighborSRT.

Run this file, open http://127.0.0.1:8765, upload a video, and download SRT.
"""

from __future__ import annotations

import cgi
import html
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill"
UPLOADS = ROOT / "uploads"
OUTPUTS = ROOT / "outputs"
INDEX = ROOT / "index.html"
TRANSCRIBE = SKILL / "scripts" / "transcribe_media_to_srt.py"
VALIDATE = SKILL / "scripts" / "validate_srt.py"

HOST = "127.0.0.1"
PORT = int(os.environ.get("SRT2CAPCUT_PORT", "8765"))


def safe_name(name: str) -> str:
    keep = []
    for char in name:
        if char.isalnum() or char in "._-() ":
            keep.append(char)
        else:
            keep.append("_")
    value = "".join(keep).strip() or "upload"
    return value[:160]


def json_bytes(data: dict, status: int = 200) -> tuple[int, bytes, str]:
    return status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8"


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


class Handler(BaseHTTPRequestHandler):
    server_version = "NeighborSRTLocal/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_body(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_body(200, INDEX.read_bytes(), "text/html; charset=utf-8")
            return

        if parsed.path == "/api/health":
            body = {
                "ok": True,
                "python": sys.version.split()[0],
                "ffmpeg": bool(shutil.which("ffmpeg")),
                "transcribe_script": TRANSCRIBE.exists(),
            }
            self.send_body(*json_bytes(body))
            return

        if parsed.path.startswith("/download/"):
            name = urllib.parse.unquote(parsed.path.removeprefix("/download/"))
            target = (OUTPUTS / name).resolve()
            if not str(target).startswith(str(OUTPUTS.resolve())) or not target.exists():
                self.send_error(404, "File not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/x-subrip; charset=utf-8")
            self.send_header("Content-Length", str(target.stat().st_size))
            self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
            self.end_headers()
            self.wfile.write(target.read_bytes())
            return

        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/transcribe":
            self.send_error(404)
            return

        ctype, pdict = cgi.parse_header(self.headers.get("content-type", ""))
        if ctype != "multipart/form-data":
            self.send_body(*json_bytes({"ok": False, "error": "Expected multipart/form-data"}, 400))
            return

        pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST"})
        file_item = form["video"] if "video" in form else None
        if not file_item or not getattr(file_item, "filename", ""):
            self.send_body(*json_bytes({"ok": False, "error": "No video uploaded"}, 400))
            return

        model = form.getfirst("model", "large-v3")
        language = form.getfirst("language", "th")
        max_chars = form.getfirst("max_chars", "34")
        max_lines = form.getfirst("max_lines", "2")
        prompt = form.getfirst("prompt", "")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        original = safe_name(Path(file_item.filename).name)
        upload_path = UPLOADS / f"{timestamp}_{original}"
        output_base = upload_path.stem
        srt_path = OUTPUTS / f"{output_base}.srt"
        txt_path = OUTPUTS / f"{output_base}.txt"

        with upload_path.open("wb") as out:
            shutil.copyfileobj(file_item.file, out)

        cmd = [
            sys.executable,
            str(TRANSCRIBE),
            str(upload_path),
            "--language",
            language,
            "--model",
            model,
            "--max-chars",
            max_chars,
            "--max-lines",
            max_lines,
            "--transcript-out",
            str(txt_path),
            "-o",
            str(srt_path),
        ]
        if prompt.strip():
            cmd.extend(["--prompt", prompt.strip()])

        result = run_command(cmd)
        if result.returncode != 0:
            self.send_body(*json_bytes({"ok": False, "error": result.stdout[-6000:]}, 500))
            return

        validation = run_command([sys.executable, str(VALIDATE), str(srt_path), "--max-chars", "42", "--max-lines", max_lines])
        preview = html.escape(srt_path.read_text(encoding="utf-8")[:6000])
        body = {
            "ok": True,
            "srt": srt_path.name,
            "txt": txt_path.name if txt_path.exists() else None,
            "download_url": f"/download/{urllib.parse.quote(srt_path.name)}",
            "transcribe_log": result.stdout,
            "validation_log": validation.stdout,
            "preview": preview,
        }
        self.send_body(*json_bytes(body))


def main() -> None:
    UPLOADS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"NeighborSRT local web running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
