<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en">
  <context>
    <name>ExtractSourceText</name>
    <message>
      <location filename="../ExtractSourceText.py" line="98"/>
      <source>Extract Source Text</source>
      <translation>Extract Source Text</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="101"/>
      <source>Exports an Analyzed FLEx text into Apertium format.</source>
      <translation>Exports an Analyzed FLEx text into Apertium format.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="103"/>
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
      <translation>This module will use the Source Text Name set in the Settings. It will first check 
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
This is typically called source_text-aper.txt and is usually in the Build folder.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="272"/>
      <source>There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.</source>
      <translation>There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="288"/>
      <source>The text named: {textName} not found.</source>
      <translation>The text named: {textName} not found.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="321"/>
      <source>There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.</source>
      <translation>There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="369"/>
      <source>Sentence {sentNum} from TreeTran not found</source>
      <translation>Sentence {sentNum} from TreeTran not found</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="390"/>
      <source>Null Guid in sentence {sentNum}, word {wordNum}</source>
      <translation>Null Guid in sentence {sentNum}, word {wordNum}</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="398"/>
      <source>Could not find the desired Guid in sentence {sentNum}, word {wordNum}</source>
      <translation>Could not find the desired Guid in sentence {sentNum}, word {wordNum}</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="455"/>
      <source>Sentence: {sentNum} not found. Check that the right parses are present.</source>
      <translation>Sentence: {sentNum} not found. Check that the right parses are present.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="463"/>
      <source>Exported: {count} sentence(s) using TreeTran results.</source>
      <translation>Exported: {count} sentence(s) using TreeTran results.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="466"/>
      <source>No parses found for {count} sentence(s).</source>
      <translation>No parses found for {count} sentence(s).</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="473"/>
      <source>Exported {count} sentence(s) to {path}.</source>
      <translation>Exported {count} sentence(s) to {path}.</translation>
    </message>
    <message>
      <location filename="../ExtractSourceText.py" line="477"/>
      <source>Export of {textName} complete.</source>
      <translation>Export of {textName} complete.</translation>
    </message>
  </context>
</TS>
