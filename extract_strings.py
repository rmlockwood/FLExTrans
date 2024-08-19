#!/usr/bin/env python3

import glob
from xml.etree import ElementTree as ET

for fname in glob.glob('*.ui'):
    print(fname)
    # TODO: it might at some point be useful to provide the class name
    # as the context key, and also have this script output data
    # in a format that we can directly upload to CrowdIn
    strings = set()
    tree = ET.parse(fname).getroot()
    for node in tree.findall('.//property/string/..'):
        if node.attrib['name'] in ['html', 'styleSheet']:
            continue
        if node[0].text:
            strings.add(node[0].text)
    print('\n'.join(sorted(strings)))
    print('')
