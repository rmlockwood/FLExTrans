#
#   fttranslator/server
#
#   Ron Lockwood
#   SIL International
#   10/30/26
#
#   Version 3.17 - 10/30/26 - Ron Lockwood
#    Initial version. A local web server for the React front end, keeping the projects open between translations.
#
#   OVERVIEW (AI generated, then edited)
#
#   The serve command's web server. It holds one Translator for its whole life, as the interactive command does, so the projects are opened once and each translation after the first takes
#   about half a second. It answers a small JSON API under /api and serves the built React front end (web\dist) for every other path, so the user runs one command and opens one browser tab.
#
#   THE API
#
#    - GET  /api/status      the work project, the source and target projects, whether the projects are open yet, and how many texts this session has translated.
#    - POST /api/translate   body {text, insert, keepApprovals}; translates the text and answers {result, record}: the run record (RunResult.toDict()) and where it was saved.
#    - GET  /api/runs        the saved run records, newest first (?limit=N, default 50).
#   An error answers {error: message} with status 400 (bad request) or 500 (the translation itself failed with an exception).
#
#   ONE REQUEST AT A TIME, ON ONE THREAD
#
#   FieldWorks objects belong to the thread that opened the project, and a run changes the source project and the FLExTrans build files, so two translations must never overlap. The server is
#   the standard library's single-threaded HTTPServer, driven by handle_request() on the main thread: requests queue and are answered in turn. That is also why there is no threading or async
#   framework here - nothing would be gained, since the translations can't run side by side anyway.
#
#   STOPPING
#
#   Ctrl+C in the console stops the server. It only asks to stop (cli.CtrlCStopper), and the loop checks between requests - handle_request() wakes every half second even when idle - so a
#   translation in progress finishes, and the projects are saved and closed when the Translator's with block in cli.cmdServe() ends.
#
#   SAFETY
#
#   The server listens on 127.0.0.1 only. A translation writes to the FLEx projects, so two checks keep other web pages the browser has open from triggering one: POST must send
#   Content-Type: application/json, which a page on another site can't do without a CORS preflight this server never approves, and the Host header must be localhost or 127.0.0.1, which defeats
#   DNS rebinding (an attacker's host name pointed at 127.0.0.1).
#
#   CODE STRUCTURE
#
#   FTServer is the HTTPServer, carrying the Translator and the session's state. RequestHandler answers each request, reaching the FTServer through its ftServer property: do_GET() and do_POST()
#   dispatch to the _api*() methods or _static(), and _sendJson() and _sendError() write the answers. serve() runs the loop for cli.cmdServe(). _hostAllowed() is the DNS-rebinding check, and STATIC_TYPES fixes the content types of the built
#   files.
#

import json
import sys
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

from .cli import CtrlCStopper, silenceTools, stdoutToStderr
from .pipeline import Options
from .report import makeReporter

# The built front end, from npm run build in the web folder
WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"

# Set explicitly: Windows takes content types from the registry, which sometimes maps .js to text/plain, and browsers refuse to run a module script served that way
STATIC_TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
                ".ico": "image/x-icon", ".json": "application/json; charset=utf-8", ".woff2": "font/woff2"}

class FTServer(HTTPServer):
    '''The HTTPServer, with the Translator and the session's state for the request handler to use.'''

    def __init__(self, address, translator, verbose):

        super().__init__(address, RequestHandler)
        self.translator = translator
        self.verbose = verbose
        self.translationCount = 0

        # Read once: the projects don't change while the server runs
        import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

        report = makeReporter(False)
        configMap = translator.readConfig(report)
        self.targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False) or ""

class RequestHandler(BaseHTTPRequestHandler):
    '''Answers one request. See THE API above.'''

    @property
    def ftServer(self) -> FTServer:
        '''The server this handler belongs to, with the Translator. The handler's own server attribute is typed as a plain BaseServer; FTServer is the only server that creates this
           handler, so the cast is safe.'''

        return cast(FTServer, self.server)

    def log_message(self, format, *args):

        # The default writes every request to stderr; only the verbose console wants that
        if self.ftServer.verbose:

            super().log_message(format, *args)

    def do_GET(self):

        if not _hostAllowed(self.headers.get("Host", "")):

            self._sendError(403, "Forbidden host")
            return

        url = urlparse(self.path)

        if url.path == "/api/status":

            self._apiStatus()

        elif url.path == "/api/runs":

            self._apiRuns(parse_qs(url.query))

        elif url.path.startswith("/api/"):

            self._sendError(404, f"No such API: {url.path}")
        else:
            self._static(url.path)

    def do_POST(self):

        if not _hostAllowed(self.headers.get("Host", "")):

            self._sendError(403, "Forbidden host")
            return

        # See SAFETY above
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":

            self._sendError(415, "Send JSON (Content-Type: application/json)")
            return

        if urlparse(self.path).path != "/api/translate":

            self._sendError(404, f"No such API: {self.path}")
            return

        self._apiTranslate()

    def _apiStatus(self):

        translator = self.ftServer.translator
        self._sendJson({"workProject": translator.env.workDir.name, "sourceProject": translator.profile.sourceProject, "targetProject": self.ftServer.targetProject,
                        "projectsOpen": translator.sourceDb is not None, "translationCount": self.ftServer.translationCount})

    def _apiRuns(self, query):

        try:
            limit = int(query.get("limit", ["50"])[0])

        except ValueError:

            self._sendError(400, "limit must be a number")
            return

        records = self.ftServer.translator.runs()[-limit:] if limit > 0 else []
        self._sendJson({"runs": list(reversed(records))})

    def _apiTranslate(self):

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        except (ValueError, UnicodeDecodeError):

            self._sendError(400, "The request body is not valid JSON")
            return

        text = body.get("text", "") if isinstance(body, dict) else ""

        if not isinstance(text, str) or not text.strip():

            self._sendError(400, "There is no text to translate")
            return

        options = Options(insert=bool(body.get("insert")), keepApprovals=bool(body.get("keepApprovals")))

        # The output of make and STAMP goes nowhere, as in the interactive command, unless --verbose asks to see it in the console. A failure is answered as an error rather than stopping the server.
        try:
            with stdoutToStderr() if self.ftServer.verbose else silenceTools():

                result = self.ftServer.translator.translate(text, options)

        except (Exception, SystemExit) as err:

            traceback.print_exc()
            self._sendError(500, f"The translation failed: {err}")
            return

        self.ftServer.translationCount += 1
        print(f"{'OK    ' if result.ok else 'FAILED'} {result.title}", file=sys.stderr, flush=True)
        self._sendJson({"result": result.toDict(), "record": result.record})

    def _static(self, path):
        '''Serve a file of the built front end. Any path that isn't a file gets index.html, so the page loads whatever the address.'''

        if not WEB_DIST.is_dir():

            self._sendError(404, f"The front end isn't built. In {WEB_DIST.parent} run: npm install, then npm run build")
            return

        # Resolve within web\dist only, so ..\ in the path can't reach other files
        target = (WEB_DIST / path.lstrip("/")).resolve()

        if not target.is_relative_to(WEB_DIST) or not target.is_file():

            target = WEB_DIST / "index.html"

        content = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", STATIC_TYPES.get(target.suffix.lower(), "application/octet-stream"))
        self.send_header("Content-Length", str(len(content)))

        # index.html must always be fetched fresh so a rebuild shows up; the hashed asset files never change
        self.send_header("Cache-Control", "no-cache" if target.name == "index.html" else "max-age=31536000, immutable")
        self.end_headers()
        self.wfile.write(content)

    def _sendJson(self, data, status=200):

        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _sendError(self, status, message):

        self._sendJson({"error": message}, status)

def _hostAllowed(host):
    '''True if the Host header names this machine. See SAFETY above.'''

    hostName = host.rsplit(":", 1)[0] if not host.startswith("[") else host.split("]")[0] + "]"

    return hostName in ("localhost", "127.0.0.1", "[::1]")

def serve(translator, port, verbose=False, openBrowser=True):
    '''Answer requests until Ctrl+C, keeping the Translator's projects open throughout. See STOPPING above.'''

    server = FTServer(("127.0.0.1", port), translator, verbose)

    # handle_request() gives up after this many seconds with nothing to do, so a Ctrl+C is noticed promptly
    server.timeout = 0.5
    address = f"http://localhost:{server.server_address[1]}/"
    ctrlC = CtrlCStopper()

    print(f"FTtranslator for {translator.env.workDir.name} is at {address}  (Ctrl+C to stop)", file=sys.stderr, flush=True)

    if openBrowser:

        webbrowser.open(address)

    try:
        while not ctrlC.requested:

            server.handle_request()

    finally:
        ctrlC.restore()
        server.server_close()

    print(f"\nTranslated {server.translationCount} text(s).", file=sys.stderr)
