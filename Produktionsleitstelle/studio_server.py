"""Startet die LayerLokal-Leitstelle auf der lokalen Loopback-Adresse."""

import argparse
import base64
from datetime import date
from functools import partial
from hashlib import sha256
from html.parser import HTMLParser
import ipaddress
import re
import socket
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
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
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


MOODBOARD = STUDIO / "moodboard"
MOODBOARD_DATA = MOODBOARD / "moodboard.json"
MOODBOARD_IMAGES = MOODBOARD / "bilder"
MOODBOARD_AREAS = {"figuren", "orte", "licht", "bewegung", "marketing"}
MAX_IMAGE = 15 * 1024 * 1024
MAX_PAGE = 3 * 1024 * 1024
BROWSER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/131.0 Safari/537.36 LayerLokal-Leitstelle")

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


# ---------------------------------------------------------------- Moodboard

def image_extension(data):
    """Erkennt erlaubte Bildformate an den ersten Bytes (kein SVG)."""
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[4:12] in (b"ftypavif", b"ftypavis"):
        return ".avif"
    return None


def check_public_url(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("Bitte einen vollständigen Link mit http:// oder https:// einfügen.")
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(parts.hostname, None)}
    except socket.gaierror as error:
        raise ValueError(f"Die Adresse {parts.hostname} wurde nicht gefunden.") from error
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%")[0])
        if not ip.is_global:
            raise ValueError("Links ins lokale Netzwerk sind im Moodboard nicht erlaubt.")


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = build_opener(SafeRedirect)


def fetch(url, limit, referer=None):
    check_public_url(url)
    headers = {"User-Agent": BROWSER_AGENT, "Accept": "image/avif,image/webp,image/*,text/html;q=0.9,*/*;q=0.5"}
    if referer:
        headers["Referer"] = referer
    try:
        with OPENER.open(Request(url, headers=headers), timeout=20) as response:
            kind = (response.headers.get_content_type() or "").lower()
            data = response.read(limit + 1)
            final = response.geturl()
    except URLError as error:
        reason = getattr(error, "reason", error)
        raise ValueError(f"Der Link konnte nicht geladen werden ({reason}).") from error
    if len(data) > limit:
        raise ValueError("Die Datei ist zu groß für das Moodboard (höchstens 15 MB).")
    return data, kind, final


class PageInfo(HTMLParser):
    """Sucht Vorschaubild und Titel einer Webseite (og:image, twitter:image …)."""

    def __init__(self):
        super().__init__()
        self.meta = {}
        self.title = ""
        self.in_title = False
        self.first_image = None

    def handle_starttag(self, tag, attrs):
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag == "meta":
            key = (values.get("property") or values.get("name") or "").lower()
            if key and "content" in values:
                self.meta.setdefault(key, values["content"].strip())
        elif tag == "link" and values.get("rel", "").lower() == "image_src":
            self.meta.setdefault("image_src", values.get("href", ""))
        elif tag == "title":
            self.in_title = True
        elif tag == "img" and not self.first_image:
            source = values.get("src", "")
            if source and not source.startswith("data:"):
                self.first_image = source

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and len(self.title) < 200:
            self.title += data


def image_from_link(url):
    """Lädt ein Bild direkt oder das Vorschaubild einer Webseite."""
    data, kind, final = fetch(url, MAX_IMAGE)
    if image_extension(data):
        return data, ""
    if "html" not in kind and not data.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        raise ValueError("Unter diesem Link liegt weder ein Bild noch eine Webseite.")
    page = PageInfo()
    page.feed(data[:MAX_PAGE].decode("utf-8", errors="replace"))
    title = (page.meta.get("og:title") or page.meta.get("twitter:title") or page.title).strip()
    for candidate in (page.meta.get("og:image"), page.meta.get("og:image:url"),
                      page.meta.get("twitter:image"), page.meta.get("twitter:image:src"),
                      page.meta.get("image_src"), page.first_image):
        if candidate:
            image, _, _ = fetch(urljoin(final, candidate), MAX_IMAGE, referer=final)
            if image_extension(image):
                return image, " ".join(title.split())[:120]
    raise ValueError("Auf dieser Seite wurde kein Vorschaubild gefunden. "
                     "Tipp: Rechtsklick aufs Bild → „Bildadresse kopieren“ oder Bild kopieren und mit Strg+V einfügen.")


def text_field(value, limit):
    return " ".join(str(value or "").split())[:limit]


def clean_tags(value):
    if isinstance(value, str):
        value = value.split(",")
    tags = []
    for tag in value or []:
        tag = text_field(tag, 30).lstrip("#").lower()
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:12]


class Moodboard:
    def __init__(self):
        self.lock = Lock()

    def load(self):
        if MOODBOARD_DATA.is_file():
            return json.loads(MOODBOARD_DATA.read_text(encoding="utf-8"))
        return {"version": 1, "pins": []}

    def save(self, board):
        MOODBOARD.mkdir(exist_ok=True)
        temporary = MOODBOARD_DATA.with_suffix(".tmp")
        temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(MOODBOARD_DATA)

    def add(self, request):
        source = text_field(request.get("quelle"), 1000)
        title = text_field(request.get("titel"), 120)
        if request.get("bild"):
            header, _, payload = str(request["bild"]).partition(",")
            if not header.startswith("data:image/") or ";base64" not in header:
                raise ValueError("Das eingefügte Bild wurde nicht erkannt.")
            data = base64.b64decode(payload, validate=True)
            if len(data) > MAX_IMAGE:
                raise ValueError("Das Bild ist zu groß (höchstens 15 MB).")
        elif request.get("link"):
            link = text_field(request["link"], 2000)
            data, page_title = image_from_link(link)
            source = source or link
            title = title or page_title
        else:
            raise ValueError("Bitte einen Link einfügen oder ein Bild hineinziehen.")
        extension = image_extension(data)
        if not extension:
            raise ValueError("Dieses Bildformat wird nicht unterstützt (JPG, PNG, WebP, GIF oder AVIF).")
        digest = sha256(data).hexdigest()[:16]
        MOODBOARD_IMAGES.mkdir(parents=True, exist_ok=True)
        image = MOODBOARD_IMAGES / (digest + extension)
        if not image.exists():
            image.write_bytes(data)
        area = request.get("bereich") if request.get("bereich") in MOODBOARD_AREAS else "figuren"
        pin = {"id": digest, "bild": "bilder/" + image.name, "titel": title, "quelle": source,
               "bereich": area, "tags": clean_tags(request.get("tags")),
               "notiz": str(request.get("notiz") or "")[:2000], "datum": date.today().isoformat()}
        with self.lock:
            board = self.load()
            if any(existing["id"] == digest for existing in board["pins"]):
                raise ValueError("Dieses Bild ist schon auf dem Moodboard.")
            board["pins"].insert(0, pin)
            self.save(board)
        return pin

    def change(self, request):
        with self.lock:
            board = self.load()
            pin = next((pin for pin in board["pins"] if pin["id"] == request.get("id")), None)
            if not pin:
                raise KeyError(request.get("id"))
            if "titel" in request:
                pin["titel"] = text_field(request["titel"], 120)
            if request.get("bereich") in MOODBOARD_AREAS:
                pin["bereich"] = request["bereich"]
            if "tags" in request:
                pin["tags"] = clean_tags(request["tags"])
            if "notiz" in request:
                pin["notiz"] = str(request["notiz"] or "")[:2000]
            if "quelle" in request:
                pin["quelle"] = text_field(request["quelle"], 1000)
            self.save(board)
            return pin

    def remove(self, request):
        with self.lock:
            board = self.load()
            pin = next((pin for pin in board["pins"] if pin["id"] == request.get("id")), None)
            if not pin:
                raise KeyError(request.get("id"))
            board["pins"].remove(pin)
            self.save(board)
            image = (MOODBOARD / pin["bild"]).resolve()
            if image.is_relative_to(MOODBOARD_IMAGES) and image.is_file():
                image.unlink()
        return {"ok": True}


class Application:
    def __init__(self, output):
        self.output = output
        self.token = secrets.token_urlsafe(24)
        self.identity = sha256(f"studio-v1{ROOT}\0{output}".encode()).hexdigest()
        self.lock = Lock()
        self.job = None
        self.moodboard = Moodboard()

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
            if url.path.startswith("/api/moodboard/"):
                action = {"neu": self.app.moodboard.add, "aendern": self.app.moodboard.change,
                          "loeschen": self.app.moodboard.remove}.get(url.path.rsplit("/", 1)[1])
                if not action:
                    raise LookupError
                length = int(self.headers.get("Content-Length") or 0)
                if length > 25 * 1024 * 1024:
                    raise ValueError("Die Anfrage ist zu groß.")
                request = json.loads(self.rfile.read(length) or b"{}")
                self.json(action(request))
                return
            if url.path == "/api/pull":
                self.app.begin("pull")
            else:
                self.json({"error": "Vorgang nicht gefunden."}, HTTPStatus.NOT_FOUND)
                return
            self.json({"ok": True})
        except (KeyError, FileNotFoundError):
            self.json({"error": "Der Eintrag ist nicht verfügbar."}, HTTPStatus.NOT_FOUND)
        except LookupError:
            self.json({"error": "Vorgang nicht gefunden."}, HTTPStatus.NOT_FOUND)
        except (ValueError, TypeError) as error:
            self.json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
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

