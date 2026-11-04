#
#   fttranslator/offlineserver
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17.4 - 11/4/26 - Ron Lockwood
#    Requires a password (HTTP Basic Auth, from FTT_PASSWORD) for the page and API, and won't listen beyond this machine without one. Added /api/health.
#
#   Version 3.17.3 - 11/4/26 - Ron Lockwood
#    Reports offline in /api/status so the page hides the insert and keep-approvals options.
#
#   Version 3.17.2 - 11/4/26 - Ron Lockwood
#    Can synthesize through HCSynthByGlossDll loaded once in the server (--hcsynth-dll), instead of starting HCSynthByGloss for every text.
#
#   Version 3.17.1 - 11/4/26 - Ron Lockwood
#    Always clean up unknown target words (CleanUpUnknownTargetWords=y), and read the unsynthesized words from the surface forms file.
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. A web server for the React front end that translates from a bundle alone, with no FieldWorks, FLExTrans or Windows: for Linux hosts such as Railway.
#
#   OVERVIEW (AI generated, then edited)
#
#   The serve-offline command's web server. It answers the same JSON API as server.py, so the same React front end (web\dist) works unchanged, but each translation runs the FieldWorks-free chain
#   from an exported bundle (see bundle.py): tokenizer.py, hcparse with the parse filer and guesser (analysisguess.py), Extract Source Text (bundleextract.py), the Apertium tools (transfer.py),
#   and Convert Text to Synthesizer Format with HermitCrab synthesis (synthesis.py). Nothing is written to any project, so it can listen on every interface of a server.
#
#   WHAT IS SET UP ONCE
#
#   OfflineTranslator loads the bundle when the server starts: the lexicon, the tokenizer data, the guesser data, the bilingual lexicon's unlinked senses, the compiled Apertium files and the
#   synthesis data. hcparse is started once and kept running, since starting .NET and loading the parser takes a few seconds and each word after that takes milliseconds; if it dies, the request
#   fails and the next one starts a new one. HermitCrab synthesis is set up once too when --hcsynth-dll is given: HCSynthByGlossDll is loaded into the server with the target
#   HermitCrab config, as FLExTrans' Live Rule Tester keeps it, so a text no longer pays for starting .NET and reading the config (see EXE OR DLL in synthesis.py). With --hcsynth instead,
#   HCSynthByGloss is started once per text, as FLExTrans' Synthesize Text module does.
#
#   EACH TRANSLATION STARTS FROM THE BUNDLE
#
#   Each request gets a fresh Guesser made from the bundle's guesser data, so one text's parses and guesses never affect the next text. That matches the desktop's default (approvals are released
#   after each run, see ingest.py); what the desktop does keep - parser analyses filed in earlier runs - the parser re-files here anyway. The insert and keepApprovals options have no meaning
#   without the projects: /api/status answers offline: true so the page hides them, and a caller that sends them anyway gets a warning in the run record and has them ignored. So the translation of a text only changes when a new bundle is exported and deployed.
#
#   THE RUN RECORD
#
#   The answer is the desktop's run record (pipeline.RunResult), filled in from what the offline steps know: the approved words with the analysis as morph:gloss pairs and the category, the
#   words with no parse or no analysis, the untranslated and unsynthesized words found as steps\finish.py finds them, the messages, and each step's time. The approval basis is simpler than the
#   desktop's (which explains the guesser's ranking): only analysis or best guess. The run records are kept in memory only (the last RUNS_KEPT), so they are lost when the server restarts.
#
#   CLEANUP
#
#   The server always cleans up the synthesized text as CleanUpUnknownTargetWords=y does (synthesis.py's fixUpText()), whatever the bundle's setting: a word that failed shows as its bare
#   lemma (caramelo) instead of %0%^caramelo1.1<n><SG>$%, and sense numbers, @ signs and tags are removed, since the page's readers want text, not diagnostics. The failures aren't lost: the
#   unsynthesized words in the run record are read from the surface forms file, which cleanup doesn't touch. Text HCSynthByGloss appends to a word ("Duplicate gloss(es) found ...") stays, as on
#   the desktop.
#
#   NOT DONE HERE
#
#   Text Out rules (TextOutRulesFile, applied by Collect Output on the desktop) aren't in the bundle yet, so a project that has some gets the synthesized text without them.
#
#   SAFETY
#
#   There is no Host check and no localhost-only binding, unlike server.py, since nothing here can change a project. POST still has to send JSON. But the bundle's lexicon can be worked out from
#   the translations, so the page and the API need a password when one is set: HTTP Basic Auth, with the password from the FTT_PASSWORD environment variable (read by cli.cmdServeOffline()).
#   The browser shows its own login box and then sends the password with every request from the page, so the React front end needs no change. Any user name is accepted; only the password counts,
#   and it is compared with hmac.compare_digest so the time taken doesn't hint at how much of it was right. Basic Auth sends the password readably, which is fine behind Railway's HTTPS but not on
#   plain HTTP across a network.
#
#   Two rules keep this from being forgotten or getting in the way. serve() refuses to start when it would listen beyond this machine (any host but 127.0.0.1, localhost or ::1) with no password,
#   so a Railway service missing FTT_PASSWORD fails its deploy instead of putting the lexicon on the internet. And GET /api/health answers {ok: true} without a password, because Railway's health
#   check (railway.toml) sends none; it says nothing about the projects, unlike /api/status.
#
#   CODE STRUCTURE
#
#   OfflineTranslator holds the bundle and the running tools; translate() runs the chain and builds the RunResult with _approvedWords(), _describe() and _untranslated(). OfflineServer is the
#   HTTPServer carrying it, and OfflineRequestHandler reuses server.RequestHandler's static files and JSON answers, replacing the request dispatch and the three _api*() methods; its do_GET() and
#   do_POST() first check the password with _authorized(), which uses _passwordMatches(), and answer 401 through _sendAuthRequired(). serve() runs the loop for cli.cmdServeOffline(), after
#   _needsPassword() has decided whether it may start without one. _firstWords() is a copy of steps\ingest.py's firstWords(), which can't be imported here because ingest.py needs FieldWorks.
#

import base64
import binascii
import hmac
import json
import shlex
import sys
import time
import traceback
import unicodedata
from datetime import datetime
from http.server import HTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

from . import analysisguess, bundleextract
from .pipeline import RunResult
from .server import RequestHandler
from .steps.finish import IDENTITY_ENTRY, LEXICAL_UNIT, STAMP_FAILURE, _lemma, _unique
from .synthesis import Synthesizer
from .tokenizer import Tokenizer
from .transfer import Transfer
from .transferexport import APERTIUM_DIR, BILINGUAL_FILE

# The hosts that only this machine can reach; listening on any other needs a password. See SAFETY above.
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")

# The run records kept for /api/runs
RUNS_KEPT = 200

# What a new text's title starts with, as the default profile's title prefix does on the desktop
TITLE_PREFIX = "FTT"

class OfflineTranslator:
    '''A bundle loaded for translating, with hcparse running and the Apertium files compiled. See WHAT IS SET UP ONCE above.'''

    def __init__(self, bundleDir, hcparseCommand, hcsynthCommand, toolsDir=None, hcsynthDll=None):

        self.bundleDir = Path(bundleDir)
        self.manifest = json.loads((self.bundleDir / "manifest.json").read_text(encoding="utf-8"))
        self.lexicon = bundleextract.Lexicon.load(self.bundleDir)
        self.tokenizer = Tokenizer.load(self.bundleDir)
        self.guesserData = json.loads((self.bundleDir / analysisguess.GUESSER_FILE).read_text(encoding="utf-8"))

        # Source senses with no link to a target sense: steps\finish.py's identity entries in the bilingual lexicon
        bilingualText = (self.bundleDir / APERTIUM_DIR / BILINGUAL_FILE).read_text(encoding="utf-8")
        self.unlinked = set(IDENTITY_ENTRY.findall(bilingualText))

        self.hcparseCommand = list(hcparseCommand)
        self.parser = analysisguess.HCParseProcess(self.hcparseCommand, self.bundleDir)
        self.transfer = Transfer(self.bundleDir, self.manifest["files"]["apertium"]["rules"], toolsDir=toolsDir)
        self.synthesizer = Synthesizer(self.bundleDir, hcsynthCommand, hcsynthDll=hcsynthDll)

        # Always clean up, whatever the bundle's CleanUpUnknownTargetWords says. See CLEANUP above.
        self.synthesizer.clean = "y"
        self.runs = []

    def close(self):

        self.parser.close()

    def translate(self, text, insert=False, keepApprovals=False):
        '''Translate a text with the whole offline chain and return its RunResult. See EACH TRANSLATION STARTS FROM THE BUNDLE above.'''

        started = time.perf_counter()
        result = RunResult(source=text)
        paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
        result.title = f"{TITLE_PREFIX} {datetime.now().strftime('%Y-%m-%d %H%M%S')} {_firstWords(paragraphs, 3)}"
        messages = []

        if insert or keepApprovals:

            messages.append(("warning", "Inserting the translation and keeping approvals need the FLEx projects, so the offline translator ignores them."))

        # Each step is timed as pipeline.run() times the desktop's
        def step(name, func, *args):

            stepStarted = time.perf_counter()
            value = func(*args)
            result.steps.append(name)
            result.timings.append({"step": name, "seconds": round(time.perf_counter() - stepStarted, 3)})

            return value

        guesser = analysisguess.Guesser(self.guesserData, self.lexicon)
        textDump = step("Import Text", self.tokenizer.tokenizeText, text, result.title)

        try:
            result.unparsed = step("Parse Words", analysisguess.parseAndFile, textDump, guesser, self.parser)

        except Exception:

            # hcparse has probably died; the next request starts a new one
            self.parser = analysisguess.HCParseProcess(self.hcparseCommand, self.bundleDir)
            raise

        planned = step("Approve Guesses", analysisguess.applyGuesses, textDump, guesser)
        result.approved, result.unanalysed = self._approvedWords(textDump, planned, guesser, result.title)
        sourceStream, extractMessages = step("Extract Source Text", bundleextract.extractText, textDump, self.lexicon)
        messages += extractMessages
        targetStream = step("Run Apertium", self.transfer.transfer, sourceStream)
        result.untranslated = self._untranslated(sourceStream, targetStream)
        translation, synthMessages = step("Synthesize Text", self.synthesizer.synthesize, targetStream)
        messages += synthMessages

        if translation is not None:

            # Cleanup has taken the failure markers out of the translation, so the failed words come from the surface forms file, which still has them
            surfaceForms = self.synthesizer.surfaceFormsFile.read_text(encoding="utf-8-sig")
            result.translation = translation.strip()
            result.unsynthesized = _unique(STAMP_FAILURE.findall(surfaceForms))
            result.ok = True

        result.messages = [{"level": level, "message": message, "ref": None} for level, message in messages]
        result.totalSeconds = round(time.perf_counter() - started, 3)
        self.runs = (self.runs + [result.toDict()])[-RUNS_KEPT:]

        return result

    def _approvedWords(self, textDump, planned, guesser, title):
        '''The approved words as {word, location, analysis, basis}, and the words left without an analysis, as the Approve Guesses step records them on the desktop.'''

        # Each word's position: its paragraph, its sentence within the paragraph and its place in the sentence (punctuation counts, as in FLEx's segments), all from 1
        positions = {}
        segmentCounts = {}
        firstSegs = {}

        for occurrence in textDump["occurrences"]:

            firstSegs.setdefault(occurrence["para"], occurrence["seg"])
            segmentCounts[occurrence["seg"]] = segmentCounts.get(occurrence["seg"], 0) + 1
            positions[id(occurrence)] = f"{title} ¶{occurrence['para'] + 1} s{occurrence['seg'] - firstSegs[occurrence['para']] + 1} w{segmentCounts[occurrence['seg']]}"

        approved = []
        approvedIds = set()

        for occurrence, guess in planned:

            choices = len(guesser.wordforms.get(guesser.owner[guess["guid"]], {}).get("analyses", []))
            approved.append({"word": occurrence["baseline"], "location": positions[id(occurrence)], "analysis": self._describe(guess), "basis": "only analysis" if choices < 2 else "best guess"})
            approvedIds.add(id(occurrence))

        unanalysed = [occurrence["baseline"] for occurrence in textDump["occurrences"] if "punct" not in occurrence and id(occurrence) not in approvedIds]

        return approved, unanalysed

    def _describe(self, analysis):
        '''An analysis as 'mang:eat + e:PRS.3SG [v]', as parse_priority's describe() shows one: each morph with its gloss, then the stem's category.'''

        parts = []
        category = ""

        for morphBundle in analysis["bundles"]:

            msa = self.lexicon.msas.get(morphBundle["msa"] or "", {})
            sense = self.lexicon.senses.get(morphBundle["sense"] or msa.get("sense") or "", {})
            parts.append(f"{morphBundle['text']}:{sense.get('gloss') or '?'}")

            if msa.get("stem") and msa.get("pos") and not category:

                category = f" [{msa['pos']}]"

        return (" + ".join(parts) or "(no morphemes)") + category

    def _untranslated(self, sourceStream, targetStream):
        '''Words marked @ in the transfer results, then source words whose sense has no link to the target lexicon, as steps\\finish.py's collectOutput() lists them.'''

        noEntry = [_lemma(unit) for unit in LEXICAL_UNIT.findall(targetStream) if unit.startswith("@")]
        noLink = [_lemma(unit) for unit in LEXICAL_UNIT.findall(sourceStream) if _lemma(unit) in self.unlinked]

        return _unique(noEntry + noLink)

class OfflineServer(HTTPServer):
    '''The HTTPServer, with the OfflineTranslator and the session's state for the request handler to use.'''

    def __init__(self, address, translator, verbose, password=None):

        super().__init__(address, OfflineRequestHandler)
        self.translator = translator
        self.verbose = verbose
        self.translationCount = 0

        # None or empty means no password is asked for. See SAFETY above.
        self.password = password or None

class OfflineRequestHandler(RequestHandler):
    '''server.py's handler with the offline translator behind the API. The static files and the JSON answers are server.py's.'''

    @property
    def offlineServer(self) -> OfflineServer:
        '''The server this handler belongs to. OfflineServer is the only server that creates this handler, so the cast is safe.'''

        return cast(OfflineServer, self.server)

    def do_GET(self):

        url = urlparse(self.path)

        # The health check is the one path open without the password. See SAFETY above.
        if url.path == "/api/health":

            self._sendJson({"ok": True})
            return

        if not self._authorized():

            self._sendAuthRequired()
            return

        if url.path == "/api/status":

            self._apiStatus()

        elif url.path == "/api/runs":

            self._apiRuns(parse_qs(url.query))

        elif url.path.startswith("/api/"):

            self._sendError(404, f"No such API: {url.path}")
        else:
            self._static(url.path)

    def do_POST(self):

        if not self._authorized():

            self._sendAuthRequired()
            return

        # A page on another site can't send JSON without a CORS preflight, which this server never approves
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":

            self._sendError(415, "Send JSON (Content-Type: application/json)")
            return

        if urlparse(self.path).path != "/api/translate":

            self._sendError(404, f"No such API: {self.path}")
            return

        self._apiTranslate()

    def _authorized(self):
        '''True if no password is set, or the request's Authorization header carries it. See SAFETY above.'''

        password = self.offlineServer.password

        if password is None:

            return True

        return _passwordMatches(self.headers.get("Authorization", ""), password)

    def _sendAuthRequired(self):
        '''Answer 401 with the WWW-Authenticate header that makes the browser show its login box. Written out like _sendJson(), which has no way to add a header.'''

        content = json.dumps({"error": "This page needs the password"}).encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="FTtranslator", charset="UTF-8"')
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _apiStatus(self):

        manifest = self.offlineServer.translator.manifest

        # offline tells the page there are no projects to insert into or keep approvals in, so it hides those options
        self._sendJson({"offline": True,"workProject": manifest.get("workProject") or "", "sourceProject": manifest.get("sourceProject") or "", "targetProject": manifest.get("targetProject") or "",
                        "projectsOpen": True, "translationCount": self.offlineServer.translationCount})

    def _apiRuns(self, query):

        try:
            limit = int(query.get("limit", ["50"])[0])

        except ValueError:

            self._sendError(400, "limit must be a number")
            return

        records = self.offlineServer.translator.runs[-limit:] if limit > 0 else []
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

        # A failure is answered as an error rather than stopping the server
        try:
            result = self.offlineServer.translator.translate(text, insert=bool(body.get("insert")), keepApprovals=bool(body.get("keepApprovals")))

        except Exception as err:

            traceback.print_exc()
            self._sendError(500, f"The translation failed: {err}")
            return

        self.offlineServer.translationCount += 1
        print(f"{'OK    ' if result.ok else 'FAILED'} {result.title}", file=sys.stderr, flush=True)
        self._sendJson({"result": result.toDict(), "record": None})

def _passwordMatches(authorization, password):
    '''True if an Authorization header ("Basic " then base64 of user:password) carries this password. Any user name is accepted. A header that isn't Basic or doesn't decode is a mismatch.'''

    scheme, _, encoded = authorization.partition(" ")

    if scheme.lower() != "basic":

        return False

    try:
        decoded = base64.b64decode(encoded.strip(), validate=True).decode("utf-8")

    except (binascii.Error, UnicodeDecodeError):

        return False

    # The password is everything after the first colon, so it may itself contain colons
    _, colon, given = decoded.partition(":")

    if not colon:

        return False

    return hmac.compare_digest(given.encode("utf-8"), password.encode("utf-8"))

def _needsPassword(host):
    '''True if listening on this host would let other machines reach the server, so it must not start without a password. See SAFETY above.'''

    return host.strip("[]").lower() not in LOOPBACK_HOSTS

def _firstWords(paragraphs, count):
    '''The first count words of the text, without the punctuation that ends the last one. A copy of steps\\ingest.py's firstWords(); see CODE STRUCTURE above.'''

    words = " ".join(paragraphs).split()[:count]
    snippet = " ".join(words)

    while snippet and unicodedata.category(snippet[-1]).startswith("P"):

        snippet = snippet[:-1]

    return snippet

def serve(bundleDir, hcparse, hcsynth, host, port, toolsDir=None, verbose=False, hcsynthDll=None, password=None):
    '''Load the bundle and answer requests until the process is stopped (Ctrl+C, or the host's stop signal). hcsynth is the HCSynthByGloss command, or hcsynthDll the dll to load instead.
       password, if given, is asked of every request but the health check; without one the server only starts on this machine's own address. See SAFETY above.'''

    # Checked before the bundle loads, so a missing password fails at once
    if not password and _needsPassword(host):

        raise SystemExit(f"Set the FTT_PASSWORD environment variable before listening on {host}: without it anyone who can reach the server could use it. (On 127.0.0.1 no password is needed.)")

    print(f"Loading the bundle in {bundleDir} ...", file=sys.stderr, flush=True)
    hcsynthCommand = shlex.split(hcsynth, posix=False) if hcsynth else None
    translator = OfflineTranslator(bundleDir, shlex.split(hcparse, posix=False), hcsynthCommand, toolsDir=toolsDir, hcsynthDll=hcsynthDll)
    server = OfflineServer((host, port), translator, verbose, password=password)
    passwordNote = "password required" if password else "no password"
    print(f"FTtranslator (offline) for {translator.manifest.get('workProject') or bundleDir} is at http://{host}:{server.server_address[1]}/  ({passwordNote}; Ctrl+C to stop)", file=sys.stderr, flush=True)

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        pass
    finally:
        server.server_close()
        translator.close()
