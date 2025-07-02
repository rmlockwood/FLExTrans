<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>SetUpTransferRuleGramCat</name>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="108"/>
        <source>Set up the transfer rule file with categories and attributes from source and target FLEx projects.</source>
        <translation>Die Transferregeldatei mit Kategorien und Attributen aus Quell- und Ziel-FLEx-Projekten einrichten.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="534"/>
        <source>There was a problem finding the transfer rules file. Check your configuration.</source>
        <translation>Es gab ein Problem beim Finden der Transferregeldatei. Überprüfen Sie Ihre Konfiguration.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="594"/>
        <source>{attrCount} attributes added to the attributes section.</source>
        <translation>{attrCount} Attribute zum Attributbereich hinzugefügt.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="595"/>
        <source>{num} categories created for the a_gram_cat attribute.</source>
        <translation>{num} Kategorien für das a_gram_cat-Attribut erstellt.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="596"/>
        <source>{catCount} categories added to the categories section.</source>
        <translation>{catCount} Kategorien zum Kategorienbereich hinzugefügt.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="546"/>
        <source>The transfer rules file is malformed or not valid XML.</source>
        <translation>Die Transferregeldatei ist fehlerhaft oder kein gültiges XML.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="556"/>
        <source>The transfer rules file is missing required sections.</source>
        <translation>Der Transferregeldatei fehlen erforderliche Abschnitte.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="591"/>
        <source>There was a problem writing the transfer rules file: {error}</source>
        <translation>Beim Schreiben der Transferregeldatei ist ein Problem aufgetreten: {error}</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="110"/>
        <source>This module first goes through both the source and target FLEx projects and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
