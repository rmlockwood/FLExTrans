<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoStampSynthesis</name>
    <message>
        <location filename="../DoStampSynthesis.py" line="142"/>
        <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the SOURCE database is being used. Actually the target database is being used.</source>
        <translation>Dieses Modul führt STAMP aus, um den synthetisierten Text zu erstellen. 
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul die Lexikondateien der Zielsprache, jeweils eine für 
Wurzeln, Präfixe, Suffixe und Infixe. Sie befinden sich im STAMP-Format für die Synthese. Die Lexikondateien 
werden in den Ordner gelegt, der in den Einstellungen als Ziellexikondateien-Ordner angegeben ist. Normalerweise ist dies der Ordner &apos;Build&apos;. 
Der synthetisierte Text wird in der Datei gespeichert, die in der Einstellung Zielausgabe-Synthesedatei angegeben ist. 
Diese wird typischerweise target_text-syn.txt genannt und befindet sich normalerweise im Ordner &apos;Output&apos;. 
HINWEIS: Nachrichten zeigen an, dass die QUELLE-Datenbank verwendet wird. Tatsächlich wird die Zieldatenbank verwendet.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="154"/>
        <source>Synthesizes the target text with the tool STAMP.</source>
        <translation>Synthetisiert den Zieltext mit dem Tool STAMP.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="742"/>
        <source>Null grapheme found for natural class: {natClassName}. Skipping.</source>
        <translation>Null-Graphem für natürliche Klasse gefunden: {natClassName}. Überspringen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="770"/>
        <source>Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Lexemform unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="778"/>
        <source>Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da der Morphemtyp unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="853"/>
        <source>Skipping sense because the POS is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Wortart (POS) unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="856"/>
        <source>Skipping sense that is of class: {className} for headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, die zur Klasse gehört: {className} für Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="859"/>
        <source>Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da keine morphosyntaktische Analyse vorliegt. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="877"/>
        <source>No gloss. Skipping. Headword: {headword}.</source>
        <translation>Keine Glosse. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="881"/>
        <source>No lexeme form. Skipping. Headword: {headword}.</source>
        <translation>Keine Lexemform. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="885"/>
        <source>No Morph Type. Skipping. {headword} Best Vern: {vernacular}.</source>
        <translation>Kein Morphtyp. Überspringen. {headword} Beste Umgangssprache: {vernacular}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="895"/>
        <source>Skipping entry since the lexeme is of type: {className}.</source>
        <translation>Eintrag wird übersprungen, da das Lexem vom Typ ist: {className}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="981"/>
        <source>Skipping entry because the morph type is: {morphType}.</source>
        <translation>Eintrag wird übersprungen, da der Morphtyp ist: {morphType}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="917"/>
        <source>STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.</source>
        <translation>STAMP-Wörterbücher erstellt. {roots} Wurzeln, {prefixes} Präfixe, {suffixes} Suffixe und {infixes} Infixe.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1110"/>
        <source>Configuration file problem.</source>
        <translation>Problem mit der Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="996"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problem mit der Konfigurationsdatei für TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1125"/>
        <source>Configuration file problem with {folder}.</source>
        <translation>Problem mit der Konfigurationsdatei für {folder}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1007"/>
        <source>Lexicon files folder: {folder} does not exist.</source>
        <translation>Lexikondateien-Ordner: {folder} existiert nicht.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1016"/>
        <source>Configuration file problem with {cacheData}.</source>
        <translation>Problem mit der Konfigurationsdatei für {cacheData}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1023"/>
        <source>The Target Database does not exist. Please check the configuration file.</source>
        <translation>Die Zieldatenbank existiert nicht. Bitte überprüfen Sie die Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1028"/>
        <source>Problem accessing the target project.</source>
        <translation>Problem beim Zugriff auf das Zielprojekt.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1033"/>
        <source>Failed to open the target database.</source>
        <translation>Die Zieldatenbank konnte nicht geöffnet werden.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1039"/>
        <source>Target lexicon files are up to date.</source>
        <translation>Ziellexikondateien sind auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1147"/>
        <source>The synthesized target text is in the file: {filePath}.</source>
        <translation>Der synthetisierte Zieltext befindet sich in der Datei: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1148"/>
        <source>Synthesis complete.</source>
        <translation>Synthese abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1171"/>
        <source>The Convert Text to STAMP Format module must be run before this module. The {fileType}: {filePath} does not exist.</source>
        <translation>Das Modul &apos;Convert Text to STAMP Format&apos; muss vor diesem Modul ausgeführt werden. Die Datei {fileType}: {filePath} existiert nicht.</translation>
    </message>
</context>
</TS>