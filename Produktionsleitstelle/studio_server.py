"""Startet die LayerLokal-Leitstelle auf der lokalen Loopback-Adresse."""

import argparse
from functools import partial
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import secrets
import subprocess
from threading import Lock, Thread, Timer
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen
import webbrowser

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STUDIO = HERE / "Studio"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
SOURCES = {
    "drehbuch": ("Pilotdrehbuch", "Pino-Produktion/Drehbuch/Das-vierte-Rad-90-Sekunden.md"),
    "mechanik": ("Mechanikprüfung", "Pino-Produktion/Mechanik/Mechanikpruefung.md"),
    "produktion": ("Produktionsstand", "Pino-Produktion/Projektstart.md"),
    "regeln": ("Visuelle Serienregeln", "Pino-Produktion/Visual-Bible/README.md"),
    "freigaben": ("Freigaben", "Pino-Produktion/Visual-Bible/FREIGABEN.md"),
}


ORIGIN = "https://github.com/Fatih624/layerlokal-marketing.git"
def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW, timeout=20,
    )


def git_value(*args):
    result = git(*args)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Git-Stand konnte nicht gelesen werden.")
    return result.stdout.strip()


def pull(progress):
    if git_value("remote", "get-url", "origin").casefold() != ORIGIN.casefold():
        raise RuntimeError("GitHub-Adresse von origin weicht vom Marketing-Repository ab.")
    if git_value("branch", "--show-current") != "main":
        raise RuntimeError("Für die Aktualisierung wird der lokale Branch main erwartet.")
    if git_value("rev-parse", "--abbrev-ref", "@{upstream}") != "origin/main":
        raise RuntimeError("main benötigt origin/main als Upstream.")
    before = git_value("rev-parse", "--short", "HEAD")
    progress("Verbinde mit GitHub …")
    with subprocess.Popen(
        ["git", "-C", str(ROOT), "-c", "pull.autostash=false",
         "pull", "--ff-only", "--no-rebase", "--no-autostash", "--progress", "origin", "main"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW,
    ) as process:
        lines = []
        for line in process.stdout:
            message = line.strip()
            if message:
                lines.append(message)
                progress(message)
        if process.wait():
            raise RuntimeError("GitHub-Pull abgebrochen.\n" + "\n".join(lines[-16:]))
    after = git_value("rev-parse", "--short", "HEAD")
    return f"GitHub-Stand aktualisiert: {before} → {after}." if before != after else f"GitHub-Pull abgeschlossen · {after}."


class Application:
    def __init__(self, output):
        self.output = output
        self.token = secrets.token_urlsafe(24)
        self.identity = sha256(f"studio-v1{ROOT}\0{output}".encode()).hexdigest()
        self.lock = Lock()
        self.job = None

    def status(self):
        with self.lock:
            return self.job.copy() if self.job else None

    def begin(self, action):
        with self.lock:
            if self.job and self.job["status"] == "running":
                raise RuntimeError("Ein Vorgang läuft bereits.")
            self.job = {
                "action": action, "status": "running", "progress": None,
                "message": "Vorgang wird gestartet …",
            }
        Thread(target=self.run, args=(action,), daemon=True).start()

    def progress(self, message, percent=None):
        with self.lock:
            self.job.update(message=message, progress=percent)

    def run(self, action):
        try:
            message = pull(self.progress)
            with self.lock:
                self.job.update(status="done", progress=100, message=message)
        except Exception as error:
            with self.lock:
                self.job.update(status="error", progress=None, message=str(error))

    def state(self):
        return {"revision": git_value("rev-parse", "--short", "HEAD"),
                "branch": git_value("branch", "--show-current"),
                "changed": bool(git_value("status", "--porcelain")),
                "sources": {key: title for key, (title, path) in SOURCES.items()
                            if (ROOT / path).is_file()}}


class LocalServer(ThreadingHTTPServer):
    allow_reuse_address = os.name != 'nt'


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, app, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        pass

    def send_headers(self, status, kind, length):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()

    def json(self, value, status=HTTPStatus.OK):
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_headers(status, "application/json; charset=utf-8", len(data))
        self.wfile.write(data)

    def serve_file(self, path, content_type=None):
        with path.open("rb") as file:
            kind = content_type or mimetypes.guess_type(path.name)[0]
            self.send_headers(HTTPStatus.OK, kind or "application/octet-stream", os.fstat(file.fileno()).st_size)
            while chunk := file.read(128 * 1024):
                self.wfile.write(chunk)

    def local_request(self):
        if self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}":
            return True
        self.json({"error": "Die Leitstelle ist nur über ihre lokale Adresse erreichbar."}, HTTPStatus.FORBIDDEN)
        return False

    def do_GET(self):
        if not self.local_request():
            return
        url = urlsplit(self.path)
        try:
            if url.path == "/api/quelle":
                key = parse_qs(url.query).get("id", [""])[0]
                self.serve_file(ROOT / SOURCES[key][1], "text/plain; charset=utf-8")
            elif url.path == "/favicon.ico":
                self.send_headers(HTTPStatus.NO_CONTENT, "image/x-icon", 0)
            elif url.path == "/api/status":
                self.json(self.app.state())
            elif url.path == "/api/job":
                self.json(self.app.status())
            elif url.path == "/api/session":
                self.json({"token": self.app.token})
            elif url.path == "/health":
                self.json({"identity": self.app.identity})
            else:
                candidate = (STUDIO / (url.path.lstrip("/") or "index.html")).resolve()
                if not candidate.is_relative_to(STUDIO) or not candidate.is_file():
                    raise FileNotFoundError(url.path)
                self.serve_file(candidate)
        except (BrokenPipeError, ConnectionResetError):
            return
        except (FileNotFoundError, KeyError):
            self.json({"error": "Datei wurde nicht gefunden."}, HTTPStatus.NOT_FOUND)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            self.json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self):
        if not self.local_request():
            return
        if not secrets.compare_digest(self.headers.get("X-Leitstelle", ""), self.app.token):
            self.json({"error": "Bitte lade die Leitstelle neu."}, HTTPStatus.FORBIDDEN)
            return
        url = urlsplit(self.path)
        try:
            if url.path == "/api/pull":
                self.app.begin("pull")
            else:
                self.json({"error": "Vorgang nicht gefunden."}, HTTPStatus.NOT_FOUND)
                return
            self.json({"ok": True})
        except (KeyError, FileNotFoundError):
            self.json({"error": "Die Quelldatei ist nicht verfügbar."}, HTTPStatus.NOT_FOUND)
        except (OSError, RuntimeError) as error:
            self.json({"error": str(error)}, HTTPStatus.CONFLICT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["serve"])
    parser.add_argument("--ausgabe", type=Path, default=HERE / "PDF-Arbeitskopien")
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    output = args.ausgabe.resolve()
    app = Application(output)
    url = f"http://127.0.0.1:{args.port}/"
    try:
        server = LocalServer(("127.0.0.1", args.port), partial(Handler, app=app))
    except OSError as error:
        try:
            with urlopen(url + "health", timeout=2) as response:
                matching = json.load(response).get("identity") == app.identity
        except (OSError, URLError, ValueError):
            matching = False
        if not matching:
            raise SystemExit(f"Die lokale Adresse {url} ist nicht verfügbar: {error}") from error
        if not args.no_browser:
            webbrowser.open(url)
        return
    with server:
        print(f"LayerLokal-Produktionsleitstelle · {url}", flush=True)
        print("Dieses Fenster geöffnet lassen. Mit Strg+C wird die Leitstelle beendet.", flush=True)
        if not args.no_browser:
            Timer(0.3, webbrowser.open, args=(url,)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

