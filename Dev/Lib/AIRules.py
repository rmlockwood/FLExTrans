#
#   AIRules
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.18 - 7/16/26 - Ron Lockwood
#    The macro-name token pattern now also recognizes the bare lowercase-m form (mCopyGender - a lowercase m directly followed by a capitalized name), not only m_snake_case, so a macro
#    referenced that way in a description is spotted. The capital keeps it from matching ordinary m-words like "modify"/"move".
#
#   Version 3.16.17 - 7/16/26 - Ron Lockwood
#    findMacroMentions now flags a mistyped macro name that is a plain word (e.g. "call the macro asldkjfsdf") as missing, not just m_-style or identifier-shaped tokens: a word next to
#    "macro" that isn't a common function word (UILanguages.MACRO_STOP_WORDS) and doesn't match an existing macro is reported, while prose like "the macro that copies gender" is left alone.
#
#   Version 3.16.16 - 7/16/26 - Ron Lockwood
#    A malformed (e.g. truncated) JSON reply from Gemini or OpenAI now raises an error that names the provider/model and suggests retrying, instead of a bare "Unterminated string" parse
#    error. The authorship comment no longer pads its sentence with spaces inside the <!-- -->, matching the house comment style.
#
#   Version 3.16.15 - 7/16/26 - Ron Lockwood
#    The shipped sample/reference definitions (m_sample, v_sample, l_sample, a_sample) are now excluded from the definition summary and style examples sent to the AI, alongside the existing
#    "Sample logic to copy and paste" rule; the m_sample macro is also kept out of the macro picker and reference macros (never shown, modified, explained, or sent). See SAMPLE_DEF_NAMES.
#
#   Version 3.16.14 - 7/16/26 - Ron Lockwood
#    The macro-mention regexes are now built from per-UI-language word lists (UILanguages.MACRO_NOUNS / MACRO_NAMING_WORDS) instead of hard-coded English/German spellings, so each UI
#    language's ways of saying 'the macro called X' are recognized and new languages can add theirs in one place.
#
#   Version 3.16.13 - 7/16/26 - Ron Lockwood
#    Macro support: rules AND macros can now be created, modified, and explained (isMacro flows through buildUserContent, spliceIntoTemp, markAuthorship, generateValidatedRule, and applyRule);
#    extractExistingDefs also returns a {name: def-macro-XML} map; macros a rule calls (recursively) and macros the user's request names (partial match) can be gathered into the prompt
#    (findCalledMacroNames / collectCalledMacros / findMacroMentions); the explain prompt now asks for Markdown, plain non-technical wording, no angle-bracket tags, and an opening walk-through
#    of what each pattern item's category matches; the reference rule "Sample logic to copy and paste" is excluded from the rule list, the prompt summary, and the style examples.
#
#   Version 3.16.12 - 7/10/26 - Ron Lockwood
#    Dropped the transfer.dtd dependency: apertium-preprocess-transfer validates without the DTD present (as in the published Build makefile), so generateValidatedRule no longer copies a DTD
#    into its scratch dir and validateFile no longer takes a dtdPath. The written temp file keeps its DOCTYPE (matching real transfer files; XXE resolves it via its own addon).
#
#   Version 3.16.11 - 7/10/26 - Ron Lockwood
#    Type fix: getSampleRulesAndMacros and extractExistingDefs now type transferPath as Optional[str] (it defaults to None), with an assert documenting that a root or a transferPath must be given.
#
#   Version 3.16.10 - 7/9/26 - Ron Lockwood
#    Added parseTransferFile so the transfer file is parsed only once at startup: extractExistingDefs and getSampleRulesAndMacros now accept a pre-parsed root (the module parses once
#    and passes it to both) instead of each re-reading and re-parsing the whole file.
#
#   Version 3.16.9 - 7/7/26 - Ron Lockwood
#    Review fixes: applyRule's modify now locates the rule to replace via an XML parse (robust to escaped chars / quote style in the comment) and replaces it by position, refusing to
#    write rather than silently appending a duplicate when it can't match; the generate scratch directory is removed in a finally; very large def-cat/def-list member lists are capped in
#    the prompt summary with a "(… N more)" marker.
#
#   Version 3.16.8 - 7/7/26 - Ron Lockwood
#    extractExistingDefs also returns a {comment: rule-XML} map built in the same parse, so the dialog can cache it and render a picked rule's preview without re-reading the file.
#
#   Version 3.16.7 - 7/6/26 - Ron Lockwood
#    buildUserContent takes optional interlinearized source/target example data (pasted by the user in the dialog's data grids) and adds it to the prompt as its own sections.
#
#   Version 3.16.6 - 7/6/26 - Ron Lockwood
#    The explain mode's language is now named in the prompt (buildUserContent's explainLang is a language name, e.g. "Spanish", not an ISO code), so the user can request any language.
#
#   Version 3.16.5 - 7/5/26 - Ron Lockwood
#    New explain task: each provider's generate() now takes a task argument selecting the rule schema or a new explanation schema and returns the parsed JSON dict; explainRule() asks
#    for a thorough plain-language explanation of an existing rule (answered in the interface language via buildUserContent's explain mode).
#
#   Version 3.16.4 - 7/4/26 - Ron Lockwood
#    The prompt's definition summary now enumerates the contents of each def-cat (the cat-item tags, and the lemma when a category is lemma-specific) and each def-list (its items),
#    instead of only listing category and list names.
#
#   Version 3.16.3 - 7/4/26 - Ron Lockwood
#    The authorship-stamp date/time is now localized to the interface language: markAuthorship / generateValidatedRule accept a preformatted whenStr from the Qt-side caller, with a
#    plain English date as the standalone fallback. The authorship sentences are also whole localized sentences (chosen by mode) rather than a verb interpolated into a fixed frame.
#
#   Version 3.16.2 - 7/4/26 - Ron Lockwood
#    API keys are now stored per provider in the credential vault (a slot per provider name), so switching providers no longer loses a previously entered key. The old single-slot key
#    is migrated to the active provider's slot on first read.
#
#   Version 3.16.1 - 7/3/26 - Ron Lockwood
#    Added the OpenAI (ChatGPT) provider, made Gemini's free model the default, per-provider model lists for the Settings tool, optional prompt/response logging for debugging, and
#    prompt grounding with the project's longest rules and macros.
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. Core logic for the "Work on Rules with AI" module: assemble the prompt, call the configured AI provider (Anthropic by default, Gemini or others selectable) to generate or
#    modify an Apertium transfer rule, and run the generated rule through a DTD + compile validation-retry loop. No Qt and no FLEx dependencies here so it can be exercised standalone.
#
#   Given a plain-language description (and, for modifications, an existing rule), ask the provider for an Apertium <rule> plus any supporting definitions, then splice it into a copy of the
#   transfer file and validate before returning it.

import os
import re
import shutil
import tempfile
import datetime
import subprocess
import dataclasses
from typing import Optional, cast
import xml.etree.ElementTree as ET

# Qt-free by design (see the module comment), so importing it here keeps AIRules usable standalone.
import UILanguages

# Generation settings. The provider and model are chosen from config (see getProvider / buildEngine); these limits are provider-independent.
MAX_TOKENS = 16000
MAX_VALIDATION_ATTEMPTS = 3
# Cap on how many members of a single def-cat or def-list we spell out in the prompt summary. Typical categories/lists are well under this; the cap only bites on a project with an
# unusually large list, keeping one huge def-list from inflating the (uncached) per-request prompt without limit. When it bites, the omitted count is shown so nothing is silently dropped.
MAX_SUMMARY_ITEMS = 80
DEFAULT_PROVIDER = 'gemini'

# The reference rule that ships in the transfer-file template as sample logic to copy from. It is not a real rule of the project, so it is never shown in the rule picker and never sent to the
# AI in any form - not in the rule-name summary, not as a style example, and never as a rule to modify or explain.
SAMPLE_LOGIC_RULE_NAME = 'Sample logic to copy and paste'

# The sample/reference definitions that ship in the transfer-file template alongside SAMPLE_LOGIC_RULE_NAME - one placeholder per definition kind (macro, variable, list, attribute). Like the
# sample rule they are not real definitions of the project, so they are excluded from the definition summary sent to the AI and from the style examples; the sample macro is also kept out of the
# macro picker and the reference macros (so it is never shown, modified, explained, or sent). The one-letter prefixes make each name unique to its kind, so a single set can filter them all.
SAMPLE_DEF_NAMES = {'m_sample', 'v_sample', 'l_sample', 'a_sample'}

# When set (by the module, from the AIRulesLogPrompts setting), every prompt sent to the provider and every response received is appended to this file. Off by default for shipping;
# a support person can turn it on in the Settings tool (Full view) to debug on a user's machine. The log can contain project data, so it is opt-in only.
PROMPT_LOG_PATH: Optional[str] = None

def logPromptTraffic(title: str, text: str) -> None:
    '''Append one titled block to the prompt log when logging is enabled. Never raises - a broken log path must not break generation.'''

    if not PROMPT_LOG_PATH:
        return

    try:

        with open(PROMPT_LOG_PATH, 'a', encoding='utf-8') as fout:
            fout.write('===== {title} at {when} =====\n{text}\n\n'.format(title=title, when=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text=text))

    except OSError:
        pass

class RateLimitError(RuntimeError):
    '''A provider returned HTTP 429. Carries the provider display name and, when the response gave one, how many seconds to wait before retrying. Its str() is a clean,
    user-facing message (the callers show it directly).'''

    def __init__(self, providerDisplay: str, retryAfter: Optional[float] = None):

        self.providerDisplay = providerDisplay
        self.retryAfter = retryAfter
        super().__init__(str(self))

    def __str__(self):

        msg = '{provider} is rate limited (HTTP 429).'.format(provider=self.providerDisplay)

        if self.retryAfter:
            msg += ' Try again in about {n} seconds.'.format(n=int(round(self.retryAfter)))

        msg += (' Free tiers have low limits, and some models (e.g. gemini-2.5-pro) are not available on the '
                'free tier at all. Wait and retry, choose a different model with the AIRulesModel setting, or '
                'enable billing on your account.')
        return msg

def parseRetryAfter(text: str) -> Optional[float]:
    '''Best-effort extraction of a retry delay (seconds) from a 429 error's text, covering both the "retry in 28.3s" phrasing and the "retryDelay": "28s" field.'''

    match = re.search(r'retry(?:Delay)?["\']?\s*[:\s]\s*["\']?in?\s*([\d.]+)\s*s', text, re.IGNORECASE)
    if not match:
        match = re.search(r'([\d.]+)\s*s(?:econds)?', text)

    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None

    return None

# Map a definition element's tag to the section it belongs in, so new definitions returned by the model land in the right place.
DEF_TAG_TO_SECTION = {
    'def-cat':   'section-def-cats',
    'def-attr':  'section-def-attrs',
    'def-var':   'section-def-vars',
    'def-list':  'section-def-lists',
    'def-macro': 'section-def-macros',
}

# The result shape both providers must return: the rule XML, any new supporting definitions, and a short explanation.
_RULE_XML_DESC = 'Exactly one <rule comment="...">...</rule> element - or, when the request asks for a macro, exactly one <def-macro n="...">...</def-macro> element. No wrapper, no DOCTYPE.'
_NEW_DEFS_DESC = 'Each string is one new <def-cat>/<def-attr>/<def-var>/<def-list>/<def-macro> element the rule needs and that does not already exist. Empty list if none.'
_EXPLANATION_DESC = 'One or two sentences describing what the rule does. Note here if the rule must be ordered before a more general rule.'
_LANGUAGE_DESC = 'The ISO 639-1 two-letter code of the language the user\'s request is written in (e.g. "en", "es", "de", "fr"). Used to localize the rule preview.'

# Gemini structured-output schema (response_mime_type=application/json + response_schema).
RULE_SCHEMA = {
    'type': 'object',
    'properties': {
        'rule_xml': {'type': 'string', 'description': _RULE_XML_DESC},
        'new_defs': {'type': 'array', 'items': {'type': 'string'}, 'description': _NEW_DEFS_DESC},
        'explanation': {'type': 'string', 'description': _EXPLANATION_DESC},
        'language': {'type': 'string', 'description': _LANGUAGE_DESC},
    },
    'required': ['rule_xml', 'new_defs', 'explanation', 'language'],
    'propertyOrdering': ['rule_xml', 'new_defs', 'explanation', 'language'],
}

# Anthropic tool the model is forced to call (its input is the same JSON object).
SUBMIT_RULE_TOOL = {
    'name': 'submit_rule',
    'description': 'Return the generated Apertium transfer rule and any new supporting definitions it needs.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'rule_xml': {'type': 'string', 'description': _RULE_XML_DESC},
            'new_defs': {'type': 'array', 'items': {'type': 'string'}, 'description': _NEW_DEFS_DESC},
            'explanation': {'type': 'string', 'description': _EXPLANATION_DESC},
            'language': {'type': 'string', 'description': _LANGUAGE_DESC},
        },
        'required': ['rule_xml', 'new_defs', 'explanation', 'language'],
    },
}

# OpenAI structured-output schema (response_format json_schema in strict mode, which requires additionalProperties: false and rejects Gemini's propertyOrdering keyword).
OPENAI_RULE_SCHEMA = {
    'type': 'object',
    'properties': {
        'rule_xml': {'type': 'string', 'description': _RULE_XML_DESC},
        'new_defs': {'type': 'array', 'items': {'type': 'string'}, 'description': _NEW_DEFS_DESC},
        'explanation': {'type': 'string', 'description': _EXPLANATION_DESC},
        'language': {'type': 'string', 'description': _LANGUAGE_DESC},
    },
    'required': ['rule_xml', 'new_defs', 'explanation', 'language'],
    'additionalProperties': False,
}

# The explain task: instead of producing a rule, the model returns a thorough plain-language explanation of an existing rule or macro. Same three per-provider shapes as the rule task.
_LONG_EXPLANATION_DESC = ('A thorough explanation of the whole rule (or macro) for a linguist unaccustomed to reading Apertium rules, written in Markdown and in plain non-technical language: what '
                          'words the pattern matches, what each part of the action does and why, what the output looks like, and how any macros/variables/lists it references contribute. Never wrap '
                          'a tag or category name in angle brackets (write 3s_POSS, not <3s_POSS>). The user content gives the full structure and style requirements.')

# Style requirements sent with every explain request. The explanation is rendered as Markdown in the preview pane, so the model is asked to use real formatting; the rest keeps the text friendly to
# a non-technical reader (no angle-bracket tags, and an opening walk-through of what the pattern's categories are actually defined to match, including lemma-pinned items and the fact that every
# cat-item's first tag is the word's grammatical category from FLEx).
EXPLAIN_STYLE_COMMON = (
    'Follow these style requirements for the explanation:\n'
    '- Write for a non-technical reader: plain language, no XML markup, and no Apertium jargon beyond the names that appear in the rule itself.\n'
    '- Never wrap a tag, category, attribute, or feature name in angle brackets: write 3s_POSS, not <3s_POSS>.\n'
    '- Format the explanation in Markdown (short headings, bold for category/tag/variable/macro names, bullet lists where they make things clearer). The Markdown will be rendered, so the formatting will show.')

EXPLAIN_STYLE_PATTERN = (
    '- Begin by explaining what the pattern matches, item by item: name each pattern item\'s category and spell out what that category is defined to match. The first tag of each cat-item is the '
    'word\'s grammatical category from FLEx, so describe it as the kind of word, with any remaining tags as tags the word carries - for example: "c_UPC matches verbs, prepositions, and adverbs '
    'that end with the UPC tag". Also mention any lemmas that are part of the category definition (a cat-item pinned to a specific lemma matches only that exact word).')

_EXPLAIN_PROPERTIES = {
    'explanation': {'type': 'string', 'description': _LONG_EXPLANATION_DESC},
    'language': {'type': 'string', 'description': _LANGUAGE_DESC},
}

EXPLAIN_SCHEMA = {
    'type': 'object',
    'properties': _EXPLAIN_PROPERTIES,
    'required': ['explanation', 'language'],
    'propertyOrdering': ['explanation', 'language'],
}

SUBMIT_EXPLANATION_TOOL = {
    'name': 'submit_explanation',
    'description': 'Return a thorough plain-language explanation of the given Apertium transfer rule.',
    'input_schema': {
        'type': 'object',
        'properties': _EXPLAIN_PROPERTIES,
        'required': ['explanation', 'language'],
    },
}

OPENAI_EXPLAIN_SCHEMA = {
    'type': 'object',
    'properties': _EXPLAIN_PROPERTIES,
    'required': ['explanation', 'language'],
    'additionalProperties': False,
}

# Task identifiers passed through Engine.generate to pick the schema set.
TASK_RULE = 'rule'
TASK_EXPLAIN = 'explain'

@dataclasses.dataclass
class RuleResult:
    '''The outcome of a generation attempt.'''

    ruleXml: str
    newDefs: list[str]
    explanation: str
    language: str
    valid: bool
    errors: str
    attempts: int

# ---------------------------------------------------------------------------
# Provider layer. Each provider knows how to build its SDK client and how to turn a system instruction + user prompt into the task's JSON object (a dict matching the rule or explain
# schema above, selected by the task argument). To add a provider, implement makeClient() and generate() and register it in PROVIDERS.
# ---------------------------------------------------------------------------

class AnthropicProvider:
    '''Anthropic Claude.'''

    name = 'anthropic'
    displayName = 'Anthropic Claude'
    defaultModel = 'claude-opus-4-8'
    models = ['claude-opus-4-8', 'claude-sonnet-5', 'claude-haiku-4-5-20251001']
    envVars = ('ANTHROPIC_API_KEY',)
    keyUrl = 'https://console.anthropic.com/settings/keys'

    def makeClient(self, apiKey: str):

        import anthropic

        return anthropic.Anthropic(api_key=apiKey)

    def generate(self, client, model: str, systemInstruction: str, userContent: str, task: str = TASK_RULE) -> dict:

        import anthropic

        tool = SUBMIT_RULE_TOOL if task == TASK_RULE else SUBMIT_EXPLANATION_TOOL

        try:
            response = client.messages.create(
                model=model, max_tokens=MAX_TOKENS, thinking={'type': 'adaptive'}, system=[{'type': 'text', 'text': systemInstruction, 'cache_control': {'type': 'ephemeral'}}], tools=[tool],
                tool_choice={'type': 'tool', 'name': tool['name']}, messages=[{'role': 'user', 'content': userContent}], )

        except anthropic.RateLimitError as err:

            retryAfter = None
            retryHeader = getattr(getattr(err, 'response', None), 'headers', {}).get('retry-after')

            if retryHeader:

                try:
                    retryAfter = float(retryHeader)

                except ValueError:
                    pass

            raise RateLimitError(self.displayName, retryAfter)

        if response.stop_reason == 'refusal':
            raise RuntimeError('The model declined this request (stop_reason=refusal).')

        for block in response.content:

            if block.type == 'tool_use' and block.name == tool['name']:
                return cast(dict, block.input)

        raise RuntimeError('The model did not return a {name} tool call.'.format(name=tool['name']))

class GeminiProvider:
    '''Google Gemini (the default provider). Default is gemini-2.5-flash, which is available on the free tier; gemini-2.5-pro requires a billing-enabled (paid) key and returns a 429
    with "limit: 0" on the free tier. Override with the AIRulesModel setting.'''

    name = 'gemini'
    displayName = 'Google Gemini'
    defaultModel = 'gemini-2.5-flash'
    models = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro']
    envVars = ('GEMINI_API_KEY', 'GOOGLE_API_KEY')
    keyUrl = 'https://aistudio.google.com/apikey'

    def makeClient(self, apiKey: str):

        from google import genai

        return genai.Client(api_key=apiKey)

    def generate(self, client, model: str, systemInstruction: str, userContent: str, task: str = TASK_RULE) -> dict:

        import json

        from google.genai import types, errors

        schema = RULE_SCHEMA if task == TASK_RULE else EXPLAIN_SCHEMA

        try:
            response = client.models.generate_content(
                model=model, contents=userContent, config=types.GenerateContentConfig(
                    system_instruction=systemInstruction, max_output_tokens=MAX_TOKENS, response_mime_type='application/json', response_schema=schema, ), )

        except errors.APIError as err:

            if getattr(err, 'code', None) == 429:
                raise RateLimitError(self.displayName, parseRetryAfter(str(err)))

            raise

        payload = getattr(response, 'text', None)

        if not payload:
            feedback = getattr(response, 'prompt_feedback', None)
            raise RuntimeError('The model returned nothing. {feedback}'.format(feedback=feedback or '(response was empty or blocked)'))

        # A truncated or malformed model reply surfaces here as a JSONDecodeError whose bare message ("Unterminated string starting at: line 2 column 15") tells the user nothing about where
        # it came from. Rewrap it so the message names the provider/model and says the practical thing: it's a one-off output glitch, and simply retrying the request usually works.
        try:
            return json.loads(payload)

        except json.JSONDecodeError as err:
            raise RuntimeError('{provider} ({model}) returned a reply that is not valid JSON, so the result could not be read ({err}). This is usually a one-off glitch in the model output - try the same request again.'.format(provider=self.displayName, model=model, err=err))

class OpenAIProvider:
    '''OpenAI (ChatGPT). Uses the chat completions API with a strict JSON-schema response format so the reply parses the same way as the other providers.'''

    name = 'openai'
    displayName = 'OpenAI ChatGPT'
    defaultModel = 'gpt-5.1'
    models = ['gpt-5.1', 'gpt-5', 'gpt-5-mini']
    envVars = ('OPENAI_API_KEY',)
    keyUrl = 'https://platform.openai.com/api-keys'

    def makeClient(self, apiKey: str):

        import openai

        return openai.OpenAI(api_key=apiKey)

    def generate(self, client, model: str, systemInstruction: str, userContent: str, task: str = TASK_RULE) -> dict:

        import json

        import openai

        if task == TASK_RULE:
            responseFormat = {'type': 'json_schema', 'json_schema': {'name': 'submit_rule', 'strict': True, 'schema': OPENAI_RULE_SCHEMA}}
        else:
            responseFormat = {'type': 'json_schema', 'json_schema': {'name': 'submit_explanation', 'strict': True, 'schema': OPENAI_EXPLAIN_SCHEMA}}

        try:
            response = client.chat.completions.create(
                model=model, max_completion_tokens=MAX_TOKENS, response_format=responseFormat,
                messages=[{'role': 'system', 'content': systemInstruction}, {'role': 'user', 'content': userContent}], )

        except openai.RateLimitError as err:
            raise RateLimitError(self.displayName, parseRetryAfter(str(err)))

        message = response.choices[0].message

        if getattr(message, 'refusal', None):
            raise RuntimeError('The model declined this request: ' + message.refusal)

        payload = message.content

        if not payload:
            raise RuntimeError('The model returned nothing (empty response).')

        # Same rewrap as the Gemini provider: name the provider/model and suggest the retry that usually fixes a malformed reply, instead of surfacing a bare JSON parse error.
        try:
            return json.loads(payload)

        except json.JSONDecodeError as err:
            raise RuntimeError('{provider} ({model}) returned a reply that is not valid JSON, so the result could not be read ({err}). This is usually a one-off glitch in the model output - try the same request again.'.format(provider=self.displayName, model=model, err=err))

# Registry of available providers, keyed by the config value. Gemini comes first because its free tier makes it the default; the Settings tool lists them in this order.
PROVIDERS = {
    GeminiProvider.name: GeminiProvider(), AnthropicProvider.name: AnthropicProvider(), OpenAIProvider.name: OpenAIProvider(), }

def findProvider(name: Optional[str]):
    '''Return the provider whose short name or display name matches `name` (case-insensitive), or None when the name is missing or unknown. The Settings tool stores the display name
    (e.g. "Google Gemini"), so both spellings are accepted.'''

    if not name:
        return None

    key = name.strip().lower()

    for provider in PROVIDERS.values():

        if key in (provider.name, provider.displayName.lower()):
            return provider

    return None

def getProvider(name: Optional[str] = None):
    '''Return the provider for `name`, falling back to the default when the name is missing or unknown.'''

    return findProvider(name) or PROVIDERS[DEFAULT_PROVIDER]

def findModelOwner(model: Optional[str]):
    '''Return the provider whose known-models list contains `model`, or None when no provider claims it. Used to reject a provider/model mismatch (e.g. a Claude model with the Gemini
    provider) while still allowing a hand-entered model that is newer than this release's lists.'''

    if not model:
        return None

    for provider in PROVIDERS.values():

        if model in provider.models:
            return provider

    return None

# Per-provider API-key slots in the OS credential vault (Windows Credential Manager / macOS Keychain / Linux Secret Service). Each provider gets its own entry keyed by its short name,
# so the user can store a key for each provider and switching back to a provider keeps its key. Keys are never written to a project file.
KEYRING_SERVICE = 'FLExTrans'
KEYRING_USER_PREFIX = 'AIRulesApiKey'
# The pre-per-provider single slot (its name is the bare prefix). It is migrated to the active provider's slot on first read so an existing user doesn't have to re-enter their key.
LEGACY_KEYRING_USER = 'AIRulesApiKey'

def keyringUser(provider) -> str:
    '''The vault entry name for a provider's API key, e.g. "AIRulesApiKey:anthropic".'''

    return '{prefix}:{name}'.format(prefix=KEYRING_USER_PREFIX, name=provider.name)

def getStoredApiKey(provider) -> Optional[str]:
    '''Read the API key stored for `provider` from the OS credential vault. Returns None if none is stored, or if keyring / its backend is unavailable.'''

    try:
        import keyring

        key = keyring.get_password(KEYRING_SERVICE, keyringUser(provider))
        if key:
            return key

        # One-time migration: an existing user's key was stored in a single, provider-agnostic slot. Treat it as belonging to the provider being asked about now (their configured
        # provider) - move it into that provider's slot and delete the old one so it can't later be reused for a different provider.
        legacy = keyring.get_password(KEYRING_SERVICE, LEGACY_KEYRING_USER)

        if legacy:

            keyring.set_password(KEYRING_SERVICE, keyringUser(provider), legacy)

            try:
                keyring.delete_password(KEYRING_SERVICE, LEGACY_KEYRING_USER)

            except Exception:
                pass

            return legacy

        return None

    except Exception:
        return None

def setStoredApiKey(provider, apiKey: str) -> None:
    '''Store `provider`'s API key in the OS credential vault. Raises if keyring or its backend is unavailable (the caller reports it).'''

    import keyring
    keyring.set_password(KEYRING_SERVICE, keyringUser(provider), apiKey)

def resolveApiKey(provider) -> Optional[str]:
    '''Resolve `provider`'s API key: the OS credential vault wins (set via the in-app dialog), then the provider's env var(s) as a fallback, then None so the caller can prompt the user
    (BYOK). Keys are never read from or written to a project file.'''

    stored = getStoredApiKey(provider)
    if stored:
        return stored

    for var in provider.envVars:

        value = os.environ.get(var)
        if value:
            return value

    return None

class Engine:
    '''A provider + its client + the model to use. This is what flows through the generation calls, so the rest of the module is provider-agnostic.'''

    def __init__(self, provider, client, model: str):

        self.provider = provider
        self.client = client
        self.model = model

    def generate(self, systemInstruction: str, userContent: str, task: str = TASK_RULE) -> dict:

        # When debug logging is on, record exactly what goes out and what comes back (or the error), so we can diagnose bad generations on a user's machine.
        logPromptTraffic('PROMPT to {provider} ({model}, task={task})'.format(provider=self.provider.displayName, model=self.model, task=task), 'SYSTEM INSTRUCTION:\n' + systemInstruction + '\n\nUSER CONTENT:\n' + userContent)

        try:
            result = self.provider.generate(self.client, self.model, systemInstruction, userContent, task)

        except Exception as err:

            logPromptTraffic('ERROR from {provider}'.format(provider=self.provider.displayName), str(err))
            raise

        logPromptTraffic('RESPONSE from {provider}'.format(provider=self.provider.displayName), repr(result))
        return result

def buildEngine(providerName: Optional[str], apiKey: str, model: Optional[str] = None) -> Engine:
    '''Construct the Engine for the configured provider. `model` overrides the provider default when given (config setting). SDKs are imported lazily inside makeClient, so only the
    selected provider's SDK needs to be installed.'''

    provider = getProvider(providerName)
    client = provider.makeClient(apiKey)
    return Engine(provider, client, model or provider.defaultModel)

def parseTransferFile(transferPath: str):
    '''Parse the transfer file once and return its root element. A caller that needs several things out of the same file (the module's startup does both extractExistingDefs and
    getSampleRulesAndMacros) parses here once and passes the root to each, instead of every function re-reading and re-parsing the whole file. insert_comments keeps the file's XML
    comments in the tree so rule text round-trips faithfully.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.parse(transferPath, parser=parser).getroot()

def getSampleRulesAndMacros(transferPath: Optional[str] = None, ruleCount: int = 4, macroCount: int = 2, root=None) -> tuple:
    '''Pull the longest rules (up to `ruleCount`) and longest macros (up to `macroCount`) from the project's transfer file, to show the model the house style with the richest examples
    available. The slices naturally guard against files with fewer rules or no macros. Returns (rulesText, macrosText), each a blank-line-separated string ('' when none exist).
    Pass an already-parsed `root` to reuse a single parse (see parseTransferFile); otherwise `transferPath` is parsed here.'''

    if root is None:

        assert transferPath is not None, 'getSampleRulesAndMacros needs either a parsed root or a transferPath.'
        root = parseTransferFile(transferPath)

    # The shipped "Sample logic to copy and paste" reference rule and the m_sample reference macro are not project style, so they never serve as examples.
    ruleTexts = sorted((ET.tostring(r, encoding='unicode') for r in root.findall('.//rule') if r.get('comment', '') != SAMPLE_LOGIC_RULE_NAME), key=len, reverse=True)[:ruleCount]
    macroTexts = sorted((ET.tostring(m, encoding='unicode') for m in root.findall('.//def-macro') if m.get('n', '') not in SAMPLE_DEF_NAMES), key=len, reverse=True)[:macroCount]

    return '\n\n'.join(ruleTexts), '\n\n'.join(macroTexts)

def buildSystemInstruction(conventionsText: str, sampleRulesText: str, sampleMacrosText: str = '') -> str:
    '''Build the system instruction: the house conventions plus real example rules and macros from the project. The transfer.dtd is intentionally NOT included - the model already knows
    the Apertium transfer format, so the DTD is ~5k low-value tokens, and the validation-retry loop (well-formedness + apertium-preprocess-transfer) is the authoritative structural check.
    This prefix is identical across requests, so it caches well (Anthropic cache_control / Gemini implicit caching).'''

    text = conventionsText

    if sampleRulesText:
        text += '\n\nExample rules from this project, for style reference (these are the longest rules in the file; your rule can be much simpler):\n\n' + sampleRulesText

    if sampleMacrosText:
        text += '\n\nExample macros from this project, for style reference:\n\n' + sampleMacrosText

    return text

def capItemsForSummary(items: list) -> list:
    '''Return `items` for the prompt summary, capped at MAX_SUMMARY_ITEMS with a trailing "(… N more)" marker when it's longer, so one very large def-list/def-cat can't blow up the
    per-request prompt. The marker makes the truncation explicit (to the model, and in the prompt log) rather than silently dropping members.'''

    if len(items) <= MAX_SUMMARY_ITEMS:
        return items

    return items[:MAX_SUMMARY_ITEMS] + ['(… {n} more)'.format(n=len(items) - MAX_SUMMARY_ITEMS)]

def extractExistingDefs(transferPath: Optional[str] = None, root=None) -> dict:
    '''Read the transfer file and collect the names of definitions that already exist (so the model reuses them) plus the value sets of each attribute and the existing rule names.
    Returns a dict with both the raw data and a text summary suitable for dropping into the prompt. Pass an already-parsed `root` to reuse a single parse (see parseTransferFile);
    otherwise `transferPath` is parsed here.'''

    if root is None:

        assert transferPath is not None, 'extractExistingDefs needs either a parsed root or a transferPath.'
        root = parseTransferFile(transferPath)

    # For categories, gather the contents of each def-cat - the tags of every cat-item and, when a cat-item is lemma-specific, the lemma - so the model sees exactly what each category
    # matches (and which categories are pinned to a particular lemma) rather than only the names.
    catItems = {}

    for c in root.findall('.//def-cat'):

        items = []

        for it in c.findall('./cat-item'):

            tags = it.get('tags', '')
            lemma = it.get('lemma')
            items.append('{tags} (lemma {lemma})'.format(tags=tags, lemma=lemma) if lemma else tags)

        catItems[c.get('n', '')] = items

    cats = list(catItems.keys())
    variables = [v.get('n', '') for v in root.findall('.//def-var') if v.get('n', '') not in SAMPLE_DEF_NAMES]

    # For macros, keep the full XML of each one (keyed by name) as well as the name list: the macro picker in the dialog renders and edits macros from this map, and macros a rule calls (or the
    # user's request names) are pulled from it into the prompt so the model sees what a call-macro invocation actually does. The shipped m_sample reference macro is left out entirely (like the
    # sample rule), so it appears neither in the picker nor in anything sent to the AI.
    macroElems = [m for m in root.findall('.//def-macro') if m.get('n', '') not in SAMPLE_DEF_NAMES]
    macros = [m.get('n', '') for m in macroElems]
    macroXml = {m.get('n', ''): ET.tostring(m, encoding='unicode') for m in macroElems}

    # For attributes, gather the tag values too so the model knows which tags are legal for each attribute.
    attrs = {}

    for a in root.findall('.//def-attr'):

        if a.get('n', '') in SAMPLE_DEF_NAMES:
            continue

        attrs[a.get('n', '')] = sorted(i.get('tags', '') for i in a.findall('./attr-item'))

    # For lists, gather the contents of each def-list - the value of every list-item - so the model sees the actual members of each list, not only its name.
    listItems = {}

    for lst in root.findall('.//def-list'):

        if lst.get('n', '') in SAMPLE_DEF_NAMES:
            continue

        listItems[lst.get('n', '')] = [li.get('v', '') for li in lst.findall('./list-item')]

    lists = list(listItems.keys())

    # Gather the rules once: their comments (used as display names in the picker) and, keyed by comment, each rule's XML text. The dialog caches this map so clicking a rule in the
    # picker renders instantly instead of re-reading and re-parsing the whole transfer file on every selection. The shipped "Sample logic to copy and paste" reference rule is left out
    # entirely - it is not a real rule, so it appears neither in the picker nor in anything sent to the AI.
    rules = [r for r in root.findall('.//rule') if r.get('comment', '') != SAMPLE_LOGIC_RULE_NAME]
    ruleNames = [r.get('comment', '') for r in rules]
    ruleXml = {r.get('comment', ''): ET.tostring(r, encoding='unicode') for r in rules}

    # Build a text summary for the prompt.
    lines = []
    lines.append('Existing categories (def-cat) with the cat-item tags each one matches (a lemma in parentheses means that item is pinned to that specific lemma):')

    for name in sorted(catItems):
        lines.append('  {name}: {items}'.format(name=name, items='; '.join(capItemsForSummary(catItems[name])) or '(empty)'))

    lines.append('')
    lines.append('Existing attributes (def-attr) and their legal tag values:')

    for name in sorted(attrs):
        lines.append('  {name}: {values}'.format(name=name, values=', '.join(attrs[name])))

    lines.append('')
    lines.append('Existing lists (def-list) with their items:')

    if listItems:

        for name in sorted(listItems):
            lines.append('  {name}: {items}'.format(name=name, items=', '.join(capItemsForSummary(listItems[name])) or '(empty)'))

    else:
        lines.append('  (none)')

    lines.append('')
    lines.append('Existing variables (def-var): ' + (', '.join(variables) or '(none)'))
    lines.append('Existing macros (def-macro): ' + (', '.join(macros) or '(none)'))
    lines.append('')
    lines.append('Existing rule names (comment): ' + ', '.join(ruleNames))

    return {
        'cats': cats, 'catItems': catItems, 'attrs': attrs, 'variables': variables, 'lists': lists, 'listItems': listItems, 'macros': macros, 'macroXml': macroXml, 'ruleNames': ruleNames, 'ruleXml': ruleXml, 'summaryText': '\n'.join(lines), }

def getRuleXmlByComment(transferPath: str, comment: str) -> Optional[str]:
    '''Return the XML text of the rule whose comment matches, or None.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(transferPath, parser=parser).getroot()

    for rule in root.findall('.//rule'):

        if rule.get('comment') == comment:
            return ET.tostring(rule, encoding='unicode')

    return None

def findCalledMacroNames(xmlText: str) -> list:
    '''The names of the macros a rule or macro fragment calls (its <call-macro n="..."/> elements), in document order without duplicates. Returns [] when the fragment can't be parsed -
    the validation loop reports the real XML error later.'''

    try:
        elem = ET.fromstring(xmlText, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))

    except ET.ParseError:
        return []

    names = []

    for call in elem.iter('call-macro'):

        name = call.get('n')

        if name and name not in names:
            names.append(name)

    return names

def collectCalledMacros(xmlText: str, macroXmlByName: dict, excludeNames=None) -> list:
    '''Collect, recursively, the names of every macro that `xmlText` (a rule or a macro) calls - including macros called by those macros in turn - in first-encountered order. Names in
    `excludeNames` (e.g. the macro being modified itself, whose XML is already in the prompt) and names with no definition in `macroXmlByName` are left out.'''

    seen = set(excludeNames or [])
    ordered = []
    queue = findCalledMacroNames(xmlText)

    while queue:

        name = queue.pop(0)

        if name in seen:
            continue

        seen.add(name)
        macroXml = macroXmlByName.get(name)

        if macroXml is None:
            continue

        ordered.append(name)
        queue.extend(findCalledMacroNames(macroXml))

    return ordered

# How a macro reference is spotted in the user's request text: any token following the macro naming convention - m_snake_case, or a bare lowercase-m prefix directly followed by a capitalized
# name (mCopyGender) - or an identifier-looking word right next to the word for "macro" (optionally skipping a filler word like "called"/"named" and an opening quote). The "macro" nouns and
# naming fillers, per UI language, live in UILanguages.MACRO_NOUNS / MACRO_NAMING_WORDS; the patterns are built from the union across all UI languages, since a description may be written in
# any of them regardless of the interface language currently chosen.
def wordAlternatives(wordsByLang: dict) -> str:
    '''Turn the per-language word lists into one regex alternation: the union of every language's words, longest first (so "macros" is tried before "macro"), each escaped, with the
    internal spaces of a multi-word phrase ("mit dem Namen") matching any whitespace.'''

    words = sorted({word for words in wordsByLang.values() for word in words}, key=len, reverse=True)
    return '|'.join(re.escape(word).replace(re.escape(' '), r'\s+') for word in words)

# A macro-name token: the m_snake_case form (m_ then word chars), or a bare lowercase m directly followed by a capital and more word chars (mCopyGender). The capital in the second form is
# what keeps it from matching ordinary m-words like "modify"/"move"/"make" (and it is deliberately case-sensitive - no re.IGNORECASE - so "Makro"/"Modify" don't match either).
MACRO_TOKEN_PATTERN = re.compile(r'\bm(?:_\w+|[A-Z]\w*)\b')
MACRO_AFTER_PATTERN = re.compile(r'\b(?:' + wordAlternatives(UILanguages.MACRO_NOUNS) + r')\s+(?:(?:' + wordAlternatives(UILanguages.MACRO_NAMING_WORDS) + r')\s+)?["\'«‘“]?([A-Za-z_][\w-]*)', re.IGNORECASE)
MACRO_BEFORE_PATTERN = re.compile(r'([A-Za-z_][\w-]*)["\'»’”]?\s+(?:' + wordAlternatives(UILanguages.MACRO_NOUNS) + r')\b', re.IGNORECASE)

# The function words that can sit next to "macro" in prose without being a macro name (union of every UI language's list; see UILanguages.MACRO_STOP_WORDS), lowercased for case-insensitive
# lookup. A word captured next to "macro" that is not one of these - and doesn't match an existing macro - is taken to be a mistyped macro name and reported, so "call the macro asldkjfsdf"
# is flagged while "the macro that copies gender" is not.
MACRO_STOP_WORDS = {word.lower() for words in UILanguages.MACRO_STOP_WORDS.values() for word in words}

def looksLikeMacroIdentifier(token: str) -> bool:
    '''Whether a word looks like an identifier (contains an underscore or a digit) rather than ordinary prose. An identifier-shaped token is treated as a macro name even when it isn't
    adjacent to the word "macro".'''

    return '_' in token or any(ch.isdigit() for ch in token)

def findMacroMentions(description: str, macroNames) -> tuple:
    '''Find the macros the user's request text refers to. Returns (foundNames, missingTokens): foundNames are existing macro names matched by some token in the text (partial and
    case-insensitive, in either direction - the token can be part of the name or the name part of the token), in the order encountered; missingTokens are tokens that name a macro but match
    no existing macro, so the caller can warn and not send the prompt until the user fixes the name.

    A token counts as naming a macro when it follows the naming convention (m_snake_case, or a bare lowercase m + capitalized name like mCopyGender - matched anywhere), or when it sits
    right next to the word "macro" (before or after it) and is neither a common function word (UILanguages.MACRO_STOP_WORDS - "the", "that", "for", …) nor too short to be a real name. This
    is what lets a plain typo like "call the macro asldkjfsdf" be reported as missing, while "the macro that copies gender" is left alone.'''

    found = []
    missing = []
    considered = set()

    def classify(token: str, definite: bool):
        '''Record one candidate token. `definite` is True for the unambiguous naming-convention forms (m_snake_case / mCamelCase, always a macro reference); otherwise the token was captured
        next to the word "macro" and only counts as a name when it isn't a stop word and is long enough (or identifier-shaped).'''

        key = token.lower()

        if key in considered:
            return

        considered.add(key)

        # A word captured next to "macro" that is a common function word or too short to be a name is prose, not a macro reference: drop it before matching. (This must precede the substring
        # match below - otherwise a tiny word like "the" would match a macro that merely contains it, e.g. "the" inside "m_o[the]r".) Convention-form tokens (definite) are always references.
        if not definite and (key in MACRO_STOP_WORDS or not (looksLikeMacroIdentifier(token) or len(token) >= 4)):
            return

        matches = [name for name in macroNames if key in name.lower() or name.lower() in key]

        if matches:

            for name in matches:

                if name not in found:
                    found.append(name)

            return

        missing.append(token)

    # m_ convention tokens first (unambiguous), then the words captured immediately after / before the word "macro".
    for match in MACRO_TOKEN_PATTERN.finditer(description):
        classify(match.group(0), definite=True)

    for pattern in (MACRO_AFTER_PATTERN, MACRO_BEFORE_PATTERN):

        for match in pattern.finditer(description):
            classify(match.group(1), definite=False)

    return found, missing

def buildUserContent(mode: str, description: str, defsSummary: str, projectData: str, currentRuleXml: Optional[str], explainLang: str = 'English', sourceData: str = '', targetData: str = '', isMacro: bool = False, macrosText: str = '') -> str:
    '''Assemble the volatile per-request part of the prompt: the project's real categories/features, the existing-definition summary, any interlinearized example data the user pasted
    (source and/or target side, tab-separated), any macro definitions to show for reference (`macrosText`: macros the rule calls or the request names), the current rule or macro (when
    modifying or explaining), and the user's request. `isMacro` switches the wording (and the requested output element) from a rule to a def-macro. For the explain mode there is no user
    request text, so `explainLang` names the language to answer in - either what the user typed in the Explanation-language box (e.g. "Spanish", "Swahili") or, when that is blank, the
    FLExTrans interface language.'''

    parts = []
    parts.append('PROJECT DATA (real categories, features, feature values, and affixes from the FLEx projects):')
    parts.append(projectData)
    parts.append('')
    parts.append('DEFINITIONS ALREADY IN THE TRANSFER FILE (reuse these; only create new ones when necessary):')
    parts.append(defsSummary)
    parts.append('')

    # Interlinearized example data the user pasted (typically copied out of FLEx). Real words, glosses, and morpheme breakdowns ground the rule/explanation in how the languages
    # actually behave, so include each side whenever it was given.
    if sourceData:

        parts.append('SOURCE LANGUAGE EXAMPLE DATA (interlinearized text supplied by the user; columns are tab-separated):')
        parts.append(sourceData)
        parts.append('')

    if targetData:

        parts.append('TARGET LANGUAGE EXAMPLE DATA (interlinearized text supplied by the user; columns are tab-separated):')
        parts.append(targetData)
        parts.append('')

    # The definitions of macros the rule/macro being worked on calls (recursively) or the user's request names, so the model sees what a call-macro invocation actually does instead of
    # guessing from the macro's name.
    if macrosText:

        parts.append('MACRO DEFINITIONS FOR REFERENCE (macros called by the rule/macro below, or named in the request):')
        parts.append(macrosText)
        parts.append('')

    if mode == 'explain' and currentRuleXml:

        if isMacro:

            parts.append('MODE: explain the following existing macro (a def-macro). Give a thorough plain-language explanation of the whole macro for someone unaccustomed to reading Apertium '
                         'rules: what the macro is for, what each parameter position stands for, what each part of its logic does and why, and how any variables/lists it references contribute. '
                         'Begin by explaining what the macro is for and what each parameter represents. Do not produce or modify any rule or macro.')
            parts.append(EXPLAIN_STYLE_COMMON)
        else:

            parts.append('MODE: explain the following existing rule. Give a thorough plain-language explanation of the whole rule for someone unaccustomed to reading Apertium rules: what words '
                         'the pattern matches, what each part of the action does and why, what the output looks like, and how any macros/variables/lists it references contribute. Do not produce '
                         'or modify any rule.')
            parts.append(EXPLAIN_STYLE_COMMON)
            parts.append(EXPLAIN_STYLE_PATTERN)

        parts.append('Write the explanation in {lang}. Also set the "language" field to that language\'s two-letter ISO 639-1 code.'.format(lang=explainLang))
        parts.append('MACRO TO EXPLAIN:' if isMacro else 'RULE TO EXPLAIN:')
        parts.append(currentRuleXml)
        return '\n'.join(parts)

    if mode == 'modify' and currentRuleXml:

        if isMacro:

            parts.append('MODE: modify the following existing macro (a def-macro). Keep its name (the n attribute) unless asked to rename it, and keep npar correct for its parameters. Return the '
                         'complete modified <def-macro> element in the rule_xml field.')
            parts.append('CURRENT MACRO:')
        else:

            parts.append('MODE: modify the following existing rule. Keep its comment unless asked to rename it.')
            parts.append('CURRENT RULE:')

        parts.append(currentRuleXml)

    elif isMacro:
        parts.append('MODE: create a new macro, not a rule: return exactly one <def-macro n="m_..."> element in the rule_xml field, with npar set to its number of parameters and a plain-language '
                     'description comment as its first child (as you would for a rule).')
    else:
        parts.append('MODE: create a new rule.')

    parts.append('')
    parts.append('USER REQUEST:')
    parts.append(description)

    return '\n'.join(parts)

def generateRule(engine: Engine, systemInstruction: str, userContent: str, priorErrors: Optional[str] = None) -> tuple:
    '''Make one generation call through the engine and return (ruleXml, newDefs, explanation, language). On a validation retry the prior errors are appended so the model can fix them.'''

    text = userContent

    if priorErrors:
        text += ('\n\nYour previous rule failed validation with these errors. Fix them and resubmit:\n'
                 + priorErrors)

    data = engine.generate(systemInstruction, text, TASK_RULE)
    return data['rule_xml'], data.get('new_defs', []), data.get('explanation', ''), data.get('language', '')

def explainRule(engine: Engine, systemInstruction: str, userContent: str) -> tuple:
    '''Ask the provider for a thorough plain-language explanation of an existing rule (the explain task). Returns (explanation, language). No validation-retry loop - there is nothing
    to compile.'''

    data = engine.generate(systemInstruction, userContent, TASK_EXPLAIN)
    return data.get('explanation', ''), data.get('language', '')

def getSection(root: ET.Element, sectionName: str) -> ET.Element:
    '''Return a section element, matching CreateApertiumRules' section ordering assumption. The sample/real files already contain every section.'''

    elem = root.find(sectionName)

    if elem is None:
        elem = ET.SubElement(root, sectionName)

    return elem

def spliceIntoTemp(transferPath: str, ruleXml: str, newDefs: list[str], mode: str, targetComment: Optional[str], workDir: str, isMacro: bool = False) -> str:
    '''Insert the candidate rule (or, with `isMacro`, the candidate def-macro) and any new definitions into a copy of the transfer file, write it to workDir, and return the temp file path.
    For "modify" the rule with targetComment (for macros: the def-macro whose n is targetComment) is replaced; for "create" the element is appended to its section (specific-before-general
    placement is a later refinement).'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(transferPath, parser=parser)
    root = tree.getroot()

    # Add any new definitions to their proper sections.
    for defText in newDefs:

        defElem = ET.fromstring(defText)
        sectionName = DEF_TAG_TO_SECTION.get(defElem.tag)

        if sectionName is None:
            raise RuntimeError('The model returned an unsupported definition element: <{tag}>.'.format(tag=defElem.tag))

        section = getSection(root, sectionName)
        section.append(defElem)

    # Comment-preserving parse so the AI-authorship comment survives into the temp file. A rule lives in section-rules and is identified by its comment; a macro lives in
    # section-def-macros and is identified by its n attribute.
    ruleElem = ET.fromstring(ruleXml, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    tagName = 'def-macro' if isMacro else 'rule'
    matchAttr = 'n' if isMacro else 'comment'
    targetSection = getSection(root, 'section-def-macros' if isMacro else 'section-rules')

    if mode == 'modify' and targetComment is not None:

        replaced = False

        for i, node in enumerate(list(targetSection)):

            if node.tag == tagName and node.get(matchAttr) == targetComment:

                targetSection.remove(node)
                targetSection.insert(i, ruleElem)
                replaced = True
                break

        if not replaced:
            targetSection.append(ruleElem)
    else:
        targetSection.append(ruleElem)

    tempPath = os.path.join(workDir, 'candidate_transfer.t1x')

    with open(tempPath, 'wb') as fout:

        fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
        fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
        tree.write(fout, encoding='utf-8', xml_declaration=False)

    return tempPath

def validateFile(tempPath: str, compilerExe: Optional[str] = None) -> tuple:
    '''Validate the spliced file. Uses the standard-library parser for a well-formedness check (no third-party dependency) and, when a compiler executable is present, runs
    apertium-preprocess-transfer, which parses against the transfer grammar and is the authoritative structural check. apertium-preprocess-transfer does not need the DTD present (the
    file's DOCTYPE references transfer.dtd but the compiler resolves the grammar itself), so none is written beside the temp file. Returns (ok, errorText).'''

    errors = []

    # Well-formedness via the standard library (expat is non-validating, so this catches malformed XML but not DTD-structure errors; the compiler below covers structure).
    try:
        ET.parse(tempPath)

    except ET.ParseError as e:
        errors.append('XML is not well-formed: ' + str(e))

    # Authoritative structural pass with the bundled Apertium compiler. It exits non-zero only on real errors; it also emits warnings (e.g. "same pattern ... Skipping") to stderr with
    # a zero exit, so gate failure on the return code, not on stderr being non-empty.
    if compilerExe and os.path.isfile(compilerExe):

        result = subprocess.run([compilerExe, tempPath, os.path.join(os.path.dirname(tempPath), 'candidate.t1x.bin')], capture_output=True)
        stderr = result.stderr.decode('utf-8', errors='replace').strip()

        if result.returncode != 0:
            errors.append('apertium-preprocess-transfer failed:')
            errors.append('  ' + stderr)

    return (len(errors) == 0, '\n'.join(errors))

# The authorship-stamp sentences, as whole sentences with a single {when} placeholder for the date/time. Being complete sentences (rather than a verb interpolated into a fixed frame)
# they translate cleanly to languages with different word order or date placement. English defaults; the caller passes localized versions (built with QCoreApplication.translate) so
# AIRules itself stays Qt-free and usable standalone.
DEFAULT_AUTHORSHIP_COMMENTS = {
    'added':         'The AI Assistant added this rule on {when}.',
    'modified':      'The AI Assistant modified this rule on {when}.',
    'addedMacro':    'The AI Assistant added this macro on {when}.',
    'modifiedMacro': 'The AI Assistant modified this macro on {when}.',
}

def markAuthorship(ruleXml: str, mode: str, now: datetime.datetime, authorshipComments: Optional[dict] = None, whenStr: Optional[str] = None, isMacro: bool = False) -> str:
    '''Prepend an XML comment to the <rule> (or def-macro) recording that the AI Assistant added or modified it, and when. Placed as the element's first child so it travels with it and
    shows in the preview. `authorshipComments` maps 'added'/'modified' (and, for macros, 'addedMacro'/'modifiedMacro') to a whole localized sentence containing "{when}"; missing keys fall
    back to English. `whenStr` is the date/time text, already localized to the interface language by the Qt-side caller; when omitted, a plain English date is used so AIRules stays usable
    standalone. Returns the original text unchanged if it can't be parsed (validation will then report the real XML error).'''

    templates = authorshipComments or DEFAULT_AUTHORSHIP_COMMENTS
    key = ('modified' if mode == 'modify' else 'added') + ('Macro' if isMacro else '')
    template = templates.get(key) or DEFAULT_AUTHORSHIP_COMMENTS[key]

    # Prefer the caller's locale-formatted date/time. The standalone fallback is a plain English date like "July 3, 2026 14:42" with a non-zero-padded day (cross-platform).
    # No space padding around the sentence: the house comment style is <!--like this-->, and the padding was showing up as a stray leading space when the comment is displayed.
    when = whenStr or (now.strftime('%B ') + str(now.day) + now.strftime(', %Y %H:%M'))
    text = template.format(when=when)

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))

    try:
        elem = ET.fromstring(ruleXml, parser=parser)

    except ET.ParseError:
        return ruleXml

    # cast() because the stdlib stubs type ET.Comment's return oddly; at runtime it is a normal comment element.
    elem.insert(0, cast(ET.Element, ET.Comment(text)))
    return ET.tostring(elem, encoding='unicode')

def generateValidatedRule(engine: Engine, systemInstruction: str, userContent: str, transferPath: str, mode: str, targetComment: Optional[str], compilerExe: Optional[str] = None, authorshipComments: Optional[dict] = None, whenStr: Optional[str] = None, isMacro: bool = False) -> RuleResult:
    '''The core loop: generate a rule (or, with `isMacro`, a def-macro), splice it into a temp copy, validate, and retry with the errors fed back up to MAX_VALIDATION_ATTEMPTS times.
    Returns the last candidate either way; the caller inspects .valid. `authorshipComments` and `whenStr` are passed to markAuthorship for the localized authorship stamp.'''

    priorErrors = None
    lastRule, lastDefs, lastExpl, lastLang, lastErrors = '', [], '', 'en', ''

    workDir = tempfile.mkdtemp(prefix='airules_')

    # Remove the scratch directory once we're done with it however we leave (success, exhausted attempts, or an exception). The returned RuleResult holds only strings, so nothing here
    # needs to outlive the call - unlike the Open-in-XXE temp file, which the dialog cleans up on close.
    try:

        for attempt in range(1, MAX_VALIDATION_ATTEMPTS + 1):

            lastRule, lastDefs, lastExpl, lastLang = generateRule(engine, systemInstruction, userContent, priorErrors)
            lastRule = markAuthorship(lastRule, mode, datetime.datetime.now(), authorshipComments, whenStr, isMacro)

            tempPath = spliceIntoTemp(transferPath, lastRule, lastDefs, mode, targetComment, workDir, isMacro)
            ok, lastErrors = validateFile(tempPath, compilerExe)

            if ok:
                return RuleResult(lastRule, lastDefs, lastExpl, lastLang, True, '', attempt)

            priorErrors = lastErrors

        return RuleResult(lastRule, lastDefs, lastExpl, lastLang, False, lastErrors, MAX_VALIDATION_ATTEMPTS)

    finally:
        shutil.rmtree(workDir, ignore_errors=True)

def insertBefore(text: str, marker: str, insertion: str) -> str:
    '''Insert `insertion` (plus a newline) immediately before the first occurrence of `marker` in `text`.'''

    idx = text.find(marker)

    if idx == -1:
        raise RuntimeError('Could not find {marker} in the transfer file.'.format(marker=marker))

    return text[:idx] + insertion + '\n' + text[idx:]

def applyRule(transferPath: str, result: RuleResult, mode: str, targetComment: Optional[str], isMacro: bool = False) -> str:
    '''Write the approved rule (or, with `isMacro`, the approved def-macro) into the real transfer file after backing it up.

    Uses surgical text insertion/replacement so the rest of the file is preserved byte-for-byte (XXE re-lays-out the touched rule on next open) rather than reserializing the whole
    tree and reformatting every rule. Returns the backup path.'''

    with open(transferPath, encoding='utf-8') as fin:
        text = fin.read()

    backupPath = transferPath + datetime.datetime.now().strftime('.%Y%m%d_%H%M%S.bak')
    shutil.copyfile(transferPath, backupPath)

    ruleText = result.ruleXml.strip()
    tagName = 'def-macro' if isMacro else 'rule'
    matchAttr = 'n' if isMacro else 'comment'

    # Place the rule/macro itself first, while `text` still matches the file on disk byte-for-byte: the modify path pairs a parse of the on-disk file with raw-text spans, so the spans
    # must be computed before the new definitions below are inserted (an inserted def-macro would otherwise throw the macro spans off against the parse). The new definitions follow.
    if mode == 'modify' and targetComment:

        # Decide which rule/macro to replace with a real XML parse, so the match is robust to XML-escaped characters (&, <, >, quotes) in the identifying attribute and to either quote
        # style - a raw-text regex on comment="X" could silently miss (and then append a duplicate). These elements don't nest and appear only in their own section, so the i-th raw-text
        # span is the i-th element in the parsed tree; we replace that span in place (plain string slice, so backslashes in the rule text aren't treated as regex replacements), keeping the
        # rest of the file byte-for-byte and the element in its original position.
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        elems = ET.parse(transferPath, parser=parser).getroot().findall('.//' + tagName)
        elemIndex = next((i for i, e in enumerate(elems) if e.get(matchAttr) == targetComment), None)

        spans = list(re.finditer(r'<' + tagName + r'\b[\s\S]*?</' + tagName + r'\s*>', text))

        # If the target isn't found, or the raw-text spans don't line up one-to-one with the parsed elements (e.g. a stray "<rule" inside a comment threw the count off), refuse to
        # guess: writing a duplicate or clobbering the wrong element is worse than stopping. The backup is already made and the user can place the rule by hand via Open in XXE.
        if elemIndex is None or len(spans) != len(elems):
            raise RuntimeError('Could not safely locate the {kind} "{comment}" to replace it, so the rule file was left unchanged (a backup was made at {backup}). Use "Open a Temporary Version in XXE" to place the {kind} manually.'.format(kind='macro' if isMacro else 'rule', comment=targetComment, backup=os.path.basename(backupPath)))

        span = spans[elemIndex]
        text = text[:span.start()] + ruleText + text[span.end():]
    else:
        text = insertBefore(text, '</section-def-macros' if isMacro else '</section-rules', ruleText)

    # Insert any new definitions before their section's closing tag.
    for defText in result.newDefs:

        defElem = ET.fromstring(defText)
        sectionClose = '</' + DEF_TAG_TO_SECTION[defElem.tag]
        text = insertBefore(text, sectionClose, defText.strip())

    with open(transferPath, 'w', encoding='utf-8') as fout:
        fout.write(text)

    return backupPath
