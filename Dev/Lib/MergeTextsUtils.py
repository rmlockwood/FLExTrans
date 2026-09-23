#
#   MergeTextsUtils
#
#   Ron Lockwood
#   SIL International
#   9/9/26
#
#   Version 3.17.1 - 9/11/26 - Ron Lockwood
#    Fixes #1561. Report chapter coverage only when every selected text has a chapter.
#
#   Version 3.17 - 9/9/26 - Ron Lockwood
#    Initial version.
#
#   OVERVIEW (AI generated, then edited)
#
#   The name arithmetic behind the Merge Texts module: given the list of text names in a FLEx project, work out which of them look like chapters of the same book, what order they go in, and what the
#   merged text should be called. It is kept in its own file, with no Qt and no FLEx imports, for one reason - this is the only part of merging that can be tested without a FLEx project, and
#   Dev/unit_tests/test_mergeTextGrouping.py does exactly that. Everything that touches the database lives in Dev/Modules/MergeTexts.py instead.
#
#   THE CHAPTER TOKEN
#
#   A Bible text imported from Paratext is named "<book> <chapter>", e.g. "Matthew 01", and a text covering more than one chapter is named with a span, e.g. "Matthew 03-04". CHAPTER_TOKEN_RE picks
#   that trailing token apart. Two details in it are deliberate and easy to break. First, the base is non-greedy (.*? rather than .*), so the EARLIEST separator-then-digits split wins. That is what
#   keeps a span whole: on "Matthew 03-04" the lazy base stops at "Matthew" and leaves "-04" for chapTo, whereas a greedy base would stretch to "Matthew 03" and read the name as chapter 4 of a
#   phantom book called "Matthew 03". Note that this is NOT what protects a book whose own name starts with a number - "1 Kings 05" parses as "1 Kings" chapter 5 either way, because the separator
#   has to be followed by digits and "Kings" is not. Second, chapter numbers are capped at three digits, which is what keeps a text called "Field notes 2024" from being read as chapter 202 of a
#   book called "Field notes 2" - a four digit run matches nothing at all and the name is simply reported as having no chapter.
#
#   The separator may be a space, an underscore or a hyphen, so "MAT_01" parses too, and a trailing " - Copy" or " - Copy (2)" is recognised and kept aside rather than defeating the match. That
#   suffix is what Utils.makeUniqueName appends when a text of the same name already exists, so it turns up in real projects often. This is the same shape as ChapterSelection.bookChapterPattern but
#   deliberately not that pattern: that one requires exactly two digits because Paratext always zero pads, and ExportFlexToParatext and ChapterSelection both depend on it staying strict.
#
#   ORDERING
#
#   textNameSortKey is what puts a group in reading order. It sorts on the parsed chapter NUMBER rather than on the name, which is what makes three separate things come out right: "Matthew 03-04"
#   lands between "Matthew 02" and "Matthew 05" (it sorts by the first chapter it covers), "Matthew 10" follows "Matthew 09" even when the names are not zero padded, and a " - Copy" sorts after the
#   text it was copied from. Names with no chapter at all sort after every name that has one, so an oddly named text cannot get mixed into the middle of a book.
#
#   GROUPING
#
#   groupTextNames buckets names by their parsed base, compared case-insensitively so "matthew 05" joins "Matthew 04", and drops any bucket with only one member - one text is not a merge. The
#   spelling of the base that is shown to the user, and that the merged name is built from, is the first one seen, so the merge is named the way the user names their texts.
#
#   THE MERGED NAME
#
#   mergedTextName names the merged text for the range actually merged, not for the whole book: merging every chapter of Matthew gives "Matthew 01-28", and merging only part of it gives
#   "Matthew 03-24". The low end comes from the first member and the high end from the last member's TO chapter, so merging up to "Matthew 23-24" ends the name at 24 rather than 23. Numbers are
#   padded to the widest padding seen in the members, so a project that zero pads keeps zero padding. A group whose members have no parseable chapter falls back to the bare base name.
#
#   CODE STRUCTURE
#
#   parseChapterToken - one digit run to an int, or None. The single place to extend if roman numeral chapters are ever wanted.
#   parseTextName - the workhorse; returns (baseName, chapFrom, chapTo, suffix), with chapFrom None when the name carries no chapter.
#   chapterPadWidth - how many digits the chapter was written with, so the merged name can be padded to match.
#   naturalSortKey - digits-as-numbers key, used for names with no chapter token and for sorting a manual selection by name.
#   textNameSortKey - the reading-order key described above; built on parseTextName and naturalSortKey.
#   groupTextNames - names to [(displayBase, orderedNameList)], multi-member groups only.
#   mergedTextName - the range name for a group.
#   chapterRangeList / chapterCoverage - what a selection covers, as plain numbers the dialog turns into a translated sentence: the range, and any gaps or overlaps in it. chapterCoverage says
#   nothing at all unless every name in the selection carries a chapter, so a merge of ordinary texts is never described as though it were scripture.
#

import re

# The trailing chapter token on a text name. See THE CHAPTER TOKEN above for why the base is non-greedy (it keeps a chapter span whole) and why the chapter is capped at three digits - both are load bearing.
CHAPTER_TOKEN_RE = re.compile(r'^(?P<base>.*?)[\s_-]+(?P<chapFrom>\d{1,3})(?:\s*-\s*(?P<chapTo>\d{1,3}))?(?P<suffix>(?: - Copy(?: \(\d{1,2}\))?)?)$')

def parseChapterToken(token):

    # One digit run to a chapter number. Split out from parseTextName as the single place to extend: roman numeral chapters would be recognised here. They are deliberately not supported yet, because
    # a trailing I, V or X is far more likely to be part of a real text name than a chapter number, and a false positive silently mis-orders a merge.
    if not token or not token.isdigit():

        return None

    return int(token)

def parseTextName(name):

    """Split a text name into (baseName, chapFrom, chapTo, suffix). chapFrom is None when the name carries no chapter token, in which case baseName is the whole (stripped) name."""

    strippedName = name.strip()
    match = CHAPTER_TOKEN_RE.match(strippedName)

    if not match:

        return strippedName, None, None, ''

    chapFrom = parseChapterToken(match.group('chapFrom'))

    if chapFrom is None:

        return strippedName, None, None, ''

    chapTo = parseChapterToken(match.group('chapTo'))

    return match.group('base').strip(), chapFrom, chapTo, match.group('suffix')

def chapterPadWidth(name):

    """How many digits the chapter was written with, so the merged name can be padded the same way. Zero when the name carries no chapter."""

    match = CHAPTER_TOKEN_RE.match(name.strip())

    if not match or parseChapterToken(match.group('chapFrom')) is None:

        return 0

    widthList = [len(match.group('chapFrom'))]

    if match.group('chapTo'):

        widthList.append(len(match.group('chapTo')))

    return max(widthList)

def naturalSortKey(name):

    """A sort key that compares digit runs as numbers, so 'Text 9' comes before 'Text 10'. Used for names with no chapter token, and for the dialog's sort-by-name button."""

    keyList = []

    # re.split with a capturing group alternates non-digit and digit pieces. Every piece becomes a 3-tuple of the same shape so that a number is never compared against a string, which would raise.
    for piece in re.split(r'(\d+)', name):

        if piece.isdigit():

            keyList.append((0, int(piece), ''))

        else:
            keyList.append((1, 0, piece.casefold()))

    return keyList

def textNameSortKey(name):

    """Reading order for text names: by book, then by chapter number, then by name. See ORDERING above."""

    baseName, chapFrom, chapTo, suffix = parseTextName(name)

    # A name with no chapter sorts after every name that has one (that is what the 0/1 field does), so an oddly named text cannot land in the middle of a book. Within one starting chapter a span
    # sorts by the chapter it ends at, and a ' - Copy' sorts after the text it was copied from.
    return (baseName.casefold(),
            0 if chapFrom is not None else 1,
            chapFrom if chapFrom is not None else 0,
            chapTo if chapTo is not None else (chapFrom if chapFrom is not None else 0),
            suffix,
            naturalSortKey(name))

def groupTextNames(nameList):

    """Bucket text names into likely books, returning [(displayBase, orderedNameList)] for every base with two or more members. Groups are ordered by base name, members in reading order."""

    groupMap = {}

    for name in nameList:

        baseName, chapFrom, _chapTo, _suffix = parseTextName(name)

        # No chapter token means there is nothing to merge this with. Leaving it ungrouped is what keeps ordinary texts out of the group picker.
        if chapFrom is None:

            continue

        groupKey = baseName.casefold()

        # Keep the first spelling seen as the one shown to the user and used to build the merged name, so the merge is named the way the user names their texts.
        if groupKey not in groupMap:

            groupMap[groupKey] = (baseName, [])

        groupMap[groupKey][1].append(name)

    groupList = []

    for groupKey in sorted(groupMap):

        displayBase, memberList = groupMap[groupKey]

        # One text is not a merge.
        if len(memberList) < 2:

            continue

        groupList.append((displayBase, sorted(memberList, key=textNameSortKey)))

    return groupList

def mergedTextName(displayBase, orderedNameList):

    """The name for the text a merge produces: the base plus the chapter range actually being merged, e.g. 'Matthew 01-28' or 'Matthew 03-24'. See THE MERGED NAME above."""

    parsedList = [parseTextName(name) for name in orderedNameList]
    chapteredList = [parsed for parsed in parsedList if parsed[1] is not None]

    # Nothing in the selection carries a chapter, so there is no range to name it after. Hand back the base and let the user type over it.
    if not chapteredList:

        return displayBase

    firstChap = chapteredList[0][1]
    lastParsed = chapteredList[-1]

    # The high end of the range is the last member's TO chapter when that member covers a span, so merging up to 'Matthew 23-24' ends the name at 24 rather than 23.
    lastChap = lastParsed[2] if lastParsed[2] is not None else lastParsed[1]

    # Pad to the widest padding any member used, so a project that zero pads its chapters keeps zero padded names. The +[1] floor covers a selection whose members are all unpadded.
    padWidth = max([chapterPadWidth(name) for name in orderedNameList] + [1])

    if firstChap == lastChap:

        return f'{displayBase} {firstChap:0{padWidth}d}'

    return f'{displayBase} {firstChap:0{padWidth}d}-{lastChap:0{padWidth}d}'

def chapterRangeList(orderedNameList):

    """The (chapFrom, chapTo) pairs of the names that carry a chapter, in the order given. Names with no chapter are left out."""

    rangeList = []

    for name in orderedNameList:

        _baseName, chapFrom, chapTo, _suffix = parseTextName(name)

        if chapFrom is None:

            continue

        rangeList.append((chapFrom, chapTo if chapTo is not None else chapFrom))

    return rangeList

def chapterCoverage(orderedNameList):

    """What a selection covers, as (lowChap, highChap, missingList, overlapList), or None when the selection is not a run of chapters.

    EVERY name has to carry a chapter, not just one of them. A mixture - say "Examples from Chapter 8" picked alongside a text called "Words" - is not a chapter run at all, and describing its
    coverage would quietly drop the names that have no chapter and then announce a range and a gap check the user never asked for, which reads as FLExTrans having decided the texts are scripture.

    Deliberately structured rather than a ready-made sentence: this file has no user-facing strings and therefore no .ts file, so the wording has to be assembled by the caller in order to be
    translatable. MergeTextsDlg.coverageDescription() is that caller.
    """

    rangeList = chapterRangeList(orderedNameList)

    # chapterRangeList leaves out the names with no chapter, so a rangeList shorter than the selection means at least one selected text is not a chapter of anything.
    if not rangeList or len(rangeList) < len(orderedNameList):

        return None

    coveredSet = set()
    overlapSet = set()

    for chapFrom, chapTo in rangeList:

        for chapNum in range(chapFrom, chapTo + 1):

            # A chapter covered by two different members means the merged text would contain it twice. Worth reporting, since it usually means a stale ' - Copy' is still in the selection.
            if chapNum in coveredSet:

                overlapSet.add(chapNum)

            coveredSet.add(chapNum)

    lowChap = min(coveredSet)
    highChap = max(coveredSet)
    missingList = [chapNum for chapNum in range(lowChap, highChap + 1) if chapNum not in coveredSet]

    return lowChap, highChap, missingList, sorted(overlapSet)
