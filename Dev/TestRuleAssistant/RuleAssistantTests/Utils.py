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

# Test stub: the real Utils.shortenPathForDisplay trims a path for user messages; the tests only need it to return the path unchanged.
def shortenPathForDisplay(path):
    return path

# Test stub mirroring Utils.makeUniqueName: return title unchanged if it's free, otherwise append ' - Copy', then ' - Copy (2)', ' - Copy (3)', ... until unused. No translation in the stub.
def makeUniqueName(title, existingNames):
    if title in existingNames:
        title += ' - Copy'
        if title in existingNames:
            i = 2
            while True:
                tryName = title + ' (' + str(i) + ')'
                if tryName not in existingNames:
                    title = tryName
                    break
                i += 1
    return title
