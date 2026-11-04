#
#   tests/test_offlineserver
#
#   Ron Lockwood
#   SIL International
#   11/4/26
#
#   Version 3.17 - 11/4/26 - Ron Lockwood
#    Initial version. Tests the offline server's password check.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for the password that keeps the offline server's page and API private (see SAFETY in offlineserver.py). They need no bundle, hcparse or HCSynthByGloss: the header check and the
#   start-up rule are plain functions, and the request tests run a real OfflineServer on a free local port with a stand-in translator that has only what /api/status and /api/runs read. Run them
#   from Dev\FTtranslator with python -m unittest discover -s tests.
#
#   CODE STRUCTURE
#
#   TestPasswordMatches covers _passwordMatches() on good, wrong and malformed Authorization headers. TestNeedsPassword covers _needsPassword(). TestRequests starts an OfflineServer on a thread
#   with FakeTranslator behind it and checks which requests are answered 200 and which 401, with and without a password set.
#

import base64
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

# The package is one folder up from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import offlineserver  # noqa: E402

def basicHeader(user, password):
    '''An Authorization header value for HTTP Basic Auth.'''

    return "Basic " + base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")

class FakeTranslator:
    '''Just enough of OfflineTranslator for /api/status and /api/runs.'''

    def __init__(self):

        self.manifest = {"workProject": "Test", "sourceProject": "Src", "targetProject": "Tgt"}
        self.runs = []

    def close(self):

        pass

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

class TestRequests(unittest.TestCase):

    def startServer(self, password):

        server = offlineserver.OfflineServer(("127.0.0.1", 0), FakeTranslator(), False, password=password)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)

        return f"http://127.0.0.1:{server.server_address[1]}"

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
