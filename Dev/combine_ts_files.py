import os
import re

def get_lang_code(filename):
    m = re.search(r'_([a-z]{2})\.ts$', filename)
    return m.group(1) if m else None

def extract_contexts(ts_text):
    # Find all <context>...</context> blocks, including newlines and inner tags
    return re.findall(r'(<context>.*?</context>)', ts_text, re.DOTALL)

def get_ts_version(ts_text):
    m = re.search(r'<TS[^>]*version="([^"]+)"', ts_text)
    return m.group(1) if m else '2.1'

def main():
    cwd = os.getcwd()
    parent_dir = os.path.basename(os.path.dirname(cwd))
    ts_files = [f for f in os.listdir(cwd) if f.endswith('.ts')]
    # Ignore any ts file named after the parent folder (e.g., ParentDir_xx.ts)
    ts_files = [
        f for f in ts_files
        if not any(f == f"{parent_dir}_{lang}.ts" for lang in [get_lang_code(f)] if lang)
    ]
    lang_files = {}
    for f in ts_files:
        lang = get_lang_code(f)
        if lang:
            lang_files.setdefault(lang, []).append(f)

    for lang, files in lang_files.items():
        all_contexts = []
        ts_version = None
        for fname in files:
            with open(fname, encoding='utf-8') as fin:
                text = fin.read()
            if ts_version is None:
                ts_version = get_ts_version(text)
            all_contexts.extend(extract_contexts(text))
        # Compose output
        out_name = f"{parent_dir}_{lang}.ts"
        with open(out_name, 'w', encoding='utf-8') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fout.write(f'<!DOCTYPE TS>\n<TS version="{ts_version}">\n')
            for ctx in all_contexts:
                fout.write(ctx + '\n')
            fout.write('</TS>\n')
        print(f"Wrote {out_name} with {len(all_contexts)} contexts.")

if __name__ == "__main__":
    main()