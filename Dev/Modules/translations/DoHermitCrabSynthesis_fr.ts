<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="148"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="151"/>
        <source>Synthesizes the target text with the tool HermitCrab.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="153"/>
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
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="205"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="216"/>
        <source>Failed to open the target project: {targetProj}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="225"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="256"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="248"/>
        <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="298"/>
        <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="264"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="274"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="303"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="281"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="282"/>
        <source>The full error message is:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="293"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="333"/>
        <source>There was an error opening the HermitCrab surface forms file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="342"/>
        <source>The file: {transferResultsFile} was not found. Did you run the {runApertium} module?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="357"/>
        <source>The number of surface forms does not match the number of Lexical Units.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="387"/>
        <source>Synthesis failed. ({saveStr})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="411"/>
        <source>Error writing the file: {synFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="428"/>
        <source>There was an error opening the HermitCrab master file. Do you have the setting &quot;Use HermitCrab Synthesis&quot; turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="437"/>
        <source>There was an error opening the HermitCrab parses file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="452"/>
        <source>Malformed Lexical Unit in HermitCrab master file skipping this line: {line}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="648"/>
        <source>Unable to open the HC master file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="674"/>
        <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="679"/>
        <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="685"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="690"/>
        <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="710"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="723"/>
        <source>An error happened when trying to open the file: {parsesFile}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="726"/>
        <source>Processing {LUsCount} unique lexical units.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="741"/>
        <source>Configuration file problem with the value: {val}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="756"/>
        <source>The synthesized target text is in the file: {file}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="757"/>
        <source>Synthesis complete.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="795"/>
        <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
