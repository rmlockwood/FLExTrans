<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en">
  <context>
    <name>GenerateParses</name>
    <message>
      <location filename="../GenerateParses.py" line="103"/>
      <source>Generate All Parses</source>
      <translation type="unfinished">Generate All Parses</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="106"/>
      <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
      <translation type="unfinished">Creates all possible parses from a FLEx project, in Apertium format.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="108"/>
      <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</source>
      <translation type="unfinished">This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="171"/>
      <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
      <translation type="unfinished">No tags found for slot {slotName} of template {templateName}. Skipping.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="245"/>
      <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
      <translation type="unfinished">  Not adding Inactive template {templateName} for Category {categoryAbbrev}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="249"/>
      <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
      <translation type="unfinished">  Adding template {templateName} for Category {categoryAbbrev}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="317"/>
      <source>Logging to {logFile}</source>
      <translation type="unfinished">Logging to {logFile}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="319"/>
      <source>There was a problem creating the log file: {logFile}.</source>
      <translation type="unfinished">There was a problem creating the log file: {logFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="324"/>
      <source>  No focus POS. Please select at least one POS with a template.</source>
      <translation type="unfinished">  No focus POS. Please select at least one POS with a template.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="330"/>
      <source>  Only collecting templates for these POS: {focusPOS}</source>
      <translation type="unfinished">  Only collecting templates for these POS: {focusPOS}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="334"/>
      <source>Collecting templates from FLEx project...</source>
      <translation type="unfinished">Collecting templates from FLEx project...</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="345"/>
      <source>  Not limiting number of stems</source>
      <translation type="unfinished">  Not limiting number of stems</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="348"/>
      <source>  Only generating on the first {maxStems} stems</source>
      <translation type="unfinished">  Only generating on the first {maxStems} stems</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="353"/>
      <source>Processing entries</source>
      <translation type="unfinished">Processing entries</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="383"/>
      <source>  Only generating on stem [{lex}]
</source>
      <translation type="unfinished">  Only generating on stem [{lex}]
</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="393"/>
      <source>  Skipping Variant with {count} Senses: {lex}</source>
      <translation type="unfinished">  Skipping Variant with {count} Senses: {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="426"/>
      <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
      <translation type="unfinished">  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="430"/>
      <source>Using NoGloss as the gloss for {lex}.</source>
      <translation type="unfinished">Using NoGloss as the gloss for {lex}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="451"/>
      <source>Skipping deriv MSA for {lex}</source>
      <translation type="unfinished">Skipping deriv MSA for {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="505"/>
      <source>MSA missing POS in {lexForm} {lex}</source>
      <translation type="unfinished">MSA missing POS in {lexForm} {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="508"/>
      <source>POS msaPOS missing Abbreviation label</source>
      <translation type="unfinished">POS msaPOS missing Abbreviation label</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="513"/>
      <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
      <translation type="unfinished">      Adding affix {lexForm} {lex} to slot [{slotName}]</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="517"/>
      <source>Morph type {morphType} ignored.</source>
      <translation type="unfinished">Morph type {morphType} ignored.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="524"/>
      <source>Finished collecting templates. Now generating words.</source>
      <translation type="unfinished">Finished collecting templates. Now generating words.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="541"/>
      <source>There was a problem creating the Apertium file: {aperFile}.</source>
      <translation type="unfinished">There was a problem creating the Apertium file: {aperFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="549"/>
      <source>There was a problem creating the words file: {outFile}.</source>
      <translation type="unfinished">There was a problem creating the words file: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="577"/>
      <source>{wrdcnt} words generated.</source>
      <translation type="unfinished">{wrdcnt} words generated.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="580"/>
      <source>Creation complete to the file: {outFile}.</source>
      <translation type="unfinished">Creation complete to the file: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="581"/>
      <source>{wrdCount} words generated.</source>
      <translation type="unfinished">{wrdCount} words generated.</translation>
    </message>
  </context>
</TS>
