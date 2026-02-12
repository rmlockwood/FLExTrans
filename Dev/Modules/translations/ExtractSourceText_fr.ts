<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractSourceText</name>
    <message>
        <location filename="../ExtractSourceText.py" line="95"/>
        <source>Extract Source Text</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="98"/>
        <source>Exports an Analyzed FLEx text into Apertium format.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="100"/>
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
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="269"/>
        <source>There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="285"/>
        <source>The text named: {textName} not found.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="318"/>
        <source>There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="366"/>
        <source>Sentence {sentNum} from TreeTran not found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="387"/>
        <source>Null Guid in sentence {sentNum}, word {wordNum}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="395"/>
        <source>Could not find the desired Guid in sentence {sentNum}, word {wordNum}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="452"/>
        <source>Sentence: {sentNum} not found. Check that the right parses are present.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="460"/>
        <source>Exported: {count} sentence(s) using TreeTran results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="463"/>
        <source>No parses found for {count} sentence(s).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="470"/>
        <source>Exported {count} sentence(s) to {path}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="474"/>
        <source>Export of {textName} complete.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
