import os
import re
from xml.etree import ElementTree as ET

def get_lang_code(filename):
    m = re.search(r'_([a-z]{2})\.ts$', filename)
    return m.group(1) if m else None

def main():
    cwd = os.getcwd()
    parent_dir = os.path.basename(os.path.dirname(cwd))
    # Find the .ts file named after the parent folder
    ts_files = [f for f in os.listdir(cwd) if f.startswith(parent_dir + "_") and f.endswith('.ts')]
    if not ts_files:
        print(f"No .ts file found starting with '{parent_dir}_' in {cwd}")
        return
    for ts_file in ts_files:
        lang = get_lang_code(ts_file)
        if not lang:
            print(f"Could not determine language code for {ts_file}")
            continue
        tree = ET.parse(ts_file)
        root = tree.getroot()
        ts_version = root.attrib.get('version', '2.1')
        for context in root.findall('context'):
            name_elem = context.find('name')
            if name_elem is None or not name_elem.text:
                print("Skipping context with no <name> element.")
                continue
            context_name = name_elem.text
            ts_root = ET.Element('TS', version=ts_version)
            ts_root.append(context)
            out_name = f"{context_name}_{lang}.ts"
            ET.ElementTree(ts_root).write(out_name, encoding='utf-8', xml_declaration=True)
            print(f"Wrote {out_name}")

if __name__ == "__main__":
    main()