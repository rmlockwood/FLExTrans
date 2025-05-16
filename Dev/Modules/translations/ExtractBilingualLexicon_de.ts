<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractBilingualLexicon</name>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="176"/>
        <source>Builds an Apertium-style bilingual lexicon.</source>
        <translation>Erstellt ein zweisprachiges Lexikon im Apertium-Stil.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="178"/>
        <source>This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.

You can make custom changes to the bilingual lexicon by using Replacement Dictionary Editor. See the help
document for more details.
</source>
        <translation>Dieses Modul erstellt ein zweisprachiges Lexikon für zwei Projekte. Das Projekt, auf das FlexTools eingestellt ist, ist Ihr Quellprojekt. Legen Sie im Menü Einstellungen das Zielprojekt auf den Namen Ihres Zielprojekts fest.
Dieses Modul erstellt das zweisprachige Lexikon basierend auf den Verknüpfungen von Quellbedeutungen zu Zielbedeutungen, die sich in Ihrem Quellprojekt befinden. Verwenden Sie das Sense Linker-Modul, um diese Verknüpfungen zu erstellen.
Das zweisprachige Lexikon wird in der Datei gespeichert, die in der Einstellung "Bilingual Dictionary Output File" angegeben ist. Diese Datei wird typischerweise bilingual.dix genannt und befindet sich normalerweise im Ordner "Output".

Sie können benutzerdefinierte Änderungen am zweisprachigen Lexikon vornehmen, indem Sie den Replacement Dictionary Editor verwenden. Weitere Details finden Sie im Hilfedokument.
</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="298"/>
        <source>Custom field for linking doesn&apos;t exist. Please read the instructions.</source>
        <translation>Das benutzerdefinierte Feld für Verknüpfungen existiert nicht. Bitte lesen Sie die Anweisungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="301"/>
        <source>No Source Morphnames to count as root found. Review your Settings.</source>
        <translation>Keine Quell-Morphnamen gefunden, die als Wurzel gezählt werden können. Überprüfen Sie Ihre Einstellungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="304"/>
        <source>No Sentence Punctuation found. Review your Settings.</source>
        <translation>Keine Satzzeichen gefunden. Überprüfen Sie Ihre Einstellungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="313"/>
        <source>Ill-formed property: &quot;CategoryAbbrevSubstitutionList&quot;. Expected pairs of categories.</source>
        <translation>Fehlerhafte Eigenschaft: &quot;CategoryAbbrevSubstitutionList&quot;. Es werden Paare von Kategorien erwartet.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="323"/>
        <source>Custom field: {linkField} doesn&apos;t exist. Please read the instructions.</source>
        <translation>Benutzerdefiniertes Feld: {linkField} existiert nicht. Bitte lesen Sie die Anweisungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="342"/>
        <source>A value for {key} not found in the configuration file.</source>
        <translation>Ein Wert für {key} wurde in der Konfigurationsdatei nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="354"/>
        <source>The bilingual dictionary is up to date.</source>
        <translation>Das zweisprachige Wörterbuch ist auf dem neuesten Stand.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="372"/>
        <source>Error retrieving categories.</source>
        <translation>Fehler beim Abrufen der Kategorien.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="408"/>
        <source>Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.</source>
        <translation>Ein Stichwort mit vorangestellten oder nachgestellten Leerzeichen wurde gefunden, während das Quellstichwort verarbeitet wurde: {rawHeadWord}. Die Leerzeichen wurden entfernt, aber bitte korrigieren Sie dies im Lexikon.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="411"/>
        <source>Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.</source>
        <translation>Ein Stichwort mit einem der folgenden ungültigen Zeichen wurde gefunden: {chars} in {rawHeadWord}. Bitte korrigieren Sie dies im Lexikon, bevor Sie fortfahren.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="438"/>
        <source>Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}</source>
        <translation>Eine Bedeutung mit unbekannter Wortart wurde gefunden, während das Quellstichwort verarbeitet wurde: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="445"/>
        <source>Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}</source>
        <translation>Ein Stichwort wurde gefunden, das sich nur in der Groß-/Kleinschreibung von einem anderen Stichwort mit derselben Wortart ({sourcePOSabbrev}) unterscheidet. Diese Bedeutung wird übersprungen. Quellstichwort: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="496"/>
        <source>Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Bedeutung wird übersprungen, da die Ziel-Wortart für das Zielstichwort nicht definiert ist: {targetHeadWord}, während das Quellstichwort verarbeitet wurde: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="498"/>
        <source>Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Bedeutung wird übersprungen, da sie dieser Klasse angehört: {className} für das Zielstichwort: {targetHeadWord}, während das Quellstichwort verarbeitet wurde: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="506"/>
        <source>Skipping sense that is of class: {className} for headword: {rawHeadWord}</source>
        <translation>Bedeutung wird übersprungen, da sie der Klasse {className} angehört, für das Stichwort: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="508"/>
        <source>Skipping sense, no analysis object for headword: {rawHeadWord}</source>
        <translation>Bedeutung wird übersprungen, da kein Analyseobjekt für das Stichwort vorhanden ist: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="531"/>
        <source>No lexeme form. Skipping. Headword: {rawHeadWord}</source>
        <translation>Keine Lexemform. Überspringen. Stichwort: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="540"/>
        <source>No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}</source>
        <translation>Kein Morph-Typ. Überspringen. {rawHeadWord} Beste Vern: {vernString}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="566"/>
        <source>There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.</source>
        <translation>Es gibt ein Problem mit der Ersatzdatei des zweisprachigen Wörterbuchs: {replFile}. Bitte überprüfen Sie die Konfigurationseinstellungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="593"/>
        <source>There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.</source>
        <translation>Es gab ein Problem beim Erstellen der Ausgabedatei des zweisprachigen Wörterbuchs: {fullPathBilingFile}. Bitte überprüfen Sie die Konfigurationseinstellungen.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="597"/>
        <source>Creation complete to the file: {filePath}.</source>
        <translation>Erstellung abgeschlossen in der Datei: {filePath}.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="598"/>
        <source>{recordsDumpedCount} records created.</source>
        <translation>{recordsDumpedCount} Einträge erstellt.</translation>
    </message>
</context>
</TS>