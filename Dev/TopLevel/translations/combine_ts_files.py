import os
import re
from xml.etree import ElementTree as ET

def get_lang_code(filename):
    # Match two-letter language code before .ts at end
    m = re.search(r'_([a-z]{2})\.ts$', filename)
    return m.group(1) if m else None

def main():
    cwd = os.getcwd()
    parent_dir = os.path.basename(os.path.dirname(cwd))  # Get parent folder name
    ts_files = [f for f in os.listdir(cwd) if f.endswith('.ts')]
    lang_files = {}
    for f in ts_files:
        lang = get_lang_code(f)
        if lang:
            lang_files.setdefault(lang, []).append(f)

    for lang, files in lang_files.items():
        contexts = []
        ts_version = None
        for fname in files:
            tree = ET.parse(fname)
            root = tree.getroot()
            if ts_version is None:
                ts_version = root.attrib.get('version', '2.1')
            for context in root.findall('context'):
                contexts.append(context)
        # Build new TS root
        ts_root = ET.Element('TS', version=ts_version)
        for context in contexts:
            ts_root.append(context)
        # Write output file
        out_name = f"{parent_dir}_{lang}.ts"
        ET.ElementTree(ts_root).write(out_name, encoding='utf-8', xml_declaration=True, short_empty_elements=False, method='xml')
        print(f"Wrote {out_name} with {len(contexts)} contexts.")

if __name__ == "__main__":
    main()