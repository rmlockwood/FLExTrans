#
#   AIRules
#
#   Ron Lockwood
#   SIL International
#   7/2/26
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
from typing import Optional
import xml.etree.ElementTree as ET

# Generation settings. The provider and model are chosen from config (see getProvider / buildEngine); these limits are provider-independent.
MAX_TOKENS = 16000
MAX_VALIDATION_ATTEMPTS = 3
DEFAULT_PROVIDER = 'anthropic'

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
_RULE_XML_DESC = 'Exactly one <rule comment="...">...</rule> element. No wrapper, no DOCTYPE.'
_NEW_DEFS_DESC = 'Each string is one new <def-cat>/<def-attr>/<def-var>/<def-list>/<def-macro> element the rule needs and that does not already exist. Empty list if none.'
_EXPLANATION_DESC = 'One or two sentences describing what the rule does. Note here if the rule must be ordered before a more general rule.'

# Gemini structured-output schema (response_mime_type=application/json + response_schema).
RULE_SCHEMA = {
    'type': 'object',
    'properties': {
        'rule_xml': {'type': 'string', 'description': _RULE_XML_DESC},
        'new_defs': {'type': 'array', 'items': {'type': 'string'}, 'description': _NEW_DEFS_DESC},
        'explanation': {'type': 'string', 'description': _EXPLANATION_DESC},
    },
    'required': ['rule_xml', 'new_defs', 'explanation'],
    'propertyOrdering': ['rule_xml', 'new_defs', 'explanation'],
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
        },
        'required': ['rule_xml', 'new_defs', 'explanation'],
    },
}

@dataclasses.dataclass
class RuleResult:
    '''The outcome of a generation attempt.'''

    ruleXml: str
    newDefs: list[str]
    explanation: str
    valid: bool
    errors: str
    attempts: int

# ---------------------------------------------------------------------------
# Provider layer. Each provider knows how to build its SDK client and how to turn a system instruction + user prompt into (ruleXml, newDefs, explanation). To add a provider,
# implement makeClient() and generate() and register it in PROVIDERS.
# ---------------------------------------------------------------------------

class AnthropicProvider:
    '''Anthropic Claude (the default).'''

    name = 'anthropic'
    displayName = 'Anthropic Claude'
    defaultModel = 'claude-opus-4-8'
    envVars = ('ANTHROPIC_API_KEY',)
    keyUrl = 'https://console.anthropic.com/settings/keys'

    def makeClient(self, apiKey: str):

        import anthropic

        return anthropic.Anthropic(api_key=apiKey)

    def generate(self, client, model: str, systemInstruction: str, userContent: str) -> tuple:

        import anthropic

        try:
            response = client.messages.create(
                model=model, max_tokens=MAX_TOKENS, thinking={'type': 'adaptive'}, system=[{'type': 'text', 'text': systemInstruction, 'cache_control': {'type': 'ephemeral'}}], tools=[SUBMIT_RULE_TOOL],
                tool_choice={'type': 'tool', 'name': 'submit_rule'}, messages=[{'role': 'user', 'content': userContent}], )

        except anthropic.RateLimitError as err:

            retryAfter = None
            try:
                retryAfter = float(err.response.headers.get('retry-after'))
            except (AttributeError, TypeError, ValueError):
                pass

            raise RateLimitError(self.displayName, retryAfter)

        if response.stop_reason == 'refusal':
            raise RuntimeError('The model declined this request (stop_reason=refusal).')

        for block in response.content:

            if block.type == 'tool_use' and block.name == 'submit_rule':
                data = block.input
                return data['rule_xml'], data.get('new_defs', []), data.get('explanation', '')

        raise RuntimeError('The model did not return a submit_rule tool call.')

class GeminiProvider:
    '''Google Gemini. Default is gemini-2.5-flash, which is available on the free tier; gemini-2.5-pro requires a billing-enabled (paid) key and returns a 429 with "limit: 0" on the
    free tier. Override with the AIRulesModel setting.'''

    name = 'gemini'
    displayName = 'Google Gemini'
    defaultModel = 'gemini-2.5-flash'
    envVars = ('GEMINI_API_KEY', 'GOOGLE_API_KEY')
    keyUrl = 'https://aistudio.google.com/apikey'

    def makeClient(self, apiKey: str):

        from google import genai

        return genai.Client(api_key=apiKey)

    def generate(self, client, model: str, systemInstruction: str, userContent: str) -> tuple:

        import json

        from google.genai import types, errors

        try:
            response = client.models.generate_content(
                model=model, contents=userContent, config=types.GenerateContentConfig(
                    system_instruction=systemInstruction, max_output_tokens=MAX_TOKENS, response_mime_type='application/json', response_schema=RULE_SCHEMA, ), )

        except errors.APIError as err:

            if getattr(err, 'code', None) == 429:
                raise RateLimitError(self.displayName, parseRetryAfter(str(err)))

            raise

        payload = getattr(response, 'text', None)

        if not payload:
            feedback = getattr(response, 'prompt_feedback', None)
            raise RuntimeError('The model returned no rule. {feedback}'.format(feedback=feedback or '(response was empty or blocked)'))

        data = json.loads(payload)
        return data['rule_xml'], data.get('new_defs', []), data.get('explanation', '')

# Registry of available providers, keyed by the config value.
PROVIDERS = {
    AnthropicProvider.name: AnthropicProvider(), GeminiProvider.name: GeminiProvider(), }

def getProvider(name: Optional[str] = None):
    '''Return the provider for `name` (case-insensitive), falling back to the default when the name is missing or unknown.'''

    return PROVIDERS.get((name or DEFAULT_PROVIDER).strip().lower(), PROVIDERS[DEFAULT_PROVIDER])

def resolveApiKey(provider, configApiKey: Optional[str] = None) -> Optional[str]:
    '''Resolve the API key for `provider`: the provider's env var(s) win (a machine-wide key overrides a stale config value), then the config setting, then None so the caller can
    prompt the user (BYOK).'''

    for var in provider.envVars:

        value = os.environ.get(var)
        if value:
            return value

    if configApiKey:
        return configApiKey

    return None

class Engine:
    '''A provider + its client + the model to use. This is what flows through the generation calls, so the rest of the module is provider-agnostic.'''

    def __init__(self, provider, client, model: str):

        self.provider = provider
        self.client = client
        self.model = model

    def generate(self, systemInstruction: str, userContent: str) -> tuple:

        return self.provider.generate(self.client, self.model, systemInstruction, userContent)

def buildEngine(providerName: Optional[str], apiKey: str, model: Optional[str] = None) -> Engine:
    '''Construct the Engine for the configured provider. `model` overrides the provider default when given (config setting). SDKs are imported lazily inside makeClient, so only the
    selected provider's SDK needs to be installed.'''

    provider = getProvider(providerName)
    client = provider.makeClient(apiKey)
    return Engine(provider, client, model or provider.defaultModel)

def buildSystemInstruction(conventionsText: str, sampleRulesText: str) -> str:
    '''Build the system instruction: the house conventions plus a few real example rules from the project. The transfer.dtd is intentionally NOT included - the model already knows the
    Apertium transfer format, so the DTD is ~5k low-value tokens, and the validation-retry loop (well-formedness + apertium-preprocess-transfer) is the authoritative structural check.
    This prefix is identical across requests, so it caches well (Anthropic cache_control / Gemini implicit caching).'''

    return (conventionsText
            + '\n\nExample rules from this project, for style reference:\n\n' + sampleRulesText)

def extractExistingDefs(transferPath: str) -> dict:
    '''Read the transfer file and collect the names of definitions that already exist (so the model reuses them) plus the value sets of each attribute and the existing rule names.
    Returns a dict with both the raw data and a text summary suitable for dropping into the prompt.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(transferPath, parser=parser).getroot()

    cats = [c.get('n') for c in root.findall('.//def-cat')]
    variables = [v.get('n') for v in root.findall('.//def-var')]
    lists = [l.get('n') for l in root.findall('.//def-list')]
    macros = [m.get('n') for m in root.findall('.//def-macro')]

    # For attributes, gather the tag values too so the model knows which tags are legal for each attribute.
    attrs = {}
    for a in root.findall('.//def-attr'):
        attrs[a.get('n')] = sorted(i.get('tags') for i in a.findall('./attr-item'))

    ruleNames = [r.get('comment') for r in root.findall('.//rule')]

    # Build a compact text summary for the prompt.
    lines = []
    lines.append('Existing categories (def-cat): ' + ', '.join(cats))
    lines.append('')
    lines.append('Existing attributes (def-attr) and their legal tag values:')

    for name in sorted(attrs):
        lines.append('  {name}: {values}'.format(name=name, values=', '.join(attrs[name])))

    lines.append('')
    lines.append('Existing variables (def-var): ' + (', '.join(variables) or '(none)'))
    lines.append('Existing lists (def-list): ' + (', '.join(lists) or '(none)'))
    lines.append('Existing macros (def-macro): ' + (', '.join(macros) or '(none)'))
    lines.append('')
    lines.append('Existing rule names (comment): ' + ', '.join(ruleNames))

    return {
        'cats': cats, 'attrs': attrs, 'variables': variables, 'lists': lists, 'macros': macros, 'ruleNames': ruleNames, 'summaryText': '\n'.join(lines), }

def getRuleXmlByComment(transferPath: str, comment: str) -> Optional[str]:
    '''Return the XML text of the rule whose comment matches, or None.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(transferPath, parser=parser).getroot()

    for rule in root.findall('.//rule'):

        if rule.get('comment') == comment:
            return ET.tostring(rule, encoding='unicode')

    return None

def buildUserContent(mode: str, description: str, defsSummary: str, projectData: str, currentRuleXml: Optional[str]) -> str:
    '''Assemble the volatile per-request part of the prompt: the project's real categories/features, the existing-definition summary, the current rule (when modifying), and the
    user's request.'''

    parts = []
    parts.append('PROJECT DATA (real categories, features, feature values, and affixes from the FLEx projects):')
    parts.append(projectData)
    parts.append('')
    parts.append('DEFINITIONS ALREADY IN THE TRANSFER FILE (reuse these; only create new ones when necessary):')
    parts.append(defsSummary)
    parts.append('')

    if mode == 'modify' and currentRuleXml:
        parts.append('MODE: modify the following existing rule. Keep its comment unless asked to rename it.')
        parts.append('CURRENT RULE:')
        parts.append(currentRuleXml)
    else:
        parts.append('MODE: create a new rule.')

    parts.append('')
    parts.append('USER REQUEST:')
    parts.append(description)

    return '\n'.join(parts)

def generateRule(engine: Engine, systemInstruction: str, userContent: str, priorErrors: Optional[str] = None) -> tuple:
    '''Make one generation call through the engine and return (ruleXml, newDefs, explanation). On a validation retry the prior errors are appended so the model can fix them.'''

    text = userContent

    if priorErrors:
        text += ('\n\nYour previous rule failed validation with these errors. Fix them and resubmit:\n'
                 + priorErrors)

    return engine.generate(systemInstruction, text)

def getSection(root: ET.Element, sectionName: str) -> ET.Element:
    '''Return a section element, matching CreateApertiumRules' section ordering assumption. The sample/real files already contain every section.'''

    elem = root.find(sectionName)

    if elem is None:
        elem = ET.SubElement(root, sectionName)

    return elem

def spliceIntoTemp(transferPath: str, ruleXml: str, newDefs: list[str], mode: str, targetComment: Optional[str], workDir: str) -> str:
    '''Insert the candidate rule and any new definitions into a copy of the transfer file, write it to workDir alongside a copy of the DTD, and return the temp file path. For "modify"
    the rule with targetComment is replaced; for "create" the rule is appended to section-rules (specific-before-general placement is a later refinement).'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(transferPath, parser=parser)
    root = tree.getroot()

    # Add any new definitions to their proper sections.
    for defText in newDefs:

        defElem = ET.fromstring(defText)
        section = getSection(root, DEF_TAG_TO_SECTION.get(defElem.tag))
        section.append(defElem)

    # Comment-preserving parse so the AI-authorship comment survives into the temp file.
    ruleElem = ET.fromstring(ruleXml, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    ruleSection = getSection(root, 'section-rules')

    if mode == 'modify' and targetComment is not None:

        replaced = False

        for i, rule in enumerate(list(ruleSection)):

            if rule.tag == 'rule' and rule.get('comment') == targetComment:

                ruleSection.remove(rule)
                ruleSection.insert(i, ruleElem)
                replaced = True
                break

        if not replaced:
            ruleSection.append(ruleElem)
    else:
        ruleSection.append(ruleElem)

    tempPath = os.path.join(workDir, 'candidate_transfer.t1x')

    with open(tempPath, 'wb') as fout:

        fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
        fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
        tree.write(fout, encoding='utf-8', xml_declaration=False)

    return tempPath

def validateFile(tempPath: str, dtdPath: str, compilerExe: Optional[str] = None) -> tuple:
    '''Validate the spliced file. Uses the standard-library parser for a well-formedness check (no third-party dependency) and, when a compiler executable is present, runs
    apertium-preprocess-transfer, which parses against the transfer grammar and is the authoritative structural check. `dtdPath` is unused here but the caller keeps a copy of the DTD
    beside the temp file for the compiler's relative lookup. Returns (ok, errorText).'''

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

def markAuthorship(ruleXml: str, mode: str, now) -> str:
    '''Prepend an XML comment to the <rule> recording that the AI Assistant added or modified it, and when. Placed as the rule's first child so it travels with the rule and shows in
    the preview. Returns the original text unchanged if it can't be parsed (validation will then report the real XML error).'''

    verb = 'modified' if mode == 'modify' else 'added'
    # Format like "July 3, 2026 14:42" without a zero-padded day (cross-platform).
    when = now.strftime('%B ') + str(now.day) + now.strftime(', %Y %H:%M')
    text = ' The AI Assistant {verb} this rule on {when}. '.format(verb=verb, when=when)

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))

    try:
        elem = ET.fromstring(ruleXml, parser=parser)

    except ET.ParseError:
        return ruleXml

    elem.insert(0, ET.Comment(text))
    return ET.tostring(elem, encoding='unicode')

def generateValidatedRule(engine: Engine, systemInstruction: str, userContent: str, transferPath: str, dtdPath: str, mode: str, targetComment: Optional[str], compilerExe: Optional[str] = None) -> RuleResult:
    '''The core loop: generate a rule, splice it into a temp copy, validate, and retry with the errors fed back up to MAX_VALIDATION_ATTEMPTS times. Returns the last candidate either
    way; the caller inspects .valid.'''

    priorErrors = None
    lastRule, lastDefs, lastExpl, lastErrors = '', [], '', ''

    workDir = tempfile.mkdtemp(prefix='airules_')
    
    # apertium-preprocess-transfer resolves the DTD relative to the file.
    shutil.copyfile(dtdPath, os.path.join(workDir, 'transfer.dtd'))

    for attempt in range(1, MAX_VALIDATION_ATTEMPTS + 1):

        lastRule, lastDefs, lastExpl = generateRule(engine, systemInstruction, userContent, priorErrors)
        lastRule = markAuthorship(lastRule, mode, datetime.datetime.now())

        tempPath = spliceIntoTemp(transferPath, lastRule, lastDefs, mode, targetComment, workDir)
        ok, lastErrors = validateFile(tempPath, os.path.join(workDir, 'transfer.dtd'), compilerExe)

        if ok:
            return RuleResult(lastRule, lastDefs, lastExpl, True, '', attempt)

        priorErrors = lastErrors

    return RuleResult(lastRule, lastDefs, lastExpl, False, lastErrors, MAX_VALIDATION_ATTEMPTS)

def insertBefore(text: str, marker: str, insertion: str) -> str:
    '''Insert `insertion` (plus a newline) immediately before the first occurrence of `marker` in `text`.'''

    idx = text.find(marker)

    if idx == -1:
        raise RuntimeError('Could not find {marker} in the transfer file.'.format(marker=marker))

    return text[:idx] + insertion + '\n' + text[idx:]

def applyRule(transferPath: str, result: RuleResult, mode: str, targetComment: Optional[str]) -> str:
    '''Write the approved rule into the real transfer file after backing it up.

    Uses surgical text insertion/replacement so the rest of the file is preserved byte-for-byte (XXE re-lays-out the touched rule on next open) rather than reserializing the whole
    tree and reformatting every rule. Returns the backup path.'''

    with open(transferPath, encoding='utf-8') as fin:
        text = fin.read()

    backupPath = transferPath + datetime.datetime.now().strftime('.%Y%m%d_%H%M%S.bak')
    shutil.copyfile(transferPath, backupPath)

    # Insert any new definitions before their section's closing tag.
    for defText in result.newDefs:

        defElem = ET.fromstring(defText)
        sectionClose = '</' + DEF_TAG_TO_SECTION[defElem.tag]
        text = insertBefore(text, sectionClose, defText.strip())

    ruleText = result.ruleXml.strip()

    if mode == 'modify' and targetComment:

        # Replace the whole <rule …comment="X"…>…</rule> span in place, keeping its position (so specific-before-general ordering is preserved). Rules don't nest, so the non-greedy
        # match stops at this rule's own close tag.
        pattern = re.compile(r'<rule\b[^>]*?comment="' + re.escape(targetComment) + r'"[\s\S]*?</rule\s*>')
        text, count = pattern.subn(lambda m: ruleText, text, count=1)

        if count == 0:
            text = insertBefore(text, '</section-rules', ruleText)
    else:
        text = insertBefore(text, '</section-rules', ruleText)

    with open(transferPath, 'w', encoding='utf-8') as fout:
        fout.write(text)

    return backupPath
