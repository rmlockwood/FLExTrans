<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoStampSynthesis</name>
    <message>
        <location filename="../DoStampSynthesis.py" line="147"/>
        <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the SOURCE database is being used. Actually the target database is being used.</source>
        <translation type="obsolete">Dieses Modul führt STAMP aus, um den synthetisierten Text zu erstellen. 
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul die Lexikondateien der Zielsprache, jeweils eine für 
Wurzeln, Präfixe, Suffixe und Infixe. Sie befinden sich im STAMP-Format für die Synthese. Die Lexikondateien 
werden in den Ordner gelegt, der in den Einstellungen als Ziellexikondateien-Ordner angegeben ist. Normalerweise ist dies der Ordner 'Build'. 
Der synthetisierte Text wird in der Datei gespeichert, die in der Einstellung Zielausgabe-Synthesedatei angegeben ist. 
Diese wird typischerweise target_text-syn.txt genannt und befindet sich normalerweise im Ordner 'Output'. 
HINWEIS: Nachrichten zeigen an, dass die QUELLE-Datenbank verwendet wird. Tatsächlich wird die Zieldatenbank verwendet.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="159"/>
        <source>Synthesizes the target text with the tool STAMP.</source>
        <translation>Synthetisiert den Zieltext mit dem Tool STAMP.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="747"/>
        <source>Null grapheme found for natural class: {natClassName}. Skipping.</source>
        <translation>Null-Graphem für natürliche Klasse gefunden: {natClassName}. Überspringen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="775"/>
        <source>Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Lexemform unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="783"/>
        <source>Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da der Morphemtyp unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="858"/>
        <source>Skipping sense because the POS is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Wortart (POS) unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="861"/>
        <source>Skipping sense that is of class: {className} for headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, die zur Klasse gehört: {className} für Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="864"/>
        <source>Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da keine morphosyntaktische Analyse vorliegt. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="882"/>
        <source>No gloss. Skipping. Headword: {headword}.</source>
        <translation>Keine Glosse. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="886"/>
        <source>No lexeme form. Skipping. Headword: {headword}.</source>
        <translation>Keine Lexemform. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="890"/>
        <source>No Morph Type. Skipping. {headword} Best Vern: {vernacular}.</source>
        <translation>Kein Morphtyp. Überspringen. {headword} Beste Umgangssprache: {vernacular}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="900"/>
        <source>Skipping entry since the lexeme is of type: {className}.</source>
        <translation>Eintrag wird übersprungen, da das Lexem vom Typ ist: {className}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="986"/>
        <source>Skipping entry because the morph type is: {morphType}.</source>
        <translation>Eintrag wird übersprungen, da der Morphtyp ist: {morphType}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="922"/>
        <source>STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.</source>
        <translation>STAMP-Wörterbücher erstellt. {roots} Wurzeln, {prefixes} Präfixe, {suffixes} Suffixe und {infixes} Infixe.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1115"/>
        <source>Configuration file problem.</source>
        <translation>Problem mit der Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1001"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problem mit der Konfigurationsdatei für TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1130"/>
        <source>Configuration file problem with {folder}.</source>
        <translation>Problem mit der Konfigurationsdatei für {folder}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1135"/>
        <source>Lexicon files folder: {folder} does not exist.</source>
        <translation>Lexikondateien-Ordner: {folder} existiert nicht.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1021"/>
        <source>Configuration file problem with {cacheData}.</source>
        <translation>Problem mit der Konfigurationsdatei für {cacheData}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1028"/>
        <source>The Target Database does not exist. Please check the configuration file.</source>
        <translation type="obsolete">Die Zieldatenbank existiert nicht. Bitte überprüfen Sie die Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1033"/>
        <source>Problem accessing the target project.</source>
        <translation>Problem beim Zugriff auf das Zielprojekt.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1038"/>
        <source>Failed to open the target database.</source>
        <translation type="obsolete">Die Zieldatenbank konnte nicht geöffnet werden.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1044"/>
        <source>Target lexicon files are up to date.</source>
        <translation>Ziellexikondateien sind auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1152"/>
        <source>The synthesized target text is in the file: {filePath}.</source>
        <translation>Der synthetisierte Zieltext befindet sich in der Datei: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1153"/>
        <source>Synthesis complete.</source>
        <translation>Synthese abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1176"/>
        <source>The Convert Text to STAMP Format module must be run before this module. The {fileType}: {filePath} does not exist.</source>
        <translation>Das Modul 'Convert Text to STAMP Format' muss vor diesem Modul ausgeführt werden. Die Datei {fileType}: {filePath} existiert nicht.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="147"/>
        <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the source project is being used. Actually the target project is being used.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1028"/>
        <source>The target project does not exist. Please check the configuration file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1038"/>
        <source>Failed to open the target project.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
