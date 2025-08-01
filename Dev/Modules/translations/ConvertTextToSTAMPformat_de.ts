<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ConvertTextToSTAMPformat</name>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="174"/>
      <source>Convert the file produced by {runApert} into a text file in a Synthesizer format</source>
      <translation>Konvertieren Sie die von {runApert} erstellte Datei in eine Textdatei im Synthesizer-Format</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="176"/>
      <source>This module will take the Target Transfer Results File created by {runApert} and convert it to a format suitable 
for synthesis, using information from the Target Project indicated in the settings.  Depending on the setting for 
HermitCrab synthesis, the output file will either be in STAMP format or in a format suitable for the HermitCrab 
synthesis program. 
The output file will be stored in different files depending on whether you are doing STAMP synthesis (default) or
HermitCrab synthesis. For STAMP, the file is what you specified by the Target Output ANA File setting -- typically
called target_text-ana.txt.
For HermitCrab, the file is what you specified by the Hermit Crab Master File setting -- typically called 
target_words-HC.txt. Both files are usually in the Build folder.
NOTE: messages and the task bar will show the source project as being used. Actually the target project 
is being used.</source>
      <translation>Dieses Modul nimmt die von {runApert} erstellte Datei „Target Transfer Results File" und konvertiert sie in ein für die Synthese geeignetes Format, wobei Informationen aus dem in den Einstellungen angegebenen Zielprojekt verwendet werden. Abhängig von der Einstellung für HermitCrab-Synthese wird die Ausgabedatei entweder im STAMP-Format oder in einem für das HermitCrab-Syntheseprogramm geeigneten Format erstellt.
Die Ausgabedatei wird in verschiedenen Dateien gespeichert, je nachdem, ob Sie eine STAMP-Synthese (Standard) oder eine HermitCrab-Synthese durchführen. Für STAMP ist die Datei die, die Sie in der Einstellung „Target Output ANA File" angegeben haben – typischerweise target_text-ana.txt.
Für HermitCrab ist die Datei die, die Sie in der Einstellung „Hermit Crab Master File" angegeben haben – typischerweise target_words-HC.txt. Beide Dateien befinden sich normalerweise im Build-Ordner.
HINWEIS: Die Meldungen und die Taskleiste zeigen das Quellprojekt als verwendet an. Tatsächlich wird jedoch das Zielprojekt verwendet.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="443"/>
      <source>Configuration file problem with {fileType}.</source>
      <translation>Problem mit der Konfigurationsdatei für {fileType}.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="434"/>
      <source>Lexicon files folder: {fileType} does not exist.</source>
      <translation>Lexikon-Dateien-Ordner: {fileType} existiert nicht.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="463"/>
      <source>Failed to open the target project.</source>
      <translation>Öffnen des Zielprojekts fehlgeschlagen.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1167"/>
      <source>The file: {fileName} was not found. Did you run the {runApert} module?</source>
      <translation>Die Datei: {fileName} wurde nicht gefunden. Haben Sie das Modul {runApert} ausgeführt?</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1253"/>
      <source>Lemma or grammatical category missing for a target word near word {wordNum}. Found only: {morphs}. The preceding two words were: {prevWords}. The following two words were: {follWords}. Processing stopped.</source>
      <translation>Lemma oder grammatische Kategorie fehlt für ein Zielwort in der Nähe von Wort {wordNum}. Gefunden wurde nur: {morphs}. 
Die beiden vorhergehenden Wörter waren: {prevWords}. Die beiden folgenden Wörter waren: {follWords}. Verarbeitung gestoppt.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1330"/>
      <source>Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct</source>
      <translation>Problem mit der Konfigurationsdatei für targetANAFile, affixFile, transferResultsFile oder sentPunct</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1341"/>
      <source>Configuration file problem with: {property}.</source>
      <translation>Problem mit der Konfigurationsdatei für: {property}.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1391"/>
      <source>Error writing the output file.</source>
      <translation>Fehler beim Schreiben der Ausgabedatei.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1418"/>
      <source>Converted target words put in the file: {filePath}.</source>
      <translation>Konvertierte Zielwörter wurden in die Datei {filePath} geschrieben.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1419"/>
      <source>{count} records exported in ANA format.</source>
      <translation>{count} Datensätze im ANA-Format exportiert.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1421"/>
      <source>Converted target words put in the file: {filePath}</source>
      <translation>Konvertierte Zielwörter wurden in die Datei {filePath} geschrieben.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1422"/>
      <source>{count} records exported in HermitCrab format.</source>
      <translation>{count} Datensätze im HermitCrab-Format exportiert.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1441"/>
      <source>The Catalog Target Affixes module must be run before this module. The {fileType}: {filePath} does not exist.</source>
      <translation>Das Modul Catalog Target Affixes muss vor diesem Modul ausgeführt werden. Die Datei {fileType}: {filePath} existiert nicht.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1457"/>
      <source>Configuration file problem with: {fileType}.</source>
      <translation>Problem mit der Konfigurationsdatei für: {fileType}.</translation>
    </message>
</context>
</TS>