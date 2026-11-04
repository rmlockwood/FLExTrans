#
#   tests/test_offlineserver
#
#   Ron Lockwood
#   SIL International
#   11/4/26
#
#   Version 3.17.1 - 11/4/26 - Ron Lockwood
#    Tests the bundles folder: bundle ids, listing, loading, uploads (including bad zips and a bundle that won't load), seeding and removing.
#
#   Version 3.17 - 11/4/26 - Ron Lockwood
#    Initial version. Tests the offline server's password check.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for the offline server's password (see SAFETY in offlineserver.py) and its bundles folder (see SEVERAL BUNDLES). They need no real bundle, hcparse or HCSynthByGloss: the header
#   check and the start-up rule are plain functions, BundleSet is given a factory that makes FakeTranslator (a stand-in with only the manifest, and a note of whether it was closed), and the
#   request tests run a real OfflineServer on a free local port over a temporary bundles folder of fake bundles, each just a manifest.json. Run them from Dev\FTtranslator with
#   python -m unittest discover -s tests.
#
#   CODE STRUCTURE
#
#   basicHeader(), makeBundle() and zipOf() build test data. TestPasswordMatches covers _passwordMatches() on good, wrong and malformed Authorization headers. TestNeedsPassword covers
#   _needsPassword(). TestBundleIds covers validBundleId(). TestBundleSet covers BundleSet directly: listing, lazy loading, install() (new, replacing, and the refusals), seed() and remove().
#   TestRequests starts an OfflineServer on a thread and checks which requests are answered 200 and which 401, with and without a password set, plus /api/bundles and an upload over HTTP.
#

import base64
import io
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# The package is one folder up from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import offlineserver  # noqa: E402

def basicHeader(user, password):
    '''An Authorization header value for HTTP Basic Auth.'''

    return "Basic " + base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")

def makeBundle(folder, workProject, extra=None):
    '''A fake bundle: a folder with just a manifest.json naming its work project, and any extra files ({relative path: text}).'''

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps({"workProject": workProject, "sourceProject": "Src", "targetProject": "Tgt", "created": "2026-11-04T12:00:00"}), encoding="utf-8")

    for name, text in (extra or {}).items():

        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")

    return folder

def zipOf(files):
    '''A zip, as bytes, holding {name in the zip: text}.'''

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as archive:

        for name, text in files.items():

            archive.writestr(name, text)

    return buffer.getvalue()

def manifestText(workProject):

    return json.dumps({"workProject": workProject, "sourceProject": "Src", "targetProject": "Tgt"})

class FakeTranslator:
    '''Just enough of OfflineTranslator for BundleSet and /api/status: the bundle's manifest, and whether close() was called. A manifest with "fail": true makes loading fail.'''

    def __init__(self, bundleDir):

        self.bundleDir = Path(bundleDir)
        self.manifest = json.loads((self.bundleDir / "manifest.json").read_text(encoding="utf-8"))
        self.closed = False

        if self.manifest.get("fail"):

            raise RuntimeError("this bundle is broken")

    def close(self):

        self.closed = True

def makeRoot(testCase):
    '''A temporary bundles folder for one test, removed when the test ends.'''

    tempDir = tempfile.TemporaryDirectory()
    testCase.addCleanup(tempDir.cleanup)

    return Path(tempDir.name)

class TestPasswordMatches(unittest.TestCase):

    def testRightPassword(self):

        self.assertTrue(offlineserver._passwordMatches(basicHeader("anyone", "s3cret"), "s3cret"))

    def testAnyUserName(self):

        self.assertTrue(offlineserver._passwordMatches(basicHeader("", "s3cret"), "s3cret"))

    def testPasswordWithColonsAndNonAscii(self):

        self.assertTrue(offlineserver._passwordMatches(basicHeader("u", "a:b:ñ"), "a:b:ñ"))

    def testWrongPassword(self):

        self.assertFalse(offlineserver._passwordMatches(basicHeader("u", "wrong"), "s3cret"))

    def testMalformedHeaders(self):

        for header in ("", "Bearer abc", "Basic", "Basic !!!notbase64", "Basic " + base64.b64encode(b"nocolon").decode("ascii"), "Basic " + base64.b64encode(b"u:\xff").decode("ascii")):

            with self.subTest(header=header):

                self.assertFalse(offlineserver._passwordMatches(header, "s3cret"))

class TestNeedsPassword(unittest.TestCase):

    def testLoopbackHosts(self):

        for host in ("127.0.0.1", "localhost", "LOCALHOST", "::1", "[::1]"):

            with self.subTest(host=host):

                self.assertFalse(offlineserver._needsPassword(host))

    def testOtherHosts(self):

        for host in ("0.0.0.0", "::", "192.168.1.5"):

            with self.subTest(host=host):

                self.assertTrue(offlineserver._needsPassword(host))

    def testServeRefusesWithoutPassword(self):

        # Refused before the bundle is touched, so a bundle folder that doesn't exist is fine
        with self.assertRaises(SystemExit):

            offlineserver.serve(Path("no-such-bundle"), "hcparse", "hcsynth", "0.0.0.0", 0)

class TestBundleIds(unittest.TestCase):

    def testGoodIds(self):

        for bundleId in ("FTT-Scratch", "Mato-Uma", "a", "Toma Zialo", "fa_bcc.v2", "Français"):

            with self.subTest(bundleId=bundleId):

                self.assertTrue(offlineserver.validBundleId(bundleId))

    def testBadIds(self):

        for bundleId in ("", ".", "..", ".incoming-x", "a/b", "a\\b", "../x", "x.", "x ", " x", "C:x", "a" * 81, None):

            with self.subTest(bundleId=bundleId):

                self.assertFalse(offlineserver.validBundleId(bundleId))

class TestBundleSet(unittest.TestCase):

    def setUp(self):

        self.root = makeRoot(self)
        self.bundles = offlineserver.BundleSet(self.root, FakeTranslator)

    def testListSkipsNonBundles(self):

        makeBundle(self.root / "Zeta", "Zeta")
        makeBundle(self.root / "alpha", "Alpha")
        makeBundle(self.root / ".old-alpha", "Alpha")
        (self.root / "empty").mkdir()
        (self.root / "notes.txt").write_text("x", encoding="utf-8")
        self.assertEqual([bundle["id"] for bundle in self.bundles.list()], ["alpha", "Zeta"])
        self.assertEqual(self.bundles.defaultId(), "alpha")

    def testNoBundles(self):

        self.assertEqual(self.bundles.list(), [])
        self.assertIsNone(self.bundles.defaultId())

    def testGetLoadsOnce(self):

        makeBundle(self.root / "A", "A")
        self.assertFalse(self.bundles.isLoaded("A"))
        first = self.bundles.get("A")
        self.assertTrue(self.bundles.isLoaded("A"))
        self.assertIs(self.bundles.get("A"), first)

    def testGetUnknown(self):

        for bundleId in ("Missing", "../x"):

            with self.subTest(bundleId=bundleId):

                with self.assertRaises(offlineserver.BundleNotFound):

                    self.bundles.get(bundleId)

    def testInstallNew(self):

        self.bundles.install("New", zipOf({"manifest.json": manifestText("New"), "apertium/tr.t1x": "<rules/>"}))
        self.assertTrue((self.root / "New" / "apertium" / "tr.t1x").is_file())
        self.assertTrue(self.bundles.isLoaded("New"))
        self.assertEqual([path.name for path in self.root.iterdir()], ["New"])

    def testInstallReplaces(self):

        makeBundle(self.root / "A", "A", {"old.txt": "old"})
        old = self.bundles.get("A")
        self.bundles.install("A", zipOf({"manifest.json": manifestText("A"), "new.txt": "new"}))
        self.assertTrue(old.closed)
        self.assertIsNot(self.bundles.get("A"), old)
        self.assertTrue((self.root / "A" / "new.txt").is_file())
        self.assertFalse((self.root / "A" / "old.txt").exists())
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["A"])

    def testInstallRefusals(self):

        makeBundle(self.root / "A", "A", {"old.txt": "old"})
        cases = {"not a zip": b"plain text", "zip slip": zipOf({"manifest.json": manifestText("A"), "../escape.txt": "x"}),
                 "absolute path": zipOf({"manifest.json": manifestText("A"), "/etc/x": "x"}), "no manifest": zipOf({"other.txt": "x"}),
                 "folder zipped": zipOf({"A/manifest.json": manifestText("A")})}

        for case, zipBytes in cases.items():

            with self.subTest(case=case):

                with self.assertRaises(ValueError):

                    self.bundles.install("A", zipBytes)

                # The old bundle is untouched and nothing is left beside it
                self.assertTrue((self.root / "A" / "old.txt").is_file())
                self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["A"])

        self.assertFalse((self.root.parent / "escape.txt").exists())

    def testInstallBadId(self):

        with self.assertRaises(ValueError):

            self.bundles.install("../x", zipOf({"manifest.json": manifestText("x")}))

    def testInstallThatWontLoadKeepsOld(self):

        makeBundle(self.root / "A", "A", {"old.txt": "old"})
        broken = json.dumps({"workProject": "A", "fail": True})

        with self.assertRaises(ValueError) as caught:

            self.bundles.install("A", zipOf({"manifest.json": broken, "new.txt": "new"}))

        self.assertIn("old one was kept", str(caught.exception))
        self.assertTrue((self.root / "A" / "old.txt").is_file())
        self.assertFalse(self.bundles.isLoaded("A"))
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["A"])

    def testSeedDoesNotOverwrite(self):

        seed = makeBundle(makeRoot(self) / "ftt_bundle", "Seeded", {"seed.txt": "1"})
        self.assertEqual(self.bundles.seed(seed), "Seeded")
        self.assertTrue((self.root / "Seeded" / "seed.txt").is_file())

        # A later upload of the same id is kept when the server starts again
        (self.root / "Seeded" / "seed.txt").write_text("uploaded", encoding="utf-8")
        self.bundles.seed(seed)
        self.assertEqual((self.root / "Seeded" / "seed.txt").read_text(encoding="utf-8"), "uploaded")
        self.assertIsNone(self.bundles.seed(makeRoot(self)))

    def testRemove(self):

        makeBundle(self.root / "A", "A")
        translator = self.bundles.get("A")
        self.bundles.addRun("A", {"title": "x"})
        self.bundles.remove("A")
        self.assertTrue(translator.closed)
        self.assertFalse((self.root / "A").exists())
        self.assertNotIn("A", self.bundles.runs)

        with self.assertRaises(offlineserver.BundleNotFound):

            self.bundles.remove("A")

class TestRequests(unittest.TestCase):

    def startServer(self, password, uploadPassword=None):

        root = makeRoot(self)
        makeBundle(root / "One", "One")
        makeBundle(root / "Two", "Two")
        self.bundles = offlineserver.BundleSet(root, FakeTranslator)
        server = offlineserver.OfflineServer(("127.0.0.1", 0), self.bundles, False, password=password, uploadPassword=uploadPassword)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)

        return f"http://127.0.0.1:{server.server_address[1]}"

    def getJson(self, url):

        with urllib.request.urlopen(url) as response:

            return json.loads(response.read())

    def upload(self, url, zipBytes, authorization=None, contentType="application/zip"):
        '''POST a zip; returns the HTTP status.'''

        request = urllib.request.Request(url, data=zipBytes, headers={"Content-Type": contentType}, method="POST")

        if authorization:

            request.add_header("Authorization", authorization)

        try:
            with urllib.request.urlopen(request) as response:

                return response.status

        except urllib.error.HTTPError as err:

            return err.code

    def testBundlesAndStatus(self):

        base = self.startServer(None)
        answer = self.getJson(base + "/api/bundles")
        self.assertEqual([bundle["id"] for bundle in answer["bundles"]], ["One", "Two"])
        self.assertEqual(answer["default"], "One")
        self.assertEqual(self.getJson(base + "/api/status")["bundle"], "One")
        status = self.getJson(base + "/api/status?bundle=Two")
        self.assertEqual((status["bundle"], status["workProject"], status["projectsOpen"]), ("Two", "Two", False))
        self.assertEqual(self.statusOf(base + "/api/status?bundle=Nope")[0], 404)
        self.assertEqual(self.getJson(base + "/api/runs?bundle=Two"), {"runs": []})

    def testUpload(self):

        base = self.startServer("s3cret", uploadPassword="up")
        zipBytes = zipOf({"manifest.json": manifestText("Three")})

        # The page's password isn't enough when uploads have their own
        self.assertEqual(self.upload(base + "/api/bundles/Three", zipBytes, basicHeader("u", "s3cret")), 401)
        self.assertEqual(self.upload(base + "/api/bundles/Three", zipBytes, basicHeader("u", "up"), contentType="application/json"), 415)
        self.assertEqual(self.upload(base + "/api/bundles/..%2Fx", zipBytes, basicHeader("u", "up")), 400)
        self.assertEqual(self.upload(base + "/api/bundles/Three", zipBytes, basicHeader("u", "up")), 200)
        self.assertTrue(self.bundles.exists("Three"))

        request = urllib.request.Request(base + "/api/bundles/Three", headers={"Authorization": basicHeader("u", "up")}, method="DELETE")

        with urllib.request.urlopen(request) as response:

            self.assertEqual(response.status, 200)

        self.assertFalse(self.bundles.exists("Three"))

    def testRefusedBigUploadIsAnswered(self):

        # A refused upload's body is read before the answer, so the client gets the 401 rather than a dropped connection (WinError 10053 on Windows)
        base = self.startServer("s3cret")
        bigBytes = bytes(4 * 1024 * 1024)
        self.assertEqual(self.upload(base + "/api/bundles/Big", bigBytes, basicHeader("u", "wrong")), 401)
        self.assertEqual(self.upload(base + "/api/bundles/Big", bigBytes, basicHeader("u", "s3cret"), contentType="text/plain"), 415)

    def statusOf(self, url, authorization=None):
        '''The HTTP status a GET of url answers, and the WWW-Authenticate header if any.'''

        request = urllib.request.Request(url)

        if authorization:

            request.add_header("Authorization", authorization)

        try:
            with urllib.request.urlopen(request) as response:

                return response.status, response.headers.get("WWW-Authenticate")

        except urllib.error.HTTPError as err:

            return err.code, err.headers.get("WWW-Authenticate")

    def testNoPasswordSet(self):

        base = self.startServer(None)
        self.assertEqual(self.statusOf(base + "/api/status")[0], 200)

    def testPasswordRequired(self):

        base = self.startServer("s3cret")
        status, challenge = self.statusOf(base + "/api/status")
        self.assertEqual(status, 401)
        self.assertIn("Basic", challenge or "")
        self.assertEqual(self.statusOf(base + "/api/runs", basicHeader("u", "wrong"))[0], 401)
        self.assertEqual(self.statusOf(base + "/api/status", basicHeader("u", "s3cret"))[0], 200)

    def testHealthIsOpen(self):

        base = self.startServer("s3cret")

        with urllib.request.urlopen(base + "/api/health") as response:

            self.assertEqual(json.loads(response.read()), {"ok": True})

    def testPostNeedsPassword(self):

        base = self.startServer("s3cret")
        request = urllib.request.Request(base + "/api/translate", data=b'{"text": "x"}', headers={"Content-Type": "application/json"}, method="POST")

        with self.assertRaises(urllib.error.HTTPError) as caught:

            urllib.request.urlopen(request)

        self.assertEqual(caught.exception.code, 401)

if __name__ == "__main__":

    unittest.main()
