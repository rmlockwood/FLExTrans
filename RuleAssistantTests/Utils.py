DATA = {}

def underscores(s):
    return s.replace('.', '_')

def getLemmasForFeature(DB, report, configMap, gramCategory, featureAbbrev):
    return DATA.get(gramCategory, {}).get(featureAbbrev, {}).get('lemma', [])

def getAffixGlossesForFeature(DB, report, configMap, gramCategory, featureAbbrev):
    return DATA.get(gramCategory, {}).get(featureAbbrev, {}).get('affix', [])
