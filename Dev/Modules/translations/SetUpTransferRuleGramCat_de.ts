<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>SetUpTransferRuleGramCat</name>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="100"/>
        <source>Set up the transfer rule file with categories and attributes from souce and target FLEx projects.</source>
        <translation>Die Transferregeldatei mit Kategorien und Attributen aus Quell- und Ziel-FLEx-Projekten einrichten.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="102"/>
        <source>This module first goes through both the source and target FLEx databases and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.</source>
        <translation>Dieses Modul durchläuft zunächst sowohl die Quell- als auch die Ziel-FLEx-Datenbanken und extrahiert
die grammatischen Kategorienlisten. Es ersetzt das, was derzeit für die Tags des
a_gram_cat-Attributs aufgelistet ist, durch die extrahierten Listen. Doppelte Kategorien
werden verworfen. Außerdem werden Namenskonventionen wie im zweisprachigen Lexikon befolgt.
D.h. Leerzeichen werden in Unterstriche umgewandelt, Punkte und Schrägstriche werden entfernt.
Dieses Modul füllt auch den Kategorienbereich der Transferregeldatei mit grammatischen
Kategorien aus dem Quell-FLEx-Projekt. Dieses Modul erstellt auch Attribute in der
Transferregeldatei aus FLEx-Flexionsmerkmalen, Flexionsklassen und Vorlagenslots.
Sie können entscheiden, welche davon verwendet werden und ob vorhandene Attribute
überschrieben werden sollen.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="542"/>
        <source>The transfer rules file has not yet been saved with the XML Mind editor. Change the file in the editor and then run this tool again.</source>
        <translation>Die Transferregeldatei wurde noch nicht mit dem XML Mind-Editor gespeichert. Ändern Sie die Datei im Editor und führen Sie dieses Tool dann erneut aus.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="614"/>
        <source>There was a problem finding the transfer rules file. Check your configuration.</source>
        <translation>Es gab ein Problem beim Finden der Transferregeldatei. Überprüfen Sie Ihre Konfiguration.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="653"/>
        <source>The transfer rules file is malformed.</source>
        <translation>Die Transferregeldatei ist fehlerhaft.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="693"/>
        <source>{attrCount} attributes added to the attributes section.</source>
        <translation>{attrCount} Attribute zum Attributbereich hinzugefügt.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="694"/>
        <source>{num} categories created for the a_gram_cat attribute.</source>
        <translation>{num} Kategorien für das a_gram_cat-Attribut erstellt.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="695"/>
        <source>{catCount} categories added to the categories section.</source>
        <translation>{catCount} Kategorien zum Kategorienbereich hinzugefügt.</translation>
    </message>
</context>
</TS>