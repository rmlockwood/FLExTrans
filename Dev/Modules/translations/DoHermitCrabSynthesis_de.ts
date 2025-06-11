<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="142"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation type="obsolete">Text mit HermitCrab synthetisieren</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="153"/>
        <source>Synthesizes the target text with the tool HermitCrab.</source>
        <translation>Synthetisiert den Zieltext mit dem Tool HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="155"/>
        <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like &apos;target_text-syn.txt&apos;. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named &apos;HermitCrab.config&apos; and will be in the &apos;Build&apos; folder. 
NOTE: Messages will say the SOURCE database
is being used. Actually the target database is being used.
Advanced Information: This module runs HermitCrab against a list of target parses (&apos;target_words-parses.txt&apos;) to
produce surface forms (&apos;target_words-surface.txt&apos;). 
These forms are then used to create the target text.</source>
        <translation>Dieses Modul führt HermitCrab aus, um den synthetisierten Text zu erstellen. Die Ergebnisse werden in die Datei geschrieben, die in den Einstellungen als Zielausgabe-Synthesedatei angegeben ist. Standardmäßig wird dies etwas wie 'target_text-syn.txt' sein. 
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul das Lexikon der Zielsprache in Form einer HermitCrab-Konfigurationsdatei. 
Diese heißt 'HermitCrab.config' und befindet sich im Ordner 'Build'. 
HINWEIS: Nachrichten werden anzeigen, dass die QUELLE-Datenbank verwendet wird. Tatsächlich wird die Zieldatenbank verwendet. 
Erweiterte Informationen: Dieses Modul führt HermitCrab gegen eine Liste von Zielanalysen ('target_words-parses.txt') aus, um Oberflächenformen ('target_words-surface.txt') zu erzeugen. 
Diese Formen werden dann verwendet, um den Zieltext zu erstellen.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="207"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problem mit der Konfigurationsdatei für TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="218"/>
        <source>Failed to open the target database: {targetProj}.</source>
        <translation>Die Zieldatenbank konnte nicht geöffnet werden: {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="227"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation>Ein Wert für {cacheData} wurde in der Konfigurationsdatei nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="258"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation>Beim Laden der HermitCrab-Konfigurationsdatei für das HC-Syntheseobjekt (DLL) ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="266"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation>Die HermitCrab-Konfigurationsdatei ist auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="276"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation>Die HermitCrab-Konfigurationsdatei wurde erstellt: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="305"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation>Beim Ausführen des Tools 'Generate HermitCrab Configuration' ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="283"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} database.</source>
        <translation>Der Fehler enthält eine 'KeyNotFoundException', was oft darauf hinweist, dass das FLEx Find and Fix-Dienstprogramm auf der {projectName}-Datenbank ausgeführt werden sollte.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="284"/>
        <source>The full error message is:</source>
        <translation>Die vollständige Fehlermeldung lautet:</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="295"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation>Beim Laden der HermitCrab-Konfigurationsdatei für das HC-Syntheseobjekt ist ein Fehler aufgetreten. Dies geschah, nachdem die Konfigurationsdatei erstellt wurde. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="250"/>
        <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="300"/>
        <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="335"/>
        <source>There was an error opening the HermitCrab surface forms file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="344"/>
        <source>The file: {transferResultsFile} was not found. Did you run the Run Apertium module?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="359"/>
        <source>The number of surface forms does not match the number of Lexical Units.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="389"/>
        <source>Synthesis failed. ({saveStr})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="413"/>
        <source>Error writing the file: {synFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="430"/>
        <source>There was an error opening the HermitCrab master file. Do you have the setting &quot;Use HermitCrab Synthesis&quot; turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="439"/>
        <source>There was an error opening the HermitCrab parses file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="565"/>
        <source>Unable to open the HC master file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="591"/>
        <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="596"/>
        <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="602"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="607"/>
        <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="627"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="640"/>
        <source>An error happened when trying to open the file: {parsesFile}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="643"/>
        <source>Processing {LUsCount} unique lexical units.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="658"/>
        <source>Configuration file problem with the value: {val}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="673"/>
        <source>The synthesized target text is in the file: {file}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="674"/>
        <source>Synthesis complete.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="712"/>
        <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
