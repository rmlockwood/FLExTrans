#
#   RuleGenPropsToTS
#
#   Ron Lockwood
#   SIL International
#   6/15/26
#
#   Generate the Qt translation source files (RuleAssistantLib_<lang>.ts) for the
#   Rule Assistant from the Java-style RuleGen_<lang>.properties files.
#
#   The Rule Assistant UI strings originate from the Java ftrulegen project
#   (https://github.com/AndyBlack/ftrulegen) as RuleGen_{en,de,es,fr}.properties.
#   The Python/PyQt6 port looks those strings up with
#   QCoreApplication.translate("RuleAssistantLib", <english-text>), so this script
#   builds one .ts per language whose <source> is the English value and whose
#   <translation> is the localized value, keyed by the matching property name.
#
#   Run from the Dev folder:  python Modules\RuleGenPropsToTS.py
#

import os
from pathlib import Path

CONTEXT = "RuleAssistantLib"
LANGS = ["de", "es", "fr"]

DEV_DIR = Path(__file__).resolve().parent.parent          # ...\Dev
PROPS_DIR = DEV_DIR                                        # RuleGen_*.properties live in Dev
TRANSL_DIR = DEV_DIR / "Modules" / "translations"


def read_props(path: Path) -> "dict[str, str]":
    """Read a .properties file into an ordered key->value dict.

    Java escape sequences that matter for these files (\\n, \\t) are converted to
    real characters so the UI shows line breaks rather than a literal backslash-n.
    """
    result = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.replace("\\n", "\n").replace("\\t", "\t")
            result[key] = value
    return result


def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_ts(lang: str, en: "dict[str, str]", loc: "dict[str, str]") -> str:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!DOCTYPE TS>",
        f'<TS version="2.1" language="{lang}" sourcelanguage="en">',
        "<context>",
        f"    <name>{CONTEXT}</name>",
    ]
    seen = set()
    for key, source in en.items():
        if source in seen:
            continue                       # duplicate English text -> one Qt message
        seen.add(source)
        translation = loc.get(key, source)
        lines.append("    <message>")
        lines.append(f"        <source>{xml_escape(source)}</source>")
        lines.append(f"        <translation>{xml_escape(translation)}</translation>")
        lines.append("    </message>")
    lines.append("</context>")
    lines.append("</TS>")
    return "\n".join(lines) + "\n"


def main() -> None:
    en = read_props(PROPS_DIR / "RuleGen_en.properties")
    for lang in LANGS:
        loc = read_props(PROPS_DIR / f"RuleGen_{lang}.properties")
        ts = build_ts(lang, en, loc)
        out = TRANSL_DIR / f"{CONTEXT}_{lang}.ts"
        out.write_text(ts, encoding="utf-8")
        print(f"wrote {out} ({ts.count('<message>')} messages)")

    # Match the project convention (see Modules\local_pylup.bat): the base .ts is a
    # copy of the French one.
    base = TRANSL_DIR / f"{CONTEXT}.ts"
    base.write_text((TRANSL_DIR / f"{CONTEXT}_fr.ts").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {base}")


if __name__ == "__main__":
    main()
