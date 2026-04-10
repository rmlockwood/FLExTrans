<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en">
  <context>
    <name>GenerateParses</name>
    <message>
      <location filename="../GenerateParses.py" line="100"/>
      <source>Generate All Parses</source>
      <translation>Alle Analysen generieren</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="103"/>
      <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
      <translation>Erstellt alle möglichen Analysen aus einem FLEx-Projekt im Apertium-Format.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="105"/>
      <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn't generate based on derivation information in the project and it doesn't yet handle
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
      <location filename="../GenerateParses.py" line="168"/>
      <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
      <translation>Keine Tags für Slot {slotName} der Vorlage {templateName} gefunden. Überspringen.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="242"/>
      <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
      <translation>  Inaktive Vorlage {templateName} für Kategorie {categoryAbbrev} wird nicht hinzugefügt</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="246"/>
      <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
      <translation>  Vorlage {templateName} für Kategorie {categoryAbbrev} wird hinzugefügt</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="314"/>
      <source>Logging to {logFile}</source>
      <translation>Protokollierung in {logFile}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="316"/>
      <source>There was a problem creating the log file: {logFile}.</source>
      <translation>Es gab ein Problem beim Erstellen der Protokolldatei: {logFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="321"/>
      <source>  No focus POS. Please select at least one POS with a template.</source>
      <translation>  Kein Fokus-POS. Bitte wählen Sie mindestens eine POS mit einer Vorlage aus.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="327"/>
      <source>  Only collecting templates for these POS: {focusPOS}</source>
      <translation>  Vorlagen werden nur für diese POS gesammelt: {focusPOS}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="331"/>
      <source>Collecting templates from FLEx project...</source>
      <translation>Vorlagen aus dem FLEx-Projekt werden gesammelt...</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="342"/>
      <source>  Not limiting number of stems</source>
      <translation>  Anzahl der Stämme wird nicht begrenzt</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="345"/>
      <source>  Only generating on the first {maxStems} stems</source>
      <translation>  Generierung nur für die ersten {maxStems} Stämme</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="350"/>
      <source>Processing entries</source>
      <translation>Einträge werden verarbeitet</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="380"/>
      <source>  Only generating on stem [{lex}]
</source>
      <translation>  Generierung nur für Stamm [{lex}]
</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="390"/>
      <source>  Skipping Variant with {count} Senses: {lex}</source>
      <translation>  Variante mit {count} Bedeutungen wird übersprungen: {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="423"/>
      <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
      <translation>  [{thisGloss}]{lex}&lt;{pos}&gt; wird zur Wurzelliste hinzugefügt</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="427"/>
      <source>Using NoGloss as the gloss for {lex}.</source>
      <translation>Verwendung von NoGloss als Gloss für {lex}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="448"/>
      <source>Skipping deriv MSA for {lex}</source>
      <translation>Deriv-MSA für {lex} wird übersprungen</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="502"/>
      <source>MSA missing POS in {lexForm} {lex}</source>
      <translation>MSA fehlt POS in {lexForm} {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="505"/>
      <source>POS msaPOS missing Abbreviation label</source>
      <translation>POS msaPOS fehlt Abkürzungsbezeichnung</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="510"/>
      <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
      <translation>      Affix {lexForm} {lex} wird zu Slot [{slotName}] hinzugefügt</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="514"/>
      <source>Morph type {morphType} ignored.</source>
      <translation>Morphtyp {morphType} wird ignoriert.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="521"/>
      <source>Finished collecting templates. Now generating words.</source>
      <translation>Vorlagen wurden gesammelt. Jetzt werden Wörter generiert.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="538"/>
      <source>There was a problem creating the Apertium file: {aperFile}.</source>
      <translation>Es gab ein Problem beim Erstellen der Apertium-Datei: {aperFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="546"/>
      <source>There was a problem creating the words file: {outFile}.</source>
      <translation>Es gab ein Problem beim Erstellen der Wörterdatei: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="574"/>
      <source>{wrdcnt} words generated.</source>
      <translation>{wrdcnt} Wörter generiert.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="577"/>
      <source>Creation complete to the file: {outFile}.</source>
      <translation>Erstellung abgeschlossen in der Datei: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="578"/>
      <source>{wrdCount} words generated.</source>
      <translation>{wrdCount} Wörter generiert.</translation>
    </message>
  </context>
</TS>
