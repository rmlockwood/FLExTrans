<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>GenerateParses</name>
    <message>
        <location filename="../GenerateParses.py" line="100"/>
        <source>Generate All Parses</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="103"/>
        <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="105"/>
        <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="168"/>
        <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="242"/>
        <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="246"/>
        <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="314"/>
        <source>Logging to {logFile}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="316"/>
        <source>There was a problem creating the log file: {logFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="321"/>
        <source>  No focus POS. Please select at least one POS with a template.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="327"/>
        <source>  Only collecting templates for these POS: {focusPOS}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="331"/>
        <source>Collecting templates from FLEx project...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="342"/>
        <source>  Not limiting number of stems</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="345"/>
        <source>  Only generating on the first {maxStems} stems</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="350"/>
        <source>Processing entries</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="380"/>
        <source>  Only generating on stem [{lex}]
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="390"/>
        <source>  Skipping Variant with {count} Senses: {lex}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="423"/>
        <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="427"/>
        <source>Using NoGloss as the gloss for {lex}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="448"/>
        <source>Skipping deriv MSA for {lex}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="502"/>
        <source>MSA missing POS in {lexForm} {lex}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="505"/>
        <source>POS msaPOS missing Abbreviation label</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="510"/>
        <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="514"/>
        <source>Morph type {morphType} ignored.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="521"/>
        <source>Finished collecting templates. Now generating words.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="538"/>
        <source>There was a problem creating the Apertium file: {aperFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="546"/>
        <source>There was a problem creating the words file: {outFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="574"/>
        <source>{wrdcnt} words generated.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="577"/>
        <source>Creation complete to the file: {outFile}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="578"/>
        <source>{wrdCount} words generated.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
