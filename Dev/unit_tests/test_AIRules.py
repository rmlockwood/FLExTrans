#
#   test_AIRules
#
#   Unit tests for Dev/Lib/AIRules.py - the standalone (Qt-free, FLEx-free) core of the
#   "Work on Rules with AI" module: the provider layer, the API-key vault helpers, the
#   prompt-assembly functions, the transfer-file parsing/summary, and the splice + validate
#   + apply pipeline. The AI provider SDKs (anthropic, google.genai, openai) and the OS
#   keyring are imported lazily inside AIRules, so each test that exercises them injects a
#   lightweight fake into sys.modules for the duration of the test - no real SDK, network,
#   or credential store is ever touched.
#
import unittest
import sys
import os
import json
import tempfile
import shutil
import datetime
from types import SimpleNamespace, ModuleType
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import AIRules

# ---------------------------------------------------------------------------
# Shared fixtures: a small but structurally complete Apertium transfer file, plus a valid
# rule and macro, reused across the parsing / splice / validate / apply tests.
# ---------------------------------------------------------------------------

SAMPLE_TRANSFER = '''<?xml version="1.0" encoding="utf-8"?>
<transfer>
  <section-def-cats>
    <def-cat n="nom">
      <cat-item tags="n"/>
      <cat-item tags="n.*"/>
    </def-cat>
    <def-cat n="det_lemma">
      <cat-item lemma="the" tags="det"/>
    </def-cat>
  </section-def-cats>
  <section-def-attrs>
    <def-attr n="gender">
      <attr-item tags="m"/>
      <attr-item tags="f"/>
    </def-attr>
  </section-def-attrs>
  <section-def-vars>
    <def-var n="number"/>
  </section-def-vars>
  <section-def-lists>
    <def-list n="mylist">
      <list-item v="a"/>
      <list-item v="b"/>
    </def-list>
  </section-def-lists>
  <section-def-macros>
    <def-macro n="mymacro" npar="1">
      <let><clip pos="1" side="tl" part="lem"/><lit v="longer-macro-body-so-it-sorts-first"/></let>
    </def-macro>
  </section-def-macros>
  <section-rules>
    <rule comment="Rule One">
      <pattern><pattern-item n="nom"/></pattern>
      <action><out><lu><clip pos="1" side="tl" part="whole"/></lu></out></action>
    </rule>
    <rule comment="Rule Two is the longer one for sort ordering">
      <pattern><pattern-item n="det_lemma"/></pattern>
      <action><out><lu><clip pos="1" side="tl" part="whole"/></lu></out></action>
    </rule>
  </section-rules>
</transfer>
'''

VALID_RULE = ('<rule comment="AI Rule"><pattern><pattern-item n="nom"/></pattern>'
              '<action><out><lu><clip pos="1" side="tl" part="whole"/></lu></out></action></rule>')

def writeSample(path):
    '''Write the shared sample transfer file to `path`.'''

    with open(path, 'w', encoding='utf-8') as fout:
        fout.write(SAMPLE_TRANSFER)

class TempDirTestCase(unittest.TestCase):
    '''Base class giving each test its own scratch directory (auto-removed) plus a written sample transfer file and a dummy DTD.'''

    def setUp(self):

        self.workDir = tempfile.mkdtemp(prefix='airules_test_')
        self.addCleanup(shutil.rmtree, self.workDir, True)

        self.transferPath = os.path.join(self.workDir, 'transfer.t1x')
        writeSample(self.transferPath)

        self.dtdPath = os.path.join(self.workDir, 'transfer.dtd')

        with open(self.dtdPath, 'w', encoding='utf-8') as fout:
            fout.write('<!-- dummy dtd; the compiler is mocked/skipped in tests -->')

# ---------------------------------------------------------------------------
# parseRetryAfter and RateLimitError
# ---------------------------------------------------------------------------

class TestParseRetryAfter(unittest.TestCase):

    def test_retry_in_phrasing(self):
        self.assertEqual(AIRules.parseRetryAfter('Please retry in 28.3s.'), 28.3)

    def test_retry_delay_field(self):
        self.assertEqual(AIRules.parseRetryAfter('"retryDelay": "28s"'), 28.0)

    def test_bare_seconds_fallback(self):
        self.assertEqual(AIRules.parseRetryAfter('wait 5 seconds and try again'), 5.0)

    def test_no_number_returns_none(self):
        self.assertIsNone(AIRules.parseRetryAfter('no numbers to be found here'))

class TestRateLimitError(unittest.TestCase):

    def test_message_without_retry_after(self):

        err = AIRules.RateLimitError('Google Gemini')
        text = str(err)

        self.assertIn('Google Gemini is rate limited (HTTP 429).', text)
        self.assertNotIn('Try again in about', text)
        self.assertIn('free tier', text.lower())

    def test_message_with_retry_after_rounds(self):

        err = AIRules.RateLimitError('Anthropic Claude', 30.4)

        self.assertIn('Try again in about 30 seconds.', str(err))

    def test_carries_fields(self):

        err = AIRules.RateLimitError('X', 12.0)

        self.assertEqual(err.providerDisplay, 'X')
        self.assertEqual(err.retryAfter, 12.0)
        self.assertIsInstance(err, RuntimeError)

# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

class TestProviderRegistry(unittest.TestCase):

    def test_three_providers_registered(self):
        self.assertEqual(set(AIRules.PROVIDERS), {'gemini', 'anthropic', 'openai'})

    def test_default_provider_is_gemini(self):
        self.assertEqual(AIRules.DEFAULT_PROVIDER, 'gemini')

    def test_find_by_short_name(self):
        self.assertIs(AIRules.findProvider('anthropic'), AIRules.PROVIDERS['anthropic'])

    def test_find_by_display_name_case_insensitive(self):
        self.assertIs(AIRules.findProvider('  GOOGLE GEMINI '), AIRules.PROVIDERS['gemini'])

    def test_find_unknown_returns_none(self):
        self.assertIsNone(AIRules.findProvider('nope'))

    def test_find_empty_returns_none(self):
        self.assertIsNone(AIRules.findProvider(''))
        self.assertIsNone(AIRules.findProvider(None))

    def test_get_provider_falls_back_to_default(self):
        self.assertIs(AIRules.getProvider(None), AIRules.PROVIDERS['gemini'])
        self.assertIs(AIRules.getProvider('unknown'), AIRules.PROVIDERS['gemini'])

    def test_get_provider_known(self):
        self.assertIs(AIRules.getProvider('openai'), AIRules.PROVIDERS['openai'])

    def test_find_model_owner(self):
        self.assertIs(AIRules.findModelOwner('claude-opus-4-8'), AIRules.PROVIDERS['anthropic'])
        self.assertIs(AIRules.findModelOwner('gpt-5.1'), AIRules.PROVIDERS['openai'])

    def test_find_model_owner_unknown(self):
        self.assertIsNone(AIRules.findModelOwner('some-future-model'))
        self.assertIsNone(AIRules.findModelOwner(None))

# ---------------------------------------------------------------------------
# API-key vault helpers (keyring is faked)
# ---------------------------------------------------------------------------

class FakeKeyring:
    '''In-memory stand-in for the `keyring` module. delete_password raises when the entry is absent, like the real backend.'''

    def __init__(self):
        self.store = {}

    def get_password(self, service, user):
        return self.store.get((service, user))

    def set_password(self, service, user, password):
        self.store[(service, user)] = password

    def delete_password(self, service, user):

        if (service, user) in self.store:
            del self.store[(service, user)]
        else:
            raise RuntimeError('no such password')

class TestKeyring(unittest.TestCase):

    def setUp(self):

        self.fake = FakeKeyring()
        patcher = mock.patch.dict(sys.modules, {'keyring': self.fake})
        patcher.start()
        self.addCleanup(patcher.stop)

        self.provider = AIRules.PROVIDERS['anthropic']

    def test_keyring_user_name(self):
        self.assertEqual(AIRules.keyringUser(self.provider), 'AIRulesApiKey:anthropic')

    def test_set_and_get(self):

        AIRules.setStoredApiKey(self.provider, 'secret-123')

        self.assertEqual(AIRules.getStoredApiKey(self.provider), 'secret-123')
        self.assertEqual(self.fake.store[(AIRules.KEYRING_SERVICE, 'AIRulesApiKey:anthropic')], 'secret-123')

    def test_get_none_when_absent(self):
        self.assertIsNone(AIRules.getStoredApiKey(self.provider))

    def test_legacy_migration(self):

        # A pre-per-provider key lives in the bare single slot; getStoredApiKey should adopt it for the asked-about provider and delete the old slot.
        self.fake.set_password(AIRules.KEYRING_SERVICE, AIRules.LEGACY_KEYRING_USER, 'legacy-key')

        self.assertEqual(AIRules.getStoredApiKey(self.provider), 'legacy-key')
        self.assertEqual(self.fake.store.get((AIRules.KEYRING_SERVICE, 'AIRulesApiKey:anthropic')), 'legacy-key')
        self.assertNotIn((AIRules.KEYRING_SERVICE, AIRules.LEGACY_KEYRING_USER), self.fake.store)

    def test_per_provider_key_wins_over_legacy(self):

        self.fake.set_password(AIRules.KEYRING_SERVICE, 'AIRulesApiKey:anthropic', 'own-key')
        self.fake.set_password(AIRules.KEYRING_SERVICE, AIRules.LEGACY_KEYRING_USER, 'legacy-key')

        self.assertEqual(AIRules.getStoredApiKey(self.provider), 'own-key')

    def test_resolve_prefers_vault(self):

        AIRules.setStoredApiKey(self.provider, 'vault-key')

        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'env-key'}):
            self.assertEqual(AIRules.resolveApiKey(self.provider), 'vault-key')

    def test_resolve_falls_back_to_env(self):

        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'env-key'}):
            self.assertEqual(AIRules.resolveApiKey(self.provider), 'env-key')

    def test_resolve_none_when_nothing(self):

        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(AIRules.resolveApiKey(self.provider))

# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

class TestPromptBuilding(unittest.TestCase):

    def test_cap_items_under_limit_unchanged(self):

        items = ['a', 'b', 'c']

        self.assertEqual(AIRules.capItemsForSummary(items), items)

    def test_cap_items_over_limit_adds_marker(self):

        items = [str(i) for i in range(AIRules.MAX_SUMMARY_ITEMS + 5)]
        result = AIRules.capItemsForSummary(items)

        self.assertEqual(len(result), AIRules.MAX_SUMMARY_ITEMS + 1)
        self.assertEqual(result[-1], '(… 5 more)')

    def test_system_instruction_conventions_only(self):

        text = AIRules.buildSystemInstruction('CONVENTIONS', '', '')

        self.assertEqual(text, 'CONVENTIONS')

    def test_system_instruction_with_rules_and_macros(self):

        text = AIRules.buildSystemInstruction('CONVENTIONS', 'RULETEXT', 'MACROTEXT')

        self.assertIn('CONVENTIONS', text)
        self.assertIn('Example rules from this project', text)
        self.assertIn('RULETEXT', text)
        self.assertIn('Example macros from this project', text)
        self.assertIn('MACROTEXT', text)

    def test_user_content_create_mode(self):

        text = AIRules.buildUserContent('create', 'make a plural rule', 'DEFS', 'PROJDATA', None)

        self.assertIn('MODE: create a new rule.', text)
        self.assertIn('USER REQUEST:', text)
        self.assertIn('make a plural rule', text)
        self.assertIn('PROJDATA', text)
        self.assertIn('DEFS', text)
        self.assertNotIn('CURRENT RULE:', text)

    def test_user_content_modify_mode(self):

        text = AIRules.buildUserContent('modify', 'change it', 'DEFS', 'PROJDATA', '<rule comment="X"/>')

        self.assertIn('MODE: modify the following existing rule.', text)
        self.assertIn('CURRENT RULE:', text)
        self.assertIn('<rule comment="X"/>', text)
        self.assertIn('USER REQUEST:', text)

    def test_user_content_explain_mode_returns_early(self):

        text = AIRules.buildUserContent('explain', '', 'DEFS', 'PROJDATA', '<rule comment="X"/>', explainLang='Spanish')

        self.assertIn('MODE: explain the following existing rule.', text)
        self.assertIn('RULE TO EXPLAIN:', text)
        self.assertIn('Spanish', text)
        # Explain mode has no user request and returns before that section is added.
        self.assertNotIn('USER REQUEST:', text)

    def test_user_content_includes_example_data(self):

        text = AIRules.buildUserContent('create', 'req', 'DEFS', 'PROJDATA', None, sourceData='SRC\tROWS', targetData='TGT\tROWS')

        self.assertIn('SOURCE LANGUAGE EXAMPLE DATA', text)
        self.assertIn('SRC\tROWS', text)
        self.assertIn('TARGET LANGUAGE EXAMPLE DATA', text)
        self.assertIn('TGT\tROWS', text)

    def test_user_content_omits_absent_example_data(self):

        text = AIRules.buildUserContent('create', 'req', 'DEFS', 'PROJDATA', None)

        self.assertNotIn('SOURCE LANGUAGE EXAMPLE DATA', text)
        self.assertNotIn('TARGET LANGUAGE EXAMPLE DATA', text)

# ---------------------------------------------------------------------------
# Transfer-file parsing and summary
# ---------------------------------------------------------------------------

class TestTransferParsing(TempDirTestCase):

    def test_parse_transfer_file_root(self):

        root = AIRules.parseTransferFile(self.transferPath)

        self.assertEqual(root.tag, 'transfer')
        self.assertIsNotNone(root.find('section-rules'))

    def test_sample_rules_and_macros(self):

        rulesText, macrosText = AIRules.getSampleRulesAndMacros(self.transferPath)

        self.assertIn('Rule One', rulesText)
        self.assertIn('Rule Two is the longer one', rulesText)
        self.assertIn('mymacro', macrosText)

    def test_sample_rules_respects_counts(self):

        rulesText, macrosText = AIRules.getSampleRulesAndMacros(self.transferPath, ruleCount=1, macroCount=0)

        # Longest rule only, and no macros requested.
        self.assertIn('Rule Two is the longer one', rulesText)
        self.assertNotIn('comment="Rule One"', rulesText)
        self.assertEqual(macrosText, '')

    def test_sample_rules_accepts_preparsed_root(self):

        root = AIRules.parseTransferFile(self.transferPath)
        viaRoot = AIRules.getSampleRulesAndMacros(root=root)
        viaPath = AIRules.getSampleRulesAndMacros(self.transferPath)

        self.assertEqual(viaRoot, viaPath)

    def test_sample_rules_requires_root_or_path(self):

        with self.assertRaises(AssertionError):
            AIRules.getSampleRulesAndMacros()

    def test_extract_existing_defs_data(self):

        defs = AIRules.extractExistingDefs(self.transferPath)

        self.assertEqual(set(defs['cats']), {'nom', 'det_lemma'})
        self.assertEqual(defs['attrs']['gender'], ['f', 'm'])
        self.assertEqual(defs['variables'], ['number'])
        self.assertEqual(defs['lists'], ['mylist'])
        self.assertEqual(defs['listItems']['mylist'], ['a', 'b'])
        self.assertEqual(defs['macros'], ['mymacro'])
        self.assertIn('Rule One', defs['ruleNames'])

    def test_extract_existing_defs_lemma_annotation(self):

        defs = AIRules.extractExistingDefs(self.transferPath)

        self.assertEqual(defs['catItems']['det_lemma'], ['det (lemma the)'])

    def test_extract_existing_defs_rule_xml_map(self):

        defs = AIRules.extractExistingDefs(self.transferPath)

        self.assertIn('Rule One', defs['ruleXml'])
        self.assertIn('<rule', defs['ruleXml']['Rule One'])

    def test_extract_existing_defs_summary_text(self):

        summary = AIRules.extractExistingDefs(self.transferPath)['summaryText']

        self.assertIn('Existing categories', summary)
        self.assertIn('gender: f, m', summary)
        self.assertIn('mylist: a, b', summary)
        self.assertIn('Existing variables (def-var): number', summary)
        self.assertIn('Existing macros (def-macro): mymacro', summary)

    def test_extract_existing_defs_requires_root_or_path(self):

        with self.assertRaises(AssertionError):
            AIRules.extractExistingDefs()

    def test_get_rule_xml_by_comment_found(self):

        xml = AIRules.getRuleXmlByComment(self.transferPath, 'Rule One')

        self.assertIsNotNone(xml)
        self.assertIn('<rule', xml)
        self.assertIn('pattern-item n="nom"', xml)

    def test_get_rule_xml_by_comment_not_found(self):
        self.assertIsNone(AIRules.getRuleXmlByComment(self.transferPath, 'Ghost Rule'))

# ---------------------------------------------------------------------------
# getSection, insertBefore, spliceIntoTemp, validateFile
# ---------------------------------------------------------------------------

class TestSpliceAndValidate(TempDirTestCase):

    def test_get_section_existing(self):

        root = AIRules.parseTransferFile(self.transferPath)
        section = AIRules.getSection(root, 'section-rules')

        self.assertIsNotNone(section)
        self.assertEqual(section.tag, 'section-rules')

    def test_get_section_creates_when_missing(self):

        root = AIRules.parseTransferFile(self.transferPath)
        section = AIRules.getSection(root, 'section-brand-new')

        self.assertEqual(section.tag, 'section-brand-new')
        self.assertIsNotNone(root.find('section-brand-new'))

    def test_insert_before_found(self):

        result = AIRules.insertBefore('AAA<end/>BBB', '<end/>', 'INSERTED')

        self.assertEqual(result, 'AAAINSERTED\n<end/>BBB')

    def test_insert_before_not_found_raises(self):

        with self.assertRaises(RuntimeError):
            AIRules.insertBefore('nothing here', '<missing/>', 'X')

    def test_splice_create_appends_rule(self):

        tempPath = AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, [], 'create', None, self.workDir)
        root = AIRules.parseTransferFile(tempPath)
        comments = [r.get('comment') for r in root.findall('.//rule')]

        self.assertIn('AI Rule', comments)
        self.assertEqual(len(comments), 3)

    def test_splice_modify_replaces_rule(self):

        newRule = VALID_RULE.replace('comment="AI Rule"', 'comment="Rule One"')
        tempPath = AIRules.spliceIntoTemp(self.transferPath, newRule, [], 'modify', 'Rule One', self.workDir)
        root = AIRules.parseTransferFile(tempPath)
        rules = root.findall('.//rule')

        # Still two rules; the "Rule One" slot now holds the new body (pattern-item nom, not the original det_lemma neighbour).
        self.assertEqual(len(rules), 2)
        ruleOne = [r for r in rules if r.get('comment') == 'Rule One'][0]
        self.assertIsNotNone(ruleOne.find('.//pattern-item[@n="nom"]'))

    def test_splice_adds_new_definition(self):

        newList = '<def-list n="freshlist"><list-item v="z"/></def-list>'
        tempPath = AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, [newList], 'create', None, self.workDir)
        root = AIRules.parseTransferFile(tempPath)
        listNames = [l.get('n') for l in root.findall('.//def-list')]

        self.assertIn('freshlist', listNames)

    def test_splice_unsupported_definition_raises(self):

        with self.assertRaises(RuntimeError):
            AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, ['<bogus n="x"/>'], 'create', None, self.workDir)

    def test_validate_wellformed_ok(self):

        tempPath = AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, [], 'create', None, self.workDir)
        ok, errors = AIRules.validateFile(tempPath, self.dtdPath, compilerExe=None)

        self.assertTrue(ok)
        self.assertEqual(errors, '')

    def test_validate_malformed_fails(self):

        badPath = os.path.join(self.workDir, 'bad.t1x')

        with open(badPath, 'w', encoding='utf-8') as fout:
            fout.write('<transfer><section-rules><rule></section-rules></transfer>')

        ok, errors = AIRules.validateFile(badPath, self.dtdPath, compilerExe=None)

        self.assertFalse(ok)
        self.assertIn('not well-formed', errors)

    def test_validate_compiler_success(self):

        tempPath = AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, [], 'create', None, self.workDir)
        compilerExe = os.path.join(self.workDir, 'fake-compiler.exe')

        with open(compilerExe, 'w') as fout:
            fout.write('')

        fakeResult = SimpleNamespace(returncode=0, stderr=b'some warning to stderr')

        with mock.patch.object(AIRules.subprocess, 'run', return_value=fakeResult):
            ok, errors = AIRules.validateFile(tempPath, self.dtdPath, compilerExe)

        # Zero exit means success even though stderr was non-empty (it emits warnings).
        self.assertTrue(ok)

    def test_validate_compiler_failure(self):

        tempPath = AIRules.spliceIntoTemp(self.transferPath, VALID_RULE, [], 'create', None, self.workDir)
        compilerExe = os.path.join(self.workDir, 'fake-compiler.exe')

        with open(compilerExe, 'w') as fout:
            fout.write('')

        fakeResult = SimpleNamespace(returncode=1, stderr=b'structural error XYZ')

        with mock.patch.object(AIRules.subprocess, 'run', return_value=fakeResult):
            ok, errors = AIRules.validateFile(tempPath, self.dtdPath, compilerExe)

        self.assertFalse(ok)
        self.assertIn('apertium-preprocess-transfer failed', errors)
        self.assertIn('structural error XYZ', errors)

# ---------------------------------------------------------------------------
# markAuthorship
# ---------------------------------------------------------------------------

class TestMarkAuthorship(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime(2026, 7, 3, 14, 42)

    def test_added_default_english(self):

        out = AIRules.markAuthorship(VALID_RULE, 'create', self.now)

        self.assertIn('The AI Assistant added this rule', out)
        self.assertIn('July 3, 2026 14:42', out)

    def test_modified_wording(self):

        out = AIRules.markAuthorship(VALID_RULE, 'modify', self.now)

        self.assertIn('The AI Assistant modified this rule', out)

    def test_comment_is_first_child(self):

        out = AIRules.markAuthorship(VALID_RULE, 'create', self.now)
        # The authorship comment precedes the <pattern> element in the serialized rule.
        self.assertLess(out.index('<!--'), out.index('<pattern>'))

    def test_when_str_overrides_date(self):

        out = AIRules.markAuthorship(VALID_RULE, 'create', self.now, whenStr='3 de julio de 2026')

        self.assertIn('3 de julio de 2026', out)
        self.assertNotIn('July 3, 2026', out)

    def test_localized_templates(self):

        templates = {'added': 'IA agregó esta regla el {when}.', 'modified': 'IA modificó esta regla el {when}.'}
        out = AIRules.markAuthorship(VALID_RULE, 'create', self.now, authorshipComments=templates, whenStr='hoy')

        self.assertIn('IA agreg', out)
        self.assertIn('hoy', out)

    def test_unparseable_returns_unchanged(self):

        junk = '<rule><not closed'

        self.assertEqual(AIRules.markAuthorship(junk, 'create', self.now), junk)

# ---------------------------------------------------------------------------
# Engine.generate, generateRule, explainRule (with fakes)
# ---------------------------------------------------------------------------

class FakeProvider:
    '''Records the arguments Engine.generate forwards, and returns a canned dict (or raises).'''

    displayName = 'Fake Provider'

    def __init__(self, result=None, exc=None):
        self.result = result if result is not None else {'ok': True}
        self.exc = exc
        self.calls = []

    def generate(self, client, model, systemInstruction, userContent, task=AIRules.TASK_RULE):

        self.calls.append((client, model, systemInstruction, userContent, task))

        if self.exc:
            raise self.exc

        return self.result

class TestEngineGenerate(unittest.TestCase):

    def test_engine_forwards_and_returns(self):

        provider = FakeProvider(result={'rule_xml': 'X'})
        engine = AIRules.Engine(provider, client='CLIENT', model='mymodel')
        result = engine.generate('SYS', 'USER', AIRules.TASK_RULE)

        self.assertEqual(result, {'rule_xml': 'X'})
        self.assertEqual(provider.calls[0], ('CLIENT', 'mymodel', 'SYS', 'USER', AIRules.TASK_RULE))

    def test_engine_logs_prompt_and_response(self):

        logPath = tempfile.mktemp(suffix='.log')
        self.addCleanup(lambda: os.path.exists(logPath) and os.remove(logPath))

        provider = FakeProvider(result={'rule_xml': 'X'})
        engine = AIRules.Engine(provider, client='C', model='m')

        with mock.patch.object(AIRules, 'PROMPT_LOG_PATH', logPath):
            engine.generate('SYSTEXT', 'USERTEXT', AIRules.TASK_RULE)

        with open(logPath, encoding='utf-8') as fin:
            logged = fin.read()

        self.assertIn('PROMPT to Fake Provider', logged)
        self.assertIn('SYSTEXT', logged)
        self.assertIn('USERTEXT', logged)
        self.assertIn('RESPONSE from Fake Provider', logged)

    def test_engine_logs_and_reraises_error(self):

        logPath = tempfile.mktemp(suffix='.log')
        self.addCleanup(lambda: os.path.exists(logPath) and os.remove(logPath))

        provider = FakeProvider(exc=RuntimeError('boom'))
        engine = AIRules.Engine(provider, client='C', model='m')

        with mock.patch.object(AIRules, 'PROMPT_LOG_PATH', logPath):

            with self.assertRaises(RuntimeError):
                engine.generate('S', 'U', AIRules.TASK_RULE)

        with open(logPath, encoding='utf-8') as fin:
            logged = fin.read()

        self.assertIn('ERROR from Fake Provider', logged)
        self.assertIn('boom', logged)

class FakeEngine:
    '''Returns queued response dicts in order; records the userContent of each call so retry-feedback can be asserted.'''

    def __init__(self, responses):
        self.responses = list(responses)
        self.userContents = []

    def generate(self, systemInstruction, userContent, task=AIRules.TASK_RULE):

        self.userContents.append(userContent)
        return self.responses.pop(0)

class TestGenerateRuleAndExplain(unittest.TestCase):

    def test_generate_rule_unpacks_fields(self):

        engine = FakeEngine([{'rule_xml': 'RX', 'new_defs': ['D'], 'explanation': 'E', 'language': 'es'}])
        rule, defs, expl, lang = AIRules.generateRule(engine, 'SYS', 'USER')

        self.assertEqual((rule, defs, expl, lang), ('RX', ['D'], 'E', 'es'))

    def test_generate_rule_defaults_missing_optional_fields(self):

        engine = FakeEngine([{'rule_xml': 'RX'}])
        rule, defs, expl, lang = AIRules.generateRule(engine, 'SYS', 'USER')

        self.assertEqual((rule, defs, expl, lang), ('RX', [], '', ''))

    def test_generate_rule_appends_prior_errors(self):

        engine = FakeEngine([{'rule_xml': 'RX'}])
        AIRules.generateRule(engine, 'SYS', 'USER', priorErrors='the DTD complained')

        self.assertIn('failed validation', engine.userContents[0])
        self.assertIn('the DTD complained', engine.userContents[0])

    def test_explain_rule_unpacks(self):

        engine = FakeEngine([{'explanation': 'long explanation', 'language': 'fr'}])
        expl, lang = AIRules.explainRule(engine, 'SYS', 'USER')

        self.assertEqual((expl, lang), ('long explanation', 'fr'))

# ---------------------------------------------------------------------------
# generateValidatedRule - the retry loop (uses FakeEngine + a mocked compiler)
# ---------------------------------------------------------------------------

class TestGenerateValidatedRule(TempDirTestCase):

    def _ruleResponse(self):
        return {'rule_xml': VALID_RULE, 'new_defs': [], 'explanation': 'does a thing', 'language': 'en'}

    def test_valid_on_first_attempt(self):

        engine = FakeEngine([self._ruleResponse()])
        result = AIRules.generateValidatedRule(engine, 'SYS', 'USER', self.transferPath, self.dtdPath, 'create', None, compilerExe=None)

        self.assertTrue(result.valid)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.explanation, 'does a thing')
        # The authorship stamp was applied to the returned rule.
        self.assertIn('The AI Assistant added this rule', result.ruleXml)

    def test_retry_then_succeed(self):

        engine = FakeEngine([self._ruleResponse(), self._ruleResponse()])
        compilerExe = os.path.join(self.workDir, 'fake-compiler.exe')

        with open(compilerExe, 'w') as fout:
            fout.write('')

        results = [SimpleNamespace(returncode=1, stderr=b'first fails'), SimpleNamespace(returncode=0, stderr=b'')]

        with mock.patch.object(AIRules.subprocess, 'run', side_effect=results):
            result = AIRules.generateValidatedRule(engine, 'SYS', 'USER', self.transferPath, self.dtdPath, 'create', None, compilerExe=compilerExe)

        self.assertTrue(result.valid)
        self.assertEqual(result.attempts, 2)
        # The second generation got the first attempt's errors fed back.
        self.assertIn('first fails', engine.userContents[1])

    def test_exhausts_attempts(self):

        engine = FakeEngine([self._ruleResponse() for _ in range(AIRules.MAX_VALIDATION_ATTEMPTS)])
        compilerExe = os.path.join(self.workDir, 'fake-compiler.exe')

        with open(compilerExe, 'w') as fout:
            fout.write('')

        alwaysFail = SimpleNamespace(returncode=1, stderr=b'never compiles')

        with mock.patch.object(AIRules.subprocess, 'run', return_value=alwaysFail):
            result = AIRules.generateValidatedRule(engine, 'SYS', 'USER', self.transferPath, self.dtdPath, 'create', None, compilerExe=compilerExe)

        self.assertFalse(result.valid)
        self.assertEqual(result.attempts, AIRules.MAX_VALIDATION_ATTEMPTS)
        self.assertIn('never compiles', result.errors)

    def test_scratch_dir_removed(self):

        scratch = tempfile.mkdtemp(prefix='airules_scratch_')
        engine = FakeEngine([self._ruleResponse()])

        with mock.patch.object(AIRules.tempfile, 'mkdtemp', return_value=scratch):
            AIRules.generateValidatedRule(engine, 'SYS', 'USER', self.transferPath, self.dtdPath, 'create', None, compilerExe=None)

        self.assertFalse(os.path.exists(scratch))

# ---------------------------------------------------------------------------
# applyRule - the real-file write path
# ---------------------------------------------------------------------------

class TestApplyRule(TempDirTestCase):

    def _result(self, ruleXml=VALID_RULE, newDefs=None):
        return AIRules.RuleResult(ruleXml=ruleXml, newDefs=newDefs or [], explanation='', language='en', valid=True, errors='', attempts=1)

    def test_create_inserts_before_section_close(self):

        backup = AIRules.applyRule(self.transferPath, self._result(), 'create', None)

        with open(self.transferPath, encoding='utf-8') as fin:
            text = fin.read()

        self.assertIn('comment="AI Rule"', text)
        self.assertLess(text.index('comment="AI Rule"'), text.index('</section-rules'))
        self.assertTrue(os.path.exists(backup))

    def test_create_inserts_new_definition(self):

        newList = '<def-list n="appliedlist"><list-item v="z"/></def-list>'
        AIRules.applyRule(self.transferPath, self._result(newDefs=[newList]), 'create', None)

        with open(self.transferPath, encoding='utf-8') as fin:
            text = fin.read()

        self.assertIn('appliedlist', text)
        self.assertLess(text.index('appliedlist'), text.index('</section-def-lists'))

    def test_modify_replaces_target_rule(self):

        newRule = '<rule comment="Rule One"><pattern><pattern-item n="det_lemma"/></pattern><action><out><lu><lit v="changed"/></lu></out></action></rule>'
        AIRules.applyRule(self.transferPath, self._result(ruleXml=newRule), 'modify', 'Rule One')

        with open(self.transferPath, encoding='utf-8') as fin:
            text = fin.read()

        self.assertIn('lit v="changed"', text)
        # Exactly two rules remain (replaced in place, not appended).
        self.assertEqual(text.count('<rule '), 2)

    def test_modify_unfound_comment_refuses(self):

        with self.assertRaises(RuntimeError):
            AIRules.applyRule(self.transferPath, self._result(), 'modify', 'No Such Rule')

    def test_modify_unfound_still_makes_backup(self):

        # Even when it refuses to write, the backup was already taken; the file is left byte-for-byte unchanged.
        with open(self.transferPath, encoding='utf-8') as fin:
            before = fin.read()

        with self.assertRaises(RuntimeError):
            AIRules.applyRule(self.transferPath, self._result(), 'modify', 'No Such Rule')

        with open(self.transferPath, encoding='utf-8') as fin:
            after = fin.read()

        self.assertEqual(before, after)
        backups = [f for f in os.listdir(self.workDir) if '.bak' in f]
        self.assertTrue(backups)

# ---------------------------------------------------------------------------
# buildEngine (provider registry + model selection, makeClient faked)
# ---------------------------------------------------------------------------

class FakeProviderForEngine:

    name = 'fakeprov'
    displayName = 'Fake Prov'
    defaultModel = 'fake-default-model'

    def makeClient(self, apiKey):
        self.seenKey = apiKey
        return ('fake-client', apiKey)

class TestBuildEngine(unittest.TestCase):

    def setUp(self):

        self.fake = FakeProviderForEngine()
        AIRules.PROVIDERS['fakeprov'] = self.fake
        self.addCleanup(lambda: AIRules.PROVIDERS.pop('fakeprov', None))

    def test_uses_provider_default_model(self):

        engine = AIRules.buildEngine('fakeprov', 'the-key')

        self.assertIs(engine.provider, self.fake)
        self.assertEqual(engine.model, 'fake-default-model')
        self.assertEqual(engine.client, ('fake-client', 'the-key'))

    def test_model_override(self):

        engine = AIRules.buildEngine('fakeprov', 'the-key', model='override-model')

        self.assertEqual(engine.model, 'override-model')

# ---------------------------------------------------------------------------
# logPromptTraffic
# ---------------------------------------------------------------------------

class TestLogPromptTraffic(unittest.TestCase):

    def test_noop_when_disabled(self):

        # Default is off; with no path set the call must not raise and must write nothing.
        with mock.patch.object(AIRules, 'PROMPT_LOG_PATH', None):
            AIRules.logPromptTraffic('title', 'text')  # no exception == pass

    def test_appends_when_enabled(self):

        logPath = tempfile.mktemp(suffix='.log')
        self.addCleanup(lambda: os.path.exists(logPath) and os.remove(logPath))

        with mock.patch.object(AIRules, 'PROMPT_LOG_PATH', logPath):
            AIRules.logPromptTraffic('MY TITLE', 'my body')
            AIRules.logPromptTraffic('SECOND', 'more')

        with open(logPath, encoding='utf-8') as fin:
            content = fin.read()

        self.assertIn('MY TITLE', content)
        self.assertIn('my body', content)
        self.assertIn('SECOND', content)

    def test_bad_path_swallowed(self):

        badPath = os.path.join(tempfile.gettempdir(), 'no_such_dir_12345', 'x.log')

        with mock.patch.object(AIRules, 'PROMPT_LOG_PATH', badPath):
            AIRules.logPromptTraffic('t', 'x')  # OSError must be swallowed, no raise == pass

# ---------------------------------------------------------------------------
# RuleResult dataclass
# ---------------------------------------------------------------------------

class TestRuleResult(unittest.TestCase):

    def test_fields(self):

        r = AIRules.RuleResult(ruleXml='X', newDefs=['a'], explanation='e', language='en', valid=True, errors='', attempts=2)

        self.assertEqual(r.ruleXml, 'X')
        self.assertEqual(r.newDefs, ['a'])
        self.assertEqual(r.language, 'en')
        self.assertTrue(r.valid)
        self.assertEqual(r.attempts, 2)

if __name__ == '__main__':
    unittest.main()
