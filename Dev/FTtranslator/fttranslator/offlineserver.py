#
#   fttranslator/offlineserver
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17.7 - 11/6/26 - Ron Lockwood
#    Transfers through FTApertium, loaded once per bundle (apertiumDll), unless the server was started with the Apertium tools.
#
#   Version 3.17.6 - 11/4/26 - Ron Lockwood
#    Applies the bundle's Text Out rules to the synthesized text, as Collect Output does on the desktop.
#
#   Version 3.17.5 - 11/4/26 - Ron Lockwood
#    Serves several bundles from one folder (a Railway volume), chosen per request, and accepts new bundles by upload (POST /api/bundles/<id>).
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
#   from an exported bundle (see bundle.py): tokenizer.py, hcparse with the parse filer and guesser (analysisguess.py), Extract Source Text (bundleextract.py), the transfer step (transfer.py),
#   Convert Text to Synthesizer Format with HermitCrab synthesis (synthesis.py), and the Text Out rules (textout.py). Nothing is written to any project, so it can listen on every interface of
#   a server.
#
#   SEVERAL BUNDLES
#
#   The server holds a bundles folder (BundleSet), with one sub-folder per bundle; the sub-folder's name is the bundle's id, normally its work project's name (FTT-Scratch, Mato-Uma). On Railway
#   the folder is on a volume mounted at /data, because a container's own files are reset by every deploy, and the bundles of real projects can't be committed to the public repo. The page lists
#   the bundles (GET /api/bundles) and names its choice in every request (?bundle= on GET, "bundle" in the translate body), so two people can use two bundles at once; a request that names
#   none gets the first bundle by name. A bundle is loaded the first time a request uses it and then stays loaded, each costing a running hcparse and its data in memory. The first bundle is
#   loaded at start-up, so a broken image still fails its deploy rather than its first translation.
#
#   New bundles arrive by upload: POST /api/bundles/<id> with the bundle folder's contents as a zip (cli.py's upload-bundle sends one). The zip is unpacked beside the bundles as .incoming-<id>,
#   with absolute paths, .. and oversized contents refused, and must have manifest.json at its top. Then the old folder (if any) is renamed .old-<id>, the new one takes its name, and it is
#   loaded at once; if that fails, the old folder is put back and the upload is answered with the error, so a bad bundle never replaces a working one. The renames happen with the old bundle's
#   translator closed, since its hcparse and temporary files point into the old folder. Folders starting with a period are never listed, which is what keeps the half-done ones out of sight.
#   DELETE /api/bundles/<id> removes one. --seed copies a bundle in at start-up when its id isn't there yet: the image seeds FTT-Scratch from deploy/bundle, so an empty volume still works.
#
#   WHAT IS SET UP ONCE
#
#   OfflineTranslator loads a bundle when it is first used: the lexicon, the tokenizer data, the guesser data, the bilingual lexicon's unlinked senses, the Apertium files (read into FTApertium,
#   or compiled for the Apertium tools with --apertium-tools; see THE TWO WAYS in transfer.py), the synthesis data and the Text Out rules. hcparse is started once and kept running, since starting .NET and loading the parser takes a few seconds and each word after that takes milliseconds;
#   if it dies, the request fails and the next one starts a new one. HermitCrab synthesis is set up once too when --hcsynth-dll is given: HCSynthByGlossDll is loaded into the server with the target
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
#   desktop's (which explains the guesser's ranking): only analysis or best guess. The record also says which bundle it came from ("bundle"). The run records are kept in memory only, per bundle
#   (the last RUNS_KEPT of each), so they are lost when the server restarts; they survive a new upload of the same bundle.
#
#   CLEANUP
#
#   The server always cleans up the synthesized text as CleanUpUnknownTargetWords=y does (synthesis.py's fixUpText()), whatever the bundle's setting: a word that failed shows as its bare
#   lemma (caramelo) instead of %0%^caramelo1.1<n><SG>$%, and sense numbers, @ signs and tags are removed, since the page's readers want text, not diagnostics. The failures aren't lost: the
#   unsynthesized words in the run record are read from the surface forms file, which cleanup doesn't touch. Text HCSynthByGloss appends to a word ("Duplicate gloss(es) found ...") stays, as on
#   the desktop.
#
#   TEXT OUT RULES
#
#   When the bundle has a Text Out rules file (TextOutRulesFile, copied in by bundle.py), it is parsed when the bundle is loaded and applied to the cleaned-up synthesized text, the order Collect
#   Output uses on the desktop: cleanup happens in synthesis, the rules after it. The "N Text Out rules applied." message goes in the run record; a rule that fails fails the translation, as on
#   the desktop, with the desktop's message naming the rule. The unsynthesized words are still read from the surface forms file, which the rules never touch. A bundle exported before rules were
#   exported has no textOutRules entry and gets no rules.
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
#   Uploading and deleting bundles take the same password, unless FTT_UPLOAD_PASSWORD is set too, in which case they take that one instead: then the people who translate can't replace
#   bundles. An upload must be sent as application/zip, which, like JSON, a page on another site can't send without a CORS preflight. Bundle ids are checked (validBundleId()) before any
#   path is built from them, so an id can't reach outside the bundles folder.
#
#   CODE STRUCTURE
#
#   OfflineTranslator holds one bundle and its running tools; translate() runs the chain, ending with the Text Out rules (textout.TextOutRules), and builds the RunResult with _approvedWords(),
#   _describe() and _untranslated(), and close() stops hcparse and removes the temporary folders. BundleSet holds the bundles folder: list(), exists(), get() (loading a translator through the factory it is given), install() for uploads (with
#   _extractBundleZip()), remove(), seed() and the run records; validBundleId() and _readManifest() are its helpers. OfflineServer is the HTTPServer carrying the BundleSet, and
#   OfflineRequestHandler reuses server.RequestHandler's static files and JSON answers, replacing the request dispatch and the _api*() methods. Its do_GET(), do_POST() and do_DELETE() first
#   check the password with _authorized() or _uploadAuthorized(), which use _passwordMatches(), and answer 401 through _sendAuthRequired(); _bundleId() picks the request's bundle. serve()
#   runs the loop for cli.cmdServeOffline(), after _needsPassword() has decided whether it may start without one. _firstWords() is a copy of steps\ingest.py's firstWords(), which can't be
#   imported here because ingest.py needs FieldWorks.
#

import base64
import binascii
import hmac
import io
import json
import re
import shlex
import shutil
import sys
import time
import traceback
import unicodedata
import zipfile
from datetime import datetime
from http.server import HTTPServer
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import parse_qs, unquote, urlparse

from . import analysisguess, bundleextract
from .pipeline import RunResult
from .server import RequestHandler
from .steps.finish import IDENTITY_ENTRY, LEXICAL_UNIT, STAMP_FAILURE, _lemma, _unique
from .synthesis import Synthesizer
from .textout import TextOutRules
from .tokenizer import Tokenizer
from .transfer import Transfer
from .transferexport import APERTIUM_DIR, BILINGUAL_FILE

# The hosts that only this machine can reach; listening on any other needs a password. See SAFETY above.
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")

# The run records kept for /api/runs, per bundle
RUNS_KEPT = 200

# The largest bundle upload accepted, as sent (zipped) and unpacked. A bundle is a few MB; the unpacked limit stops a small zip that unpacks to fill the volume.
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
MAX_UNPACKED_BYTES = 1024 * 1024 * 1024

# A bundle id is a folder name: letters, digits, _ . - and spaces, not starting with a period (those are BundleSet's half-done folders) and not ending with a period or space (Windows drops them)
BUNDLE_ID = re.compile(r"\w(?:[\w .-]{0,78}[\w-])?")

# The API path that a bundle's id follows, for uploading or deleting it
BUNDLES_PATH = "/api/bundles/"

# What a new text's title starts with, as the default profile's title prefix does on the desktop
TITLE_PREFIX = "FTT"

class OfflineTranslator:
    '''A bundle loaded for translating, with hcparse running and the Apertium files loaded or compiled. See WHAT IS SET UP ONCE above.'''

    def __init__(self, bundleDir, hcparseCommand, hcsynthCommand, toolsDir=None, hcsynthDll=None, apertiumDll=None):

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
        self.transfer = Transfer(self.bundleDir, self.manifest["files"]["apertium"]["rules"], toolsDir=toolsDir, apertiumDll=apertiumDll)
        self.synthesizer = Synthesizer(self.bundleDir, hcsynthCommand, hcsynthDll=hcsynthDll)

        # Always clean up, whatever the bundle's CleanUpUnknownTargetWords says. See CLEANUP above.
        self.synthesizer.clean = "y"

        # None when the bundle has no Text Out rules. See TEXT OUT RULES above.
        self.textOutRules = TextOutRules.load(self.bundleDir, self.manifest)

    def close(self):
        '''Stop hcparse and remove the transfer and synthesis folders, so a bundle that is replaced or removed leaves nothing behind. See SEVERAL BUNDLES above.'''

        self.parser.close()

        # Both are temporary folders made for this translator (no workDir is passed to them above); transfer through FTApertium has none
        for workDir in (self.transfer.workDir, self.synthesizer.workDir):

            if workDir is not None:

                shutil.rmtree(workDir, ignore_errors=True)

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

        # The user's fix-ups, after cleanup, as Collect Output applies them. A failing rule leaves translation None. See TEXT OUT RULES above.
        if translation is not None and self.textOutRules is not None:

            translation, textOutMessages = step("Apply Text Out Rules", self.textOutRules.apply, translation)
            messages += textOutMessages

        if translation is not None:

            # Cleanup has taken the failure markers out of the translation, so the failed words come from the surface forms file, which still has them
            surfaceForms = self.synthesizer.surfaceFormsFile.read_text(encoding="utf-8-sig")
            result.translation = translation.strip()
            result.unsynthesized = _unique(STAMP_FAILURE.findall(surfaceForms))
            result.ok = True

        result.messages = [{"level": level, "message": message, "ref": None} for level, message in messages]
        result.totalSeconds = round(time.perf_counter() - started, 3)

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

class BundleNotFound(LookupError):
    '''A request named a bundle that isn't in the bundles folder.'''

class BundleSet:
    '''The bundles folder: one sub-folder per bundle, named by its id, each loaded into an OfflineTranslator when first used. translatorFactory turns a bundle folder into a translator. See
       SEVERAL BUNDLES above.'''

    def __init__(self, root, translatorFactory):

        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.translatorFactory = translatorFactory
        self.loaded = {}

        # Each bundle's run records, newest last; kept here rather than in the translator so they survive a new upload of the bundle
        self.runs = {}

    def list(self):
        '''Each bundle as {id, workProject, sourceProject, targetProject, created}, by id. Folders that aren't valid ids or have no readable manifest.json are left out.'''

        bundles = []

        for folder in sorted(self.root.iterdir(), key=lambda path: path.name.lower()):

            if not folder.is_dir() or not validBundleId(folder.name):

                continue

            manifest = _readManifest(folder)

            if manifest is None:

                continue

            bundles.append({"id": folder.name, "workProject": manifest.get("workProject") or "", "sourceProject": manifest.get("sourceProject") or "",
                            "targetProject": manifest.get("targetProject") or "", "created": manifest.get("created") or ""})

        return bundles

    def defaultId(self):
        '''The bundle a request gets when it names none: the first by id, or None when there are none.'''

        bundles = self.list()

        return bundles[0]["id"] if bundles else None

    def exists(self, bundleId):

        return validBundleId(bundleId) and _readManifest(self.root / bundleId) is not None

    def manifest(self, bundleId):
        '''The bundle's manifest, from the loaded translator if there is one. Raises BundleNotFound.'''

        if bundleId in self.loaded:

            return self.loaded[bundleId].manifest

        manifest = _readManifest(self.root / bundleId) if validBundleId(bundleId) else None

        if manifest is None:

            raise BundleNotFound(bundleId)

        return manifest

    def isLoaded(self, bundleId):

        return bundleId in self.loaded

    def get(self, bundleId):
        '''The bundle's translator, loading it the first time. Raises BundleNotFound, or whatever loading raises (nothing is kept then, so the next request tries again).'''

        if bundleId not in self.loaded:

            if not self.exists(bundleId):

                raise BundleNotFound(bundleId)

            self.loaded[bundleId] = self.translatorFactory(self.root / bundleId)

        return self.loaded[bundleId]

    def addRun(self, bundleId, record):

        self.runs[bundleId] = (self.runs.get(bundleId, []) + [record])[-RUNS_KEPT:]

    def unload(self, bundleId):
        '''Close the bundle's translator, if it is loaded, so its folder can be renamed or removed.'''

        translator = self.loaded.pop(bundleId, None)

        if translator is not None:

            translator.close()

    def install(self, bundleId, zipBytes):
        '''Unpack an uploaded bundle (the bundle folder's contents, zipped) as bundleId, replacing any bundle of that id, and load it. Raises ValueError, saying why, if the id or the zip
           is bad or the new bundle won't load; the old bundle is then left as it was. See SEVERAL BUNDLES above.'''

        if not validBundleId(bundleId):

            raise ValueError(f"Not a usable bundle name: {bundleId!r}. Use letters, digits, spaces, _ . and -.")

        folder = self.root / bundleId
        incoming = self.root / f".incoming-{bundleId}"
        old = self.root / f".old-{bundleId}"

        # Left over if the server stopped part way through an earlier upload
        for leftover in (incoming, old):

            shutil.rmtree(leftover, ignore_errors=True)

        incoming.mkdir()

        try:
            _extractBundleZip(zipBytes, incoming)

            if _readManifest(incoming) is None:

                raise ValueError("The zip has no readable manifest.json at its top level. Zip the contents of the bundle folder, not the folder itself (upload-bundle does this).")

        except Exception:

            shutil.rmtree(incoming, ignore_errors=True)
            raise

        # Swap the folders with the old translator closed, since it points into the old folder
        self.unload(bundleId)
        hadOld = folder.exists()

        if hadOld:

            folder.rename(old)

        incoming.rename(folder)

        try:
            self.get(bundleId)

        except Exception as err:

            # Put the old bundle back; it is loaded again by the next request that uses it
            shutil.rmtree(folder, ignore_errors=True)

            if hadOld:

                old.rename(folder)

            kept = "the old one was kept" if hadOld else "nothing was installed"
            raise ValueError(f"The new bundle didn't load, so {kept}: {err}")

        shutil.rmtree(old, ignore_errors=True)

    def remove(self, bundleId):
        '''Delete a bundle and its run records. Raises BundleNotFound.'''

        if not self.exists(bundleId):

            raise BundleNotFound(bundleId)

        self.unload(bundleId)
        shutil.rmtree(self.root / bundleId)
        self.runs.pop(bundleId, None)

    def seed(self, seedDir):
        '''Copy a bundle folder in, as its work project's name, unless a bundle of that id is already here (an upload is never overwritten). Returns the id, or None if seedDir isn't a bundle.'''

        seedDir = Path(seedDir)
        manifest = _readManifest(seedDir)

        if manifest is None:

            return None

        bundleId = manifest.get("workProject") or seedDir.name

        if not validBundleId(bundleId):

            bundleId = seedDir.name

        if not (self.root / bundleId).exists():

            shutil.copytree(seedDir, self.root / bundleId)

        return bundleId

    def close(self):

        for bundleId in list(self.loaded):

            self.unload(bundleId)

class OfflineServer(HTTPServer):
    '''The HTTPServer, with the BundleSet and the session's state for the request handler to use.'''

    def __init__(self, address, bundles, verbose, password=None, uploadPassword=None):

        super().__init__(address, OfflineRequestHandler)
        self.bundles = bundles
        self.verbose = verbose
        self.translationCount = 0

        # None or empty means no password is asked for; uploads take the page's password unless they have their own. See SAFETY above.
        self.password = password or None
        self.uploadPassword = uploadPassword or self.password

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

        query = parse_qs(url.query)

        if url.path == "/api/status":

            self._apiBundleStatus(query)

        elif url.path == "/api/runs":

            self._apiRuns(query)

        elif url.path == "/api/bundles":

            self._apiBundles()

        elif url.path.startswith("/api/"):

            self._sendError(404, f"No such API: {url.path}")
        else:
            self._static(url.path)

    def do_POST(self):

        path = urlparse(self.path).path

        # Uploads have their own password and content type. See SEVERAL BUNDLES and SAFETY above.
        if path.startswith(BUNDLES_PATH):

            self._apiUpload(unquote(path[len(BUNDLES_PATH):]))
            return

        if not self._authorized():

            self._discardBody()
            self._sendAuthRequired()
            return

        # A page on another site can't send JSON without a CORS preflight, which this server never approves
        if self._contentType() != "application/json":

            self._discardBody()
            self._sendError(415, "Send JSON (Content-Type: application/json)")
            return

        if path != "/api/translate":

            self._discardBody()
            self._sendError(404, f"No such API: {self.path}")
            return

        self._apiTranslate()

    def _discardBody(self, length=None):
        '''Read and throw away the request's body before answering it with an error. Answering without reading it makes the server close the connection while the client is still sending,
           which the client sees as a dropped connection (Windows: WinError 10053) instead of the error. Read in chunks, so nothing is kept; a body over MAX_UPLOAD_BYTES closes the connection.'''

        if length is None:

            try:
                length = int(self.headers.get("Content-Length", "0"))

            except ValueError:

                length = 0

        if length > MAX_UPLOAD_BYTES:

            self.close_connection = True
            return

        while length > 0:

            chunk = self.rfile.read(min(length, 64 * 1024))

            if not chunk:

                break

            length -= len(chunk)

    def do_DELETE(self):

        path = urlparse(self.path).path

        if not self._uploadAuthorized():

            self._sendAuthRequired()
            return

        if not path.startswith(BUNDLES_PATH):

            self._sendError(404, f"No such API: {self.path}")
            return

        bundleId = unquote(path[len(BUNDLES_PATH):])

        try:
            self.offlineServer.bundles.remove(bundleId)

        except BundleNotFound:

            self._sendError(404, f"No such bundle: {bundleId}")
            return

        print(f"Removed the bundle {bundleId}", file=sys.stderr, flush=True)
        self._sendJson({"removed": bundleId})

    def _contentType(self):

        return self.headers.get("Content-Type", "").split(";")[0].strip().lower()

    def _authorized(self):
        '''True if no password is set, or the request's Authorization header carries it. See SAFETY above.'''

        password = self.offlineServer.password

        if password is None:

            return True

        return _passwordMatches(self.headers.get("Authorization", ""), password)

    def _uploadAuthorized(self):
        '''As _authorized(), for uploading and deleting bundles, which take FTT_UPLOAD_PASSWORD when it is set. See SAFETY above.'''

        password = self.offlineServer.uploadPassword

        if password is None:

            return True

        return _passwordMatches(self.headers.get("Authorization", ""), password)

    def _bundleId(self, requested):
        '''The id of the bundle a request names, or of the default bundle when it names none. Answers 404 itself and returns None when there is no such bundle.'''

        bundles = self.offlineServer.bundles
        bundleId = requested or bundles.defaultId()

        if not bundleId:

            self._sendError(404, "There are no bundles on this server yet. Send one with: python -m fttranslator upload-bundle")
            return None

        if not bundles.exists(bundleId):

            self._sendError(404, f"No such bundle: {bundleId}")
            return None

        return bundleId

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

    def _apiBundleStatus(self, query):
        '''GET /api/status for the bundle the query names. Not called _apiStatus because server.py's takes no query.'''

        bundleId = self._bundleId(query.get("bundle", [""])[0])

        if bundleId is None:

            return

        bundles = self.offlineServer.bundles
        manifest = bundles.manifest(bundleId)

        # offline tells the page there are no projects to insert into or keep approvals in, so it hides those options. projectsOpen says whether the bundle is loaded yet.
        self._sendJson({"offline": True, "bundle": bundleId, "workProject": manifest.get("workProject") or "", "sourceProject": manifest.get("sourceProject") or "",
                        "targetProject": manifest.get("targetProject") or "", "projectsOpen": bundles.isLoaded(bundleId), "translationCount": self.offlineServer.translationCount})

    def _apiRuns(self, query):

        try:
            limit = int(query.get("limit", ["50"])[0])

        except ValueError:

            self._sendError(400, "limit must be a number")
            return

        bundleId = self._bundleId(query.get("bundle", [""])[0])

        if bundleId is None:

            return

        records = self.offlineServer.bundles.runs.get(bundleId, [])
        records = records[-limit:] if limit > 0 else []
        self._sendJson({"runs": list(reversed(records))})

    def _apiBundles(self):

        bundles = self.offlineServer.bundles
        self._sendJson({"bundles": bundles.list(), "default": bundles.defaultId()})

    def _apiUpload(self, bundleId):
        '''POST /api/bundles/<id>: install the zipped bundle in the body. See SEVERAL BUNDLES above.'''

        try:
            length = int(self.headers.get("Content-Length", "0"))

        except ValueError:

            self.close_connection = True
            self._sendError(400, "Content-Length must be a number")
            return

        # Too big to read even to throw away; the client may see the connection drop instead of this answer
        if length > MAX_UPLOAD_BYTES:

            self.close_connection = True
            self._sendError(413, f"The upload is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
            return

        if not self._uploadAuthorized():

            self._discardBody(length)
            self._sendAuthRequired()
            return

        # Like JSON, a zip can't be posted from another site's page without a CORS preflight
        if self._contentType() != "application/zip":

            self._discardBody(length)
            self._sendError(415, "Send the bundle as a zip (Content-Type: application/zip)")
            return

        if length <= 0:

            self._sendError(400, "The upload is empty")
            return

        zipBytes = self.rfile.read(length)

        try:
            self.offlineServer.bundles.install(bundleId, zipBytes)

        except ValueError as err:

            self._sendError(400, str(err))
            return

        except Exception as err:

            traceback.print_exc()
            self._sendError(500, f"The upload failed: {err}")
            return

        print(f"Installed the bundle {bundleId}", file=sys.stderr, flush=True)
        manifest = self.offlineServer.bundles.manifest(bundleId)
        self._sendJson({"installed": bundleId, "workProject": manifest.get("workProject") or "", "created": manifest.get("created") or ""})

    def _apiTranslate(self):

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        except (ValueError, UnicodeDecodeError):

            self._sendError(400, "The request body is not valid JSON")
            return

        if not isinstance(body, dict):

            body = {}

        text = body.get("text", "")

        if not isinstance(text, str) or not text.strip():

            self._sendError(400, "There is no text to translate")
            return

        requested = body.get("bundle")
        bundleId = self._bundleId(requested if isinstance(requested, str) else "")

        if bundleId is None:

            return

        # A failure, including a bundle that won't load, is answered as an error rather than stopping the server
        try:
            translator = self.offlineServer.bundles.get(bundleId)
            result = translator.translate(text, insert=bool(body.get("insert")), keepApprovals=bool(body.get("keepApprovals")))

        except Exception as err:

            traceback.print_exc()
            self._sendError(500, f"The translation failed: {err}")
            return

        record = result.toDict()
        record["bundle"] = bundleId
        self.offlineServer.bundles.addRun(bundleId, record)
        self.offlineServer.translationCount += 1
        print(f"{'OK    ' if result.ok else 'FAILED'} [{bundleId}] {result.title}", file=sys.stderr, flush=True)
        self._sendJson({"result": record, "record": None})

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

def validBundleId(bundleId):
    '''True if bundleId can safely be used as a folder name in the bundles folder: no path separators, no .., not hidden. See SAFETY above.'''

    return isinstance(bundleId, str) and BUNDLE_ID.fullmatch(bundleId) is not None

def _readManifest(folder):
    '''A bundle folder's manifest.json as a dict, or None if it is missing or unreadable.'''

    try:
        manifest = json.loads((Path(folder) / "manifest.json").read_text(encoding="utf-8"))

    except (OSError, ValueError):

        return None

    return manifest if isinstance(manifest, dict) else None

def _extractBundleZip(zipBytes, target):
    '''Unpack an uploaded zip into target. Raises ValueError if it isn't a zip, names a path outside target, or unpacks to more than MAX_UNPACKED_BYTES.'''

    try:
        archive = zipfile.ZipFile(io.BytesIO(zipBytes))

    except zipfile.BadZipFile:

        raise ValueError("The upload is not a zip file")

    with archive:

        members = archive.infolist()

        if sum(member.file_size for member in members) > MAX_UNPACKED_BYTES:

            raise ValueError(f"The bundle unpacks to more than {MAX_UNPACKED_BYTES // (1024 * 1024)} MB")

        # extractall() would quietly clean such names up; refusing them says something is wrong with the zip. A colon would be a Windows drive.
        for member in members:

            name = member.filename.replace("\\", "/")

            if name.startswith("/") or ":" in name or ".." in PurePosixPath(name).parts:

                raise ValueError(f"The zip has a path outside the bundle: {member.filename}")

        archive.extractall(target)

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

def serve(bundlesRoot, hcparse, hcsynth, host, port, toolsDir=None, verbose=False, hcsynthDll=None, password=None, seeds=(), uploadPassword=None, apertiumDll=None):
    '''Serve the bundles in bundlesRoot until the process is stopped (Ctrl+C, or the host's stop signal), after copying in each seed bundle folder whose id isn't there yet. hcsynth is the
       HCSynthByGloss command, or hcsynthDll the dll to load instead. apertiumDll is FTApertium's DLL to transfer with, or None for the Apertium tools in toolsDir (or on PATH). password,
       if given, is asked of every request but the health check (uploadPassword, if given, of uploads instead); without one the server only starts on this machine's own address. See
       SEVERAL BUNDLES and SAFETY above.'''

    # Checked before any bundle loads, so a missing password fails at once
    if not password and _needsPassword(host):

        raise SystemExit(f"Set the FTT_PASSWORD environment variable before listening on {host}: without it anyone who can reach the server could use it. (On 127.0.0.1 no password is needed.)")

    hcparseCommand = shlex.split(hcparse, posix=False)
    hcsynthCommand = shlex.split(hcsynth, posix=False) if hcsynth else None

    def makeTranslator(bundleDir):

        print(f"Loading the bundle in {bundleDir} ...", file=sys.stderr, flush=True)

        return OfflineTranslator(bundleDir, hcparseCommand, hcsynthCommand, toolsDir=toolsDir, hcsynthDll=hcsynthDll, apertiumDll=apertiumDll)

    bundles = BundleSet(bundlesRoot, makeTranslator)

    for seedDir in seeds:

        if bundles.seed(seedDir) is None:

            print(f"Not a bundle (no manifest.json), so not copied in: {seedDir}", file=sys.stderr, flush=True)

    # Load the default bundle now, so a broken image fails its deploy rather than its first translation. See SEVERAL BUNDLES above.
    defaultId = bundles.defaultId()

    if defaultId:

        bundles.get(defaultId)

    server = OfflineServer((host, port), bundles, verbose, password=password, uploadPassword=uploadPassword)
    passwordNote = "password required" if password else "no password"
    bundleNote = ", ".join(bundle["id"] for bundle in bundles.list()) or "none yet; send one with upload-bundle"
    print(f"FTtranslator (offline) is at http://{host}:{server.server_address[1]}/  ({passwordNote}; Ctrl+C to stop)", file=sys.stderr, flush=True)
    print(f"Bundles in {bundles.root}: {bundleNote}", file=sys.stderr, flush=True)

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        pass
    finally:
        server.server_close()
        bundles.close()
