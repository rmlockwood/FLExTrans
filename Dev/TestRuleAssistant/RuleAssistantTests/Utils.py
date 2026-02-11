DATA = {}

def underscores(s):
    return s.replace('.', '_')

def getLemmasForFeature(DB, report, configMap, gramCategory, featureAbbrev):
    return DATA.get(gramCategory, {}).get(featureAbbrev, {}).get(DB+'_lemma', [])

def getAffixGlossesForFeature(DB, report, configMap, gramCategory, featureAbbrev):
    if isinstance(gramCategory, set):
        ret = []
        for k in sorted(gramCategory):
            ret += getAffixGlossesForFeature(DB, report, configMap, k, featureAbbrev)
        return ret
    return DATA.get(gramCategory, {}).get(featureAbbrev, {}).get(DB+'_affix', [])

def getPossibleFeatureValues(DB, featureName):
    return DATA.get(None, {}).get(featureName, {}).get(DB+'_features', [])

def getCategoryHierarchy(DB):
    return {}
