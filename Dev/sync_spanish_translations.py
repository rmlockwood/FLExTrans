"""Sync Spanish translations from root .ts files into their per-module translation files.

This script reads the three root Spanish translation files:
- Dev/Lib_es.ts
- Dev/Modules_es.ts
- Dev/Windows_es.ts

For each message in a root file, it extracts the source string, the translated string,
and the first location filename. It maps the root file to the corresponding
translations subfolder and looks for the matching Spanish file by the location
module name.

If the same source string exists in the module translation file and the translation
text differs, the target translation is updated to match the root file.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_FILE_NAMES = ["Lib_es.ts", "Modules_es.ts", "Windows_es.ts"]
ROOT_DIR = Path(__file__).resolve().parents[1] / "Dev"


def parse_ts_file(path: Path) -> ET.ElementTree:
    parser = ET.XMLParser(encoding="utf-8")
    return ET.parse(path, parser=parser)


def get_root_messages(root_tree: ET.ElementTree) -> List[ET.Element]:
    root = root_tree.getroot()
    return list(root.findall("./context/message"))


def get_first_location_filename(message: ET.Element) -> Optional[str]:
    location = message.find("location")
    if location is None:
        return None
    return location.get("filename")


def find_target_translation_file(root_file: Path, location_filename: str) -> Optional[Path]:
    basename = Path(location_filename).name
    stem = Path(basename).stem

    if root_file.name == "Lib_es.ts":
        candidate_dir = ROOT_DIR / "Lib" / "translations"
    elif root_file.name == "Modules_es.ts":
        candidate_dir = ROOT_DIR / "Modules" / "translations"
    elif root_file.name == "Windows_es.ts":
        candidate_dir = ROOT_DIR / "Windows" / "translations"
    else:
        return None

    candidate_path = candidate_dir / f"{stem}_es.ts"
    if candidate_path.exists():
        return candidate_path

    # Fallback: search the candidate folder for matching stem.
    for path in candidate_dir.glob(f"{stem}_*.ts"):
        if path.name.endswith("_es.ts"):
            return path

    return None


def get_text(element: ET.Element, tag: str) -> str:
    node = element.find(tag)
    if node is None:
        return ""
    return node.text or ""


def update_translations_in_target(
    target_path: Path,
    source_text: str,
    new_translation: str,
) -> Tuple[bool, bool]:
    tree = parse_ts_file(target_path)
    root = tree.getroot()
    updated = False
    found = False

    for message in root.findall("./context/message"):
        source_node = message.find("source")
        if source_node is None:
            continue

        if source_node.text != source_text:
            continue

        found = True
        translation_node = message.find("translation")
        if translation_node is None:
            translation_node = ET.SubElement(message, "translation")

        current_translation = translation_node.text or ""
        if current_translation != new_translation:
            translation_node.text = new_translation
            translation_node.attrib.pop("type", None)
            updated = True
            break

    if updated:
        tree.write(target_path, encoding="utf-8", xml_declaration=True)

    return found, updated


def sync_root_file(root_file: Path) -> Dict[str, int]:
    stats = {"messages": 0, "missing_location": 0, "missing_target_file": 0, "missing_source": 0, "updated": 0}
    tree = parse_ts_file(root_file)

    for message in get_root_messages(tree):
        stats["messages"] += 1
        source_text = get_text(message, "source")
        translation_text = get_text(message, "translation")
        location_filename = get_first_location_filename(message)

        if not location_filename:
            stats["missing_location"] += 1
            continue

        target_file = find_target_translation_file(root_file, location_filename)
        if target_file is None:
            stats["missing_target_file"] += 1
            continue

        found, updated = update_translations_in_target(target_file, source_text, translation_text)
        if not found:
            stats["missing_source"] += 1
            continue
        if updated:
            stats["updated"] += 1

    return stats


def main() -> None:
    root_files = [ROOT_DIR / name for name in ROOT_FILE_NAMES]
    total_stats = {"messages": 0, "missing_location": 0, "missing_target_file": 0, "missing_source": 0, "updated": 0}

    for root_file in root_files:
        if not root_file.exists():
            print(f"Root file not found: {root_file}")
            continue

        print(f"Processing {root_file}...")
        stats = sync_root_file(root_file)
        print(
            f"  messages={stats['messages']}, updated={stats['updated']},"
            f" missing_location={stats['missing_location']},"
            f" missing_target_file={stats['missing_target_file']},"
            f" missing_source={stats['missing_source']}"
        )

        for key in total_stats:
            total_stats[key] += stats[key]

    print("\nSummary:")
    print(f"  total messages={total_stats['messages']}")
    print(f"  total updated={total_stats['updated']}")
    print(f"  total missing_location={total_stats['missing_location']}")
    print(f"  total missing_target_file={total_stats['missing_target_file']}")
    print(f"  total missing_source={total_stats['missing_source']}")


if __name__ == "__main__":
    main()
