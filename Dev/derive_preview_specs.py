#
#   derive_preview_specs.py
#
#   Build tool. Derives the per-language preview label/colour specs used by
#   TransferPreview from the XXE stylesheet(s), so that editing the main
#   transfer.css (or a translated one) is reflected in the in-app preview.
#
#   For English it reads the main XXE stylesheet; for de/es/fr it reads the
#   translated stylesheet under XXEaddon/translations/<lang>/. Each is parsed into
#   a {tag: [labelText, [[attr, attrLabel, colorClass], ...]]} map and written to
#   Dev/Lib/preview_spec_<lang>.json, which TransferPreview loads at render time.
#
#   The spec also carries a "_colors" map (chip class -> hex colour) parsed from the
#   stylesheet's @property-value declarations, so the preview's box colours come
#   from the XXE CSS rather than being hard coded; editing a colour there flows
#   into the derived JSON and from it into the in-app preview.
#
#   Run it whenever the XXE transfer.css files change (the installer runs it too).
#     python Dev/derive_preview_specs.py

import os
import re
import json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XXE = os.path.join(REPO, 'Installer', 'InstallerResources', 'XXEaddon')
OUT_DIR = os.path.join(REPO, 'Dev', 'Lib')

# The XXE stylesheet per UI language. 'en' is the untranslated master.
CSS_FOR_LANG = {
    'en': os.path.join(XXE, 'ApertiumTransferXMLmind', 'css', 'transfer.css'),
    'de': os.path.join(XXE, 'translations', 'de', 'ApertiumTransferXMLmind', 'css', 'transfer.css'),
    'es': os.path.join(XXE, 'translations', 'es', 'ApertiumTransferXMLmind', 'css', 'transfer.css'),
    'fr': os.path.join(XXE, 'translations', 'fr', 'ApertiumTransferXMLmind', 'css', 'transfer.css'),
}

# XXE background-color property-value name -> our transfer_preview.css chip class.
COLOR_CLASS = {
    'def-attr-background-color': 'c-attr',
    'def-cat-background-color': 'c-cat',
    'def-list-background-color': 'c-list',
    'def-macro-background-color': 'c-macro',
    'def-rule-background-color': 'c-rule',
    'def-var-background-color': 'c-var',
    'def-pos-background-color': 'c-pos',
    'def-literal-background-color': 'c-lit',
    'def-literal-tag-background-color': 'c-littag',
    'def-chunk-background-color': 'c-chunk',
}


def stripComments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)


def parseColors(css):
    '''Parse the @property-value colour declarations (e.g. "@property-value def-cat-background-color() #FFB6C1;")
    into a {chipClass: hexColor} map keyed by our transfer_preview.css class names.'''

    colors = {}

    for name, hexColor in re.findall(r'@property-value\s+([\w-]+)\(\)\s+(#[0-9A-Fa-f]{3,8})\s*;', css):
        cls = COLOR_CLASS.get(name)
        if cls:
            colors[cls] = hexColor.upper()

    return colors


def splitArgs(argText):
    '''Split a function's argument list on top-level commas (ignoring commas inside nested parens or quoted strings).'''

    args, depth, quote, cur = [], 0, None, ''

    for ch in argText:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in '"\'':
            quote = ch
            cur += ch
        elif ch == '(':
            depth += 1; cur += ch
        elif ch == ')':
            depth -= 1; cur += ch
        elif ch == ',' and depth == 0:
            args.append(cur.strip()); cur = ''
        else:
            cur += ch

    if cur.strip():
        args.append(cur.strip())

    return args


def tokenizeContent(value):
    '''Turn a CSS `content:` value into an ordered list of tokens: ('str', text) for
    string literals, ('field', attr, colorClass) for text-field(), and ('combo', attr)
    for combo-box(). collapser/icon/label/check-box are ignored.'''

    tokens = []
    i, n = 0, len(value)

    while i < n:
        ch = value[i]

        if ch.isspace():
            i += 1
            continue

        if ch == '"':
            j = value.find('"', i + 1)
            if j == -1:
                break
            tokens.append(('str', value[i + 1:j]))
            i = j + 1
            continue

        m = re.match(r'([\w-]+)\s*\(', value[i:])
        if m:
            name = m.group(1)
            # find the matching close paren for this call
            depth, k = 0, i + m.end() - 1
            while k < n:
                if value[k] == '(':
                    depth += 1
                elif value[k] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            argText = value[i + m.end():k]
            i = k + 1

            if name in ('text-field', 'combo-box'):
                args = splitArgs(argText)
                attr = args[args.index('attribute') + 1] if 'attribute' in args else ''
                if name == 'text-field':
                    color = ''
                    if 'background-color' in args:
                        color = args[args.index('background-color') + 1].rstrip('()')
                    tokens.append(('field', attr, COLOR_CLASS.get(color, 'c-chunk')))
                else:
                    tokens.append(('combo', attr))
            # collapser / icon / label / check-box: no chip, skip
            continue

        i += 1   # stray punctuation

    return tokens


def contentOf(body):
    '''Extract the `content:` value string from a rule body, or '' if none.'''

    m = re.search(r'content\s*:\s*(.*?);', body, flags=re.DOTALL)
    return m.group(1) if m else ''


def readText(path):
    '''Read a CSS file, tolerating the non-UTF-8 (cp1252) encoding of the translated stylesheets.'''

    data = open(path, 'rb').read()

    for enc in ('utf-8', 'cp1252', 'latin-1'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue

    return data.decode('utf-8', errors='replace')


def parseCss(path):
    '''Parse one transfer.css into {tag: [labelText, [[attr, attrLabel, colorClass], ...]]}.'''

    css = stripComments(readText(path))

    before, elemBare, elemVariant = {}, {}, {}

    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):

        selector = selector.strip()

        if selector.startswith('@'):
            continue

        m = re.match(r'^([\w-]+)(:before)?$', selector)
        if m:
            tag, isBefore = m.group(1), bool(m.group(2))
            (before if isBefore else elemBare)[tag] = contentOf(body)
            continue

        # TAG[...] — attribute-qualified element rule (e.g. cat-item[tags]); keep the
        # first as a fallback for tags that have no bare TAG {} block.
        m = re.match(r'^([\w-]+)\[', selector)
        if m:
            elemVariant.setdefault(m.group(1), contentOf(body))

    spec = {}
    tags = set(before) | set(elemBare) | set(elemVariant)

    for tag in tags:

        # :before content comes first, then the element content (bare preferred).
        stream = tokenizeContent(before.get(tag, ''))
        stream += tokenizeContent(elemBare.get(tag) or elemVariant.get(tag) or '')

        labelText, attrs, pending, seenField = '', [], '', False

        for tok in stream:

            if tok[0] == 'str':
                pending += tok[1]
                continue

            # a field or combo
            if not seenField:
                labelText, pending, seenField = pending, '', True
                attrLabel = ''
            else:
                attrLabel, pending = pending, ''

            if tok[0] == 'field':
                attrs.append([tok[1], attrLabel, tok[2]])
            else:
                attrs.append([tok[1], attrLabel, 'c-plain'])

        if not seenField:
            labelText = pending

        spec[tag] = [labelText, attrs]

    # Carry the chip colours along under a key no element tag can collide with.
    spec['_colors'] = parseColors(css)

    return spec


def main():
    for lang, path in CSS_FOR_LANG.items():

        if not os.path.isfile(path):
            print('SKIP %s: %s not found' % (lang, path))
            continue

        spec = parseCss(path)
        outPath = os.path.join(OUT_DIR, 'preview_spec_%s.json' % lang)
        json.dump(spec, open(outPath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
        print('wrote %s (%d elements)' % (outPath, len(spec)))


if __name__ == '__main__':
    main()
