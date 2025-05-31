<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractSourceText</name>
    <message>
      <location filename="../ExtractSourceText.py" line="97"/>
      <source>Builds an Apertium-style bilingual lexicon.</source>
      <translation>Erstellt ein zweisprachiges Lexikon im Apertium-Stil.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="99"/>
      <source>This module will use the Source Text Name set in the Settings. It will first check 
to see if each word in the selected text is
fully analyzed (word gloss or category is not necessary). If the text is not
fully analyzed you will get warnings.
Next, this module will go through each bundle in the interlinear text and export
information in the format that Apertium needs. The general idea is that
affixes and clitics will be exported as &lt;gloss&gt; and root/stems will be exported
as head_word&lt;pos&gt;&lt;feat1&gt;...&lt;featN&gt;&lt;class1&gt;...&lt;classN&gt;. Where feat1 to featN are one or more 
inflection features that may be present for the root/stem 
and class1 to classN are inflection classes that may be present on the stem.
The exported sentences will be stored in the file specified by the Analyzed Text Output File setting.
This is typically called source_text-aper.txt and is usually in the Build folder.</source>
      <translation>Dieses Modul verwendet den im Menü Einstellungen festgelegten Namen des Quelltextes. Es wird zunächst überprüft, ob jedes Wort im ausgewählten Text vollständig analysiert ist (Wortglossar oder Kategorie sind nicht erforderlich). Wenn der Text nicht vollständig analysiert ist, erhalten Sie Warnungen. Anschließend wird dieses Modul jedes Bündel im interlinearen Text durchgehen und Informationen im von Apertium benötigten Format exportieren. Die allgemeine Idee ist, dass Affixe und Klitika als &lt;gloss&gt; exportiert werden und Wurzeln/Stämme als head_word&lt;pos&gt;&lt;feat1&gt;...&lt;featN&gt;&lt;class1&gt;...&lt;classN&gt; exportiert werden. Dabei sind feat1 bis featN ein oder mehrere Flexionsmerkmale, die für die Wurzel/den Stamm vorhanden sein können, und class1 bis classN sind Flexionsklassen, die auf dem Stamm vorhanden sein können. Die exportierten Sätze werden in der Datei gespeichert, die in der Einstellung &quot;Analyzed Text Output File&quot; angegeben ist. Diese Datei wird typischerweise source_text-aper.txt genannt und befindet sich normalerweise im Build-Ordner.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="268"/>
      <source>There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.</source>
      <translation>Es gibt ein Problem mit dem Pfad der Datei für die analysierten Texte: {path}. Bitte überprüfen Sie die Konfigurationseinstellungen.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="283"/>
      <source>The text named: {textName} not found.</source>
      <translation>Der Text mit dem Namen: {textName} wurde nicht gefunden.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="315"/>
      <source>There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.</source>
      <translation>Es gibt ein Problem mit dem Pfad der Tree Tran-Ergebnisdatei: {path}. Bitte überprüfen Sie die Konfigurationseinstellungen.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="363"/>
      <source>Sentence {sentNum} from TreeTran not found</source>
      <translation>Satz {sentNum} aus TreeTran wurde nicht gefunden.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="384"/>
      <source>Null Guid in sentence {sentNum}, word {wordNum}</source>
      <translation>Null-GUID im Satz {sentNum}, Wort {wordNum}</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="392"/>
      <source>Could not find the desired Guid in sentence {sentNum}, word {wordNum}</source>
      <translation>Die gewünschte GUID konnte im Satz {sentNum}, Wort {wordNum} nicht gefunden werden.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="449"/>
      <source>Sentence: {sentNum} not found. Check that the right parses are present.</source>
      <translation>Satz: {sentNum} wurde nicht gefunden. Überprüfen Sie, ob die richtigen Analysen vorhanden sind.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="457"/>
      <source>Exported: {count} sentence(s) using TreeTran results.</source>
      <translation>Exportiert: {count} Satz/Sätze unter Verwendung der TreeTran-Ergebnisse.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="460"/>
      <source>No parses found for {count} sentence(s).</source>
      <translation>Keine Analysen für {count} Satz/Sätze gefunden.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="467"/>
      <source>Exported {count} sentence(s) to {path}.</source>
      <translation>{count} Satz/Sätze nach {path} exportiert.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="471"/>
      <source>Export of {textName} complete.</source>
      <translation>Export von {textName} abgeschlossen.</translation>
    </message>
  </context>
</TS>
