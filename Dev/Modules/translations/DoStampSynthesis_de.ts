<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en">
<context>
    <name>DoStampSynthesis</name>
    <message>
        <location filename="../DoStampSynthesis.py" line="182"/>
        <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the source project is being used. Actually the target project is being used.</source>
        <translation>Dieses Modul führt STAMP aus, um den synthetisierten Text zu erstellen.
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul die Lexikondaten der Zielsprache, jeweils eine Datei für Wurzeln, Präfixe, Suffixe und Infixe. Diese liegen im STAMP-Format für die Synthese vor. Die Lexikondaten werden in den Ordner geschrieben, der in den Einstellungen als „Target Lexicon Files Folder“ angegeben ist. In der Regel ist dies der „Build“-Ordner.
Der synthetisierte Text wird in der Datei gespeichert, die in den Einstellungen als „Target Output Synthesis File“ angegeben ist.
Diese heißt typischerweise target_text-syn.txt und befindet sich normalerweise im Output-Ordner.
HINWEIS: Die Meldungen geben an, dass das Quellprojekt verwendet wird. Tatsächlich wird aber das Zielprojekt verwendet.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="191"/>
        <source>Synthesize Text with STAMP</source>
        <translation>Text mit STAMP synthetisieren</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="194"/>
        <source>Synthesizes the target text with the tool STAMP.</source>
        <translation>Synthetisiert den Zieltext mit dem Tool STAMP.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="921"/>
        <source>Null grapheme found for natural class: {natClassName}. Skipping.</source>
        <translation>Null-Graphem für natürliche Klasse gefunden: {natClassName}. Überspringen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="963"/>
        <source>Aborting target lexicon export because the custom XAMPLE field is not a list. When you define the custom XAMPLE field, it must be a list.</source>
        <translation type="unfinished">Aborting target lexicon export because the custom XAMPLE field is not a list. When you define the custom XAMPLE field, it must be a list.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="974"/>
        <source>Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Lexemform unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="982"/>
        <source>Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da der Morphemtyp unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1066"/>
        <source>Skipping sense because the POS is unknown: while processing target headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da die Wortart (POS) unbekannt ist: während der Verarbeitung des Zielstichworts: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1069"/>
        <source>Skipping sense that is of class: {className} for headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, die zur Klasse gehört: {className} für Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1072"/>
        <source>Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.</source>
        <translation>Bedeutung wird übersprungen, da keine morphosyntaktische Analyse vorliegt. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1092"/>
        <source>No gloss. Skipping. Headword: {headword}.</source>
        <translation>Keine Glosse. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1096"/>
        <source>No lexeme form. Skipping. Headword: {headword}.</source>
        <translation>Keine Lexemform. Überspringen. Stichwort: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1100"/>
        <source>No Morph Type. Skipping. {headword} Best Vern: {vernacular}.</source>
        <translation>Kein Morphtyp. Überspringen. {headword} Beste Umgangssprache: {vernacular}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1110"/>
        <source>Skipping entry since the lexeme is of type: {className}.</source>
        <translation>Eintrag wird übersprungen, da das Lexem vom Typ ist: {className}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1196"/>
        <source>Skipping entry because the morph type is: {morphType}.</source>
        <translation>Eintrag wird übersprungen, da der Morphtyp ist: {morphType}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1132"/>
        <source>STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.</source>
        <translation>STAMP-Wörterbücher erstellt. {roots} Wurzeln, {prefixes} Präfixe, {suffixes} Suffixe und {infixes} Infixe.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1367"/>
        <source>Configuration file problem.</source>
        <translation>Problem mit der Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1211"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problem mit der Konfigurationsdatei für TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1382"/>
        <source>Configuration file problem with {folder}.</source>
        <translation>Problem mit der Konfigurationsdatei für {folder}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1387"/>
        <source>Lexicon files folder: {folder} does not exist.</source>
        <translation>Lexikondateien-Ordner: {folder} existiert nicht.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1231"/>
        <source>Configuration file problem with {cacheData}.</source>
        <translation>Problem mit der Konfigurationsdatei für {cacheData}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1238"/>
        <source>The target project does not exist. Please check the configuration file.</source>
        <translation>Das Zielprojekt existiert nicht. Bitte überprüfen Sie die Konfigurationsdatei.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1243"/>
        <source>Problem accessing the target project.</source>
        <translation>Problem beim Zugriff auf das Zielprojekt.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1248"/>
        <source>Failed to open the target project.</source>
        <translation>Das Zielprojekt konnte nicht geöffnet werden.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1254"/>
        <source>Target lexicon files are up to date.</source>
        <translation>Ziellexikondateien sind auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1415"/>
        <source>The synthesized target text is in the file: {filePath}.</source>
        <translation>Der synthetisierte Zieltext befindet sich in der Datei: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1416"/>
        <source>Synthesis complete.</source>
        <translation>Synthese abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1408"/>
        <source>An error happened when running the STAMP tool.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1439"/>
        <source>The {modname} module must be run before this module. The file: ...\{filePath} does not exist.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
