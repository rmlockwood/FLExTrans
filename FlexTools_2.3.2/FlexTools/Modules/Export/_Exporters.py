#
#   Defines Export_Publication(), which exports one set of headwords
#   from a publication.
#

#----------------------------------------------------------------
def Export_Publication(project, report, pubName):
    report.Info(f"Exporting all headwords in '{pubName}'...")
    
    
    headwordsFile = "{}_{}.txt".format(pubName,
                                       project.ProjectName())

    pubType = project.PublicationType(pubName)
    if not pubType:
        report.Error(f"{pubName} isn't in the list of publications for this project:")
        report.Info("   " + ", ".join(project.GetPublications()))
        return

    headwords = []
    for e in project.LexiconAllEntries():       
        if pubType in e.PublishIn:
            headword = project.LexiconGetHeadword(e)
            headwords.append(headword)

    with open(headwordsFile, mode="w", encoding="utf-8") as output:
        for headword in sorted(headwords, key=lambda s: s.lower()):
            output.write(headword + '\n')

    report.Info("Exported {0} headwords to file {1}".format(
                len(headwords), headwordsFile),
                report.FileURL(headwordsFile))

