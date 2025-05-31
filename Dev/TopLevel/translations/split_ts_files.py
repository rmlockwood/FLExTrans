import os
import re

def get_lang_code(filename):
    m = re.search(r'_([a-z]{2})\.ts$', filename)
    return m.group(1) if m else None

def get_ts_version(ts_text):
    m = re.search(r'<TS[^>]*version="([^"]+)"', ts_text)
    return m.group(1) if m else '2.1'

def extract_contexts(ts_text):
    # Find all <context>...</context> blocks, including newlines and inner tags
    return re.findall(r'(<context>.*?</context>)', ts_text, re.DOTALL)

def get_context_name(context_text):
    m = re.search(r'<name>(.*?)</name>', context_text, re.DOTALL)
    return m.group(1).strip() if m else None

def main():
    cwd = os.getcwd()
    parent_dir = os.path.basename(os.path.dirname(cwd))
    ts_files = [f for f in os.listdir(cwd) if f.startswith(parent_dir + "_") and f.endswith('.ts')]
    if not ts_files:
        print(f"No .ts file found starting with '{parent_dir}_' in {cwd}")
        return
    for ts_file in ts_files:
        lang = get_lang_code(ts_file)
        if not lang:
            print(f"Could not determine language code for {ts_file}")
            continue
        with open(ts_file, encoding='utf-8') as fin:
            text = fin.read()
        ts_version = get_ts_version(text)
        contexts = extract_contexts(text)
        for context in contexts:
            context_name = get_context_name(context)
            if not context_name:
                print("Skipping context with no <name> element.")
                continue
            out_name = f"{context_name}_{lang}.ts"
            with open(out_name, 'w', encoding='utf-8') as fout:
                fout.write('<?xml version="1.0" encoding="utf-8"?>\n')
                fout.write(f'<!DOCTYPE TS>\n<TS version="{ts_version}">\n')
                fout.write(context + '\n')
                fout.write('</TS>\n')
            print(f"Wrote {out_name}")

if __name__ == "__main__":
    main()