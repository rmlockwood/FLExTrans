<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>GenerateParses</name>
    <message>
      <location filename="../GenerateParses.py" line="118"/>
      <source>Generate All Parses</source>
      <translation>Alle Analysen generieren</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="94"/>
        <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
        <translation>Erstellt alle möglichen Analysen aus einem FLEx-Projekt im Apertium-Format.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="96"/>
        <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</source>
        <translation>Dieses Modul erstellt eine Apertium-Datei (die für die Eingabe in einen Synthesizer-Prozess konvertiert werden kann) mit
allen Analysen, die aus dem Ziel-FLEx-Projekt basierend auf seinen Flexionsvorlagen generiert werden können.
(Es generiert nicht basierend auf Ableitungsinformationen im Projekt und behandelt noch keine
Klitika oder Varianten.)
In FLExTrans &gt; Einstellungen, unter Synthesis-Testeinstellungen, ist es möglich, die Ausgabe auf
eine einzelne POS oder Zitatform oder auf eine bestimmte Anzahl von Stämmen zu beschränken (Stämme werden zufällig ausgewählt).
Dieses Modul gibt auch eine menschenlesbare Version der Analysen (mit Glossen von Wurzeln
und Affixen) in die in den Einstellungen angegebene Parses-Ausgabedatei aus.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="159"/>
        <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
        <translation>Keine Tags für Slot {slotName} der Vorlage {templateName} gefunden. Überspringen.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="233"/>
        <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
        <translation>  Inaktive Vorlage {templateName} für Kategorie {categoryAbbrev} wird nicht hinzugefügt</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="237"/>
        <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
        <translation>  Vorlage {templateName} für Kategorie {categoryAbbrev} wird hinzugefügt</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="301"/>
        <source>Logging to {logFile}</source>
        <translation>Protokollierung in {logFile}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="303"/>
        <source>There was a problem creating the log file: {logFile}.</source>
        <translation>Es gab ein Problem beim Erstellen der Protokolldatei: {logFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="308"/>
        <source>  No focus POS. Please select at least one POS with a template.</source>
        <translation>  Kein Fokus-POS. Bitte wählen Sie mindestens eine POS mit einer Vorlage aus.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="314"/>
        <source>  Only collecting templates for these POS: {focusPOS}</source>
        <translation>  Vorlagen werden nur für diese POS gesammelt: {focusPOS}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="318"/>
        <source>Collecting templates from FLEx project...</source>
        <translation>Vorlagen aus dem FLEx-Projekt werden gesammelt...</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="329"/>
        <source>  Not limiting number of stems</source>
        <translation>  Anzahl der Stämme wird nicht begrenzt</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="332"/>
        <source>  Only generating on the first {maxStems} stems</source>
        <translation>  Generierung nur für die ersten {maxStems} Stämme</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="337"/>
        <source>Processing entries</source>
        <translation>Einträge werden verarbeitet</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="367"/>
        <source>  Only generating on stem [{lex}]
</source>
        <translation>  Generierung nur für Stamm [{lex}]
</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="377"/>
        <source>  Skipping Variant with {count} Senses: {lex}</source>
        <translation>  Variante mit {count} Bedeutungen wird übersprungen: {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="410"/>
        <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
        <translation>  [{thisGloss}]{lex}&lt;{pos}&gt; wird zur Wurzelliste hinzugefügt</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="414"/>
        <source>Using NoGloss as the gloss for {lex}.</source>
        <translation>Verwendung von NoGloss als Gloss für {lex}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="435"/>
        <source>Skipping deriv MSA for {lex}</source>
        <translation>Deriv-MSA für {lex} wird übersprungen</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="489"/>
        <source>MSA missing POS in {lexForm} {lex}</source>
        <translation>MSA fehlt POS in {lexForm} {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="492"/>
        <source>POS msaPOS missing Abbreviation label</source>
        <translation>POS msaPOS fehlt Abkürzungsbezeichnung</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="497"/>
        <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
        <translation>      Affix {lexForm} {lex} wird zu Slot [{slotName}] hinzugefügt</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="501"/>
        <source>Morph type {morphType} ignored.</source>
        <translation>Morphtyp {morphType} wird ignoriert.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="508"/>
        <source>Finished collecting templates. Now generating words.</source>
        <translation>Vorlagen wurden gesammelt. Jetzt werden Wörter generiert.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="525"/>
        <source>There was a problem creating the Apertium file: {aperFile}.</source>
        <translation>Es gab ein Problem beim Erstellen der Apertium-Datei: {aperFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="533"/>
        <source>There was a problem creating the words file: {outFile}.</source>
        <translation>Es gab ein Problem beim Erstellen der Wörterdatei: {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="561"/>
        <source>{wrdcnt} words generated.</source>
        <translation>{wrdcnt} Wörter generiert.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="564"/>
        <source>Creation complete to the file: {outFile}.</source>
        <translation>Erstellung abgeschlossen in der Datei: {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="565"/>
        <source>{wrdCount} words generated.</source>
        <translation>{wrdCount} Wörter generiert.</translation>
    </message>
</context>
</TS>
