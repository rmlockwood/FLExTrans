#
#   test_AIRules_providers
#
#   Unit tests for the three provider adapters in AIRules (AnthropicProvider, GeminiProvider,
#   OpenAIProvider). Each provider's generate() imports its SDK lazily and calls the SDK
#   client, so these tests inject a fake SDK module into sys.modules and pass a hand-built fake
#   client - exercising the request-shaping, the JSON/tool-call extraction, the refusal and
#   empty-response handling, and the 429 -> RateLimitError translation, without any real SDK,
#   network call, or API key.
#
import unittest
import sys
import os
from types import SimpleNamespace, ModuleType
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import AIRules

# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

def makeFakeAnthropic():
    '''A stand-in `anthropic` module exposing just the RateLimitError class that generate()'s except clause references.'''

    mod = ModuleType('anthropic')

    class RateLimitError(Exception):

        def __init__(self, *args, response=None, **kw):
            super().__init__(*args)
            self.response = response

    mod.RateLimitError = RateLimitError
    return mod

def anthropicClient(response=None, exc=None):
    '''Fake anthropic client whose messages.create returns `response` or raises `exc`.'''

    def create(**kwargs):

        if exc:
            raise exc

        return response

    return SimpleNamespace(messages=SimpleNamespace(create=create))

class TestAnthropicProvider(unittest.TestCase):

    def setUp(self):

        self.fake = makeFakeAnthropic()
        patcher = mock.patch.dict(sys.modules, {'anthropic': self.fake})
        patcher.start()
        self.addCleanup(patcher.stop)

        self.provider = AIRules.AnthropicProvider()

    def test_returns_tool_input(self):

        block = SimpleNamespace(type='tool_use', name='submit_rule', input={'rule_xml': 'RX', 'new_defs': []})
        response = SimpleNamespace(stop_reason='tool_use', content=[block])
        client = anthropicClient(response=response)

        result = self.provider.generate(client, 'claude-x', 'SYS', 'USER', AIRules.TASK_RULE)

        self.assertEqual(result, {'rule_xml': 'RX', 'new_defs': []})

    def test_explain_task_uses_explanation_tool(self):

        block = SimpleNamespace(type='tool_use', name='submit_explanation', input={'explanation': 'E', 'language': 'en'})
        response = SimpleNamespace(stop_reason='tool_use', content=[block])
        client = anthropicClient(response=response)

        result = self.provider.generate(client, 'claude-x', 'SYS', 'USER', AIRules.TASK_EXPLAIN)

        self.assertEqual(result['explanation'], 'E')

    def test_refusal_raises(self):

        response = SimpleNamespace(stop_reason='refusal', content=[])
        client = anthropicClient(response=response)

        with self.assertRaises(RuntimeError):
            self.provider.generate(client, 'claude-x', 'SYS', 'USER')

    def test_missing_tool_call_raises(self):

        block = SimpleNamespace(type='text', name=None, input=None)
        response = SimpleNamespace(stop_reason='end_turn', content=[block])
        client = anthropicClient(response=response)

        with self.assertRaises(RuntimeError):
            self.provider.generate(client, 'claude-x', 'SYS', 'USER')

    def test_rate_limit_with_retry_header(self):

        err = self.fake.RateLimitError('rate limited', response=SimpleNamespace(headers={'retry-after': '15'}))
        client = anthropicClient(exc=err)

        with self.assertRaises(AIRules.RateLimitError) as ctx:
            self.provider.generate(client, 'claude-x', 'SYS', 'USER')

        self.assertEqual(ctx.exception.retryAfter, 15.0)
        self.assertEqual(ctx.exception.providerDisplay, self.provider.displayName)

    def test_rate_limit_with_bad_retry_header(self):

        err = self.fake.RateLimitError('rate limited', response=SimpleNamespace(headers={'retry-after': 'soon'}))
        client = anthropicClient(exc=err)

        with self.assertRaises(AIRules.RateLimitError) as ctx:
            self.provider.generate(client, 'claude-x', 'SYS', 'USER')

        self.assertIsNone(ctx.exception.retryAfter)

# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def installFakeGemini(testcase):
    '''Install fake `google` / `google.genai` modules (with types + errors) for the duration of the test. Returns the APIError class the tests raise.'''

    class APIError(Exception):

        def __init__(self, message, code=None):
            super().__init__(message)
            self.code = code

    googleMod = ModuleType('google')
    genaiMod = ModuleType('google.genai')
    genaiMod.types = SimpleNamespace(GenerateContentConfig=lambda **kw: SimpleNamespace(**kw))
    genaiMod.errors = SimpleNamespace(APIError=APIError)
    googleMod.genai = genaiMod

    patcher = mock.patch.dict(sys.modules, {'google': googleMod, 'google.genai': genaiMod})
    patcher.start()
    testcase.addCleanup(patcher.stop)
    return APIError

def geminiClient(response=None, exc=None):

    def generate_content(**kwargs):

        if exc:
            raise exc

        return response

    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))

class TestGeminiProvider(unittest.TestCase):

    def setUp(self):

        self.APIError = installFakeGemini(self)
        self.provider = AIRules.GeminiProvider()

    def test_parses_json_text(self):

        response = SimpleNamespace(text='{"rule_xml": "RX", "explanation": "E"}', prompt_feedback=None)
        client = geminiClient(response=response)

        result = self.provider.generate(client, 'gemini-x', 'SYS', 'USER', AIRules.TASK_RULE)

        self.assertEqual(result, {'rule_xml': 'RX', 'explanation': 'E'})

    def test_empty_response_raises(self):

        response = SimpleNamespace(text='', prompt_feedback='blocked: safety')
        client = geminiClient(response=response)

        with self.assertRaises(RuntimeError) as ctx:
            self.provider.generate(client, 'gemini-x', 'SYS', 'USER')

        self.assertIn('blocked: safety', str(ctx.exception))

    def test_429_becomes_rate_limit_error(self):

        err = self.APIError('Quota exceeded, retry in 12s', code=429)
        client = geminiClient(exc=err)

        with self.assertRaises(AIRules.RateLimitError) as ctx:
            self.provider.generate(client, 'gemini-x', 'SYS', 'USER')

        self.assertEqual(ctx.exception.retryAfter, 12.0)

    def test_other_api_error_propagates(self):

        err = self.APIError('Internal error', code=500)
        client = geminiClient(exc=err)

        with self.assertRaises(self.APIError):
            self.provider.generate(client, 'gemini-x', 'SYS', 'USER')

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

def makeFakeOpenAI():

    mod = ModuleType('openai')

    class RateLimitError(Exception):
        pass

    mod.RateLimitError = RateLimitError

    class OpenAI:  # referenced by makeClient, not by generate; present for completeness
        def __init__(self, api_key=None):
            self.api_key = api_key

    mod.OpenAI = OpenAI
    return mod

def openaiClient(message=None, exc=None):

    def create(**kwargs):

        if exc:
            raise exc

        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

class TestOpenAIProvider(unittest.TestCase):

    def setUp(self):

        self.fake = makeFakeOpenAI()
        patcher = mock.patch.dict(sys.modules, {'openai': self.fake})
        patcher.start()
        self.addCleanup(patcher.stop)

        self.provider = AIRules.OpenAIProvider()

    def test_parses_json_content(self):

        message = SimpleNamespace(refusal=None, content='{"rule_xml": "RX"}')
        client = openaiClient(message=message)

        result = self.provider.generate(client, 'gpt-x', 'SYS', 'USER', AIRules.TASK_RULE)

        self.assertEqual(result, {'rule_xml': 'RX'})

    def test_refusal_raises(self):

        message = SimpleNamespace(refusal='I cannot help with that', content=None)
        client = openaiClient(message=message)

        with self.assertRaises(RuntimeError) as ctx:
            self.provider.generate(client, 'gpt-x', 'SYS', 'USER')

        self.assertIn('cannot help', str(ctx.exception))

    def test_empty_content_raises(self):

        message = SimpleNamespace(refusal=None, content='')
        client = openaiClient(message=message)

        with self.assertRaises(RuntimeError):
            self.provider.generate(client, 'gpt-x', 'SYS', 'USER')

    def test_rate_limit_becomes_rate_limit_error(self):

        client = openaiClient(exc=self.fake.RateLimitError('slow down, retry in 8s'))

        with self.assertRaises(AIRules.RateLimitError) as ctx:
            self.provider.generate(client, 'gpt-x', 'SYS', 'USER')

        self.assertEqual(ctx.exception.retryAfter, 8.0)

if __name__ == '__main__':
    unittest.main()
