<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="167"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation>Text mit HermitCrab synthetisieren</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="170"/>
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
        <translation type="obsolete">Dieses Modul führt HermitCrab aus, um den synthetisierten Text zu erstellen. Die Ergebnisse werden in die Datei geschrieben, die in den Einstellungen als Zielausgabe-Synthesedatei angegeben ist. Standardmäßig wird dies etwas wie 'target_text-syn.txt' sein. 
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul das Lexikon der Zielsprache in Form einer HermitCrab-Konfigurationsdatei. 
Diese heißt 'HermitCrab.config' und befindet sich im Ordner 'Build'. 
HINWEIS: Nachrichten werden anzeigen, dass die QUELLE-Datenbank verwendet wird. Tatsächlich wird die Zieldatenbank verwendet. 
Erweiterte Informationen: Dieses Modul führt HermitCrab gegen eine Liste von Zielanalysen ('target_words-parses.txt') aus, um Oberflächenformen ('target_words-surface.txt') zu erzeugen. 
Diese Formen werden dann verwendet, um den Zieltext zu erstellen.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="224"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problem mit der Konfigurationsdatei für TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="218"/>
        <source>Failed to open the target database: {targetProj}.</source>
        <translation type="obsolete">Die Zieldatenbank konnte nicht geöffnet werden: {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="244"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation>Ein Wert für {cacheData} wurde in der Konfigurationsdatei nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="275"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation>Beim Laden der HermitCrab-Konfigurationsdatei für das HC-Syntheseobjekt (DLL) ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="283"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation>Die HermitCrab-Konfigurationsdatei ist auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="293"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation>Die HermitCrab-Konfigurationsdatei wurde erstellt: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="322"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation>Beim Ausführen des Tools 'Generate HermitCrab Configuration' ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="283"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} database.</source>
        <translation type="obsolete">Der Fehler enthält eine 'KeyNotFoundException', was oft darauf hinweist, dass das FLEx Find and Fix-Dienstprogramm auf der {projectName}-Datenbank ausgeführt werden sollte.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="301"/>
        <source>The full error message is:</source>
        <translation>Die vollständige Fehlermeldung lautet:</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="312"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation>Beim Laden der HermitCrab-Konfigurationsdatei für das HC-Syntheseobjekt ist ein Fehler aufgetreten. Dies geschah, nachdem die Konfigurationsdatei erstellt wurde. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="267"/>
        <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
        <translation>Beim Versuch, die HermitCrab-XML-Datei vom DLL-Objekt zu erhalten, ist eine Ausnahme aufgetreten: {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="317"/>
        <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
        <translation>Beim Versuch, die HermitCrab-XML-Datei im DLL-Objekt zu setzen, ist eine Ausnahme aufgetreten. Fehler: {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="352"/>
        <source>There was an error opening the HermitCrab surface forms file.</source>
        <translation>Beim Öffnen der HermitCrab-Oberflächenformendatei ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="344"/>
        <source>The file: {transferResultsFile} was not found. Did you run the Run Apertium module?</source>
        <translation type="obsolete">Die Datei: {transferResultsFile} wurde nicht gefunden. Haben Sie das Modul &quot;Run Apertium&quot; ausgeführt?</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="376"/>
        <source>The number of surface forms does not match the number of Lexical Units.</source>
        <translation>Die Anzahl der Oberflächenformen stimmt nicht mit der Anzahl der Lexikalischen Einheiten überein.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="406"/>
        <source>Synthesis failed. ({saveStr})</source>
        <translation>Synthese fehlgeschlagen. ({saveStr})</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="430"/>
        <source>Error writing the file: {synFile}.</source>
        <translation>Fehler beim Schreiben der Datei: {synFile}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="447"/>
        <source>There was an error opening the HermitCrab master file. Do you have the setting &quot;Use HermitCrab Synthesis&quot; turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
        <translation>Beim Öffnen der HermitCrab-Masterdatei ist ein Fehler aufgetreten. Ist die Einstellung &quot;Use HermitCrab Synthesis&quot; aktiviert? Haben Sie das Modul &quot;Convert Text to Synthesizer Format&quot; ausgeführt? Datei: {parsesFile}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="456"/>
        <source>There was an error opening the HermitCrab parses file.</source>
        <translation>Beim Öffnen der HermitCrab-Analysedatei ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="662"/>
        <source>Unable to open the HC master file.</source>
        <translation>Die HC-Masterdatei konnte nicht geöffnet werden.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="688"/>
        <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Beim Setzen der Glossdatei für das HermitCrab Synthesize By Gloss-Tool (DLL) ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="693"/>
        <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Beim Versuch, die Glossdatei für das HermitCrab Synthesize By Gloss-Tool (DLL) zu setzen, ist eine Ausnahme aufgetreten. Fehler: {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="699"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Beim Ausführen des HermitCrab Synthesize By Gloss-Tools (DLL) ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="704"/>
        <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Beim Versuch, das HermitCrab Synthesize By Gloss-Tool (DLL) auszuführen (durch Aufruf von Process), ist eine Ausnahme aufgetreten. Fehler: {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="724"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
        <translation>Beim Ausführen des HermitCrab Synthesize By Gloss-Tools ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="737"/>
        <source>An error happened when trying to open the file: {parsesFile}</source>
        <translation>Beim Versuch, die Datei zu öffnen: {parsesFile}, ist ein Fehler aufgetreten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="740"/>
        <source>Processing {LUsCount} unique lexical units.</source>
        <translation>Verarbeite {LUsCount} eindeutige lexikalische Einheiten.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="755"/>
        <source>Configuration file problem with the value: {val}.</source>
        <translation>Problem mit der Konfigurationsdatei beim Wert: {val}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="770"/>
        <source>The synthesized target text is in the file: {file}.</source>
        <translation>Der synthetisierte Zieltext befindet sich in der Datei: {file}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="771"/>
        <source>Synthesis complete.</source>
        <translation>Synthese abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="809"/>
        <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
        <translation>{master} oder {parses} oder {surface} oder {transfer} wurde in der Konfigurationsdatei nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="172"/>
        <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like &apos;target_text-syn.txt&apos;. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named &apos;HermitCrab.config&apos; and will be in the &apos;Build&apos; folder. 
NOTE: Messages will say the source project
is being used. Actually the target project is being used.
Advanced Information: This module runs HermitCrab against a list of target parses (&apos;target_words-parses.txt&apos;) to
produce surface forms (&apos;target_words-surface.txt&apos;). 
These forms are then used to create the target text.</source>
        <translation>Dieses Modul führt HermitCrab aus, um den synthetisierten Text zu erstellen. Die Ergebnisse werden in die Datei geschrieben, die in den Einstellungen als Ziel-Output-Synthese-Datei bezeichnet ist.
Dies wird standardmäßig etwas wie &apos;target_text-syn.txt&apos; sein. 
Bevor der synthetisierte Text erstellt wird, extrahiert dieses Modul das Lexikon der Zielsprache in Form einer HermitCrab-Konfigurationsdatei. 
Sie heißt &apos;HermitCrab.config&apos; und befindet sich im &apos;Build&apos;-Ordner. 
HINWEIS: Meldungen werden sagen, dass das Quellprojekt verwendet wird. Tatsächlich wird das Zielprojekt verwendet.
Erweiterte Informationen: Dieses Modul führt HermitCrab gegen eine Liste von Zielparsen (&apos;target_words-parses.txt&apos;) aus, um Oberflächenformen (&apos;target_words-surface.txt&apos;) zu erzeugen. 
Diese Formen werden dann verwendet, um den Zielsprachtext zu erstellen.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="235"/>
        <source>Failed to open the target project: {targetProj}.</source>
        <translation>Fehler beim Öffnen des Zielprojekts: {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="300"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.</source>
        <translation>Der Fehler enthält eine &apos;KeyNotFoundException&apos;, was oft darauf hinweist, dass das FLEx Find and Fix-Werkzeug auf das Projekt {projectName} angewendet werden sollte.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="361"/>
        <source>The file: {transferResultsFile} was not found. Did you run the {runApertium} module?</source>
        <translation>Die Datei: {transferResultsFile} wurde nicht gefunden. Haben Sie das Modul {runApertium} ausgeführt?</translation>
    </message>
</context>
</TS>
