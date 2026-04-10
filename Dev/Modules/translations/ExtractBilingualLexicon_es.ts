<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es-ES" sourcelanguage="en">
  <context>
    <name>ExtractBilingualLexicon</name>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="141"/>
      <source>Build Bilingual Lexicon</source>
      <translation>Build Bilingual Lexicon</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="144"/>
      <source>Builds an Apertium-style bilingual lexicon.</source>
      <translation>Builds an Apertium-style bilingual lexicon.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="146"/>
      <source>This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.

You can make custom changes to the bilingual lexicon by using the {replEditorModule}. See the help
document for more details.</source>
      <translation>This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.

You can make custom changes to the bilingual lexicon by using the {replEditorModule}. See the help
document for more details.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="273"/>
      <source>Custom field for linking doesn&apos;t exist. Please read the instructions.</source>
      <translation>Custom field for linking doesn&apos;t exist. Please read the instructions.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="276"/>
      <source>No Source Morphnames to count as root found. Review your Settings.</source>
      <translation>No Source Morphnames to count as root found. Review your Settings.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="279"/>
      <source>No Sentence Punctuation found. Review your Settings.</source>
      <translation>No Sentence Punctuation found. Review your Settings.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="289"/>
      <source>Ill-formed property: &quot;CategoryAbbrevSubstitutionList&quot;. Expected pairs of categories.</source>
      <translation>Ill-formed property: &quot;CategoryAbbrevSubstitutionList&quot;. Expected pairs of categories.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="299"/>
      <source>Custom field: {linkField} doesn&apos;t exist. Please read the instructions.</source>
      <translation>Custom field: {linkField} doesn&apos;t exist. Please read the instructions.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="321"/>
      <source>A value for {key} not found in the configuration file.</source>
      <translation>A value for {key} not found in the configuration file.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="333"/>
      <source>The bilingual dictionary is up to date.</source>
      <translation>The bilingual dictionary is up to date.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="352"/>
      <source>Error retrieving categories.</source>
      <translation>Error retrieving categories.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="388"/>
      <source>Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.</source>
      <translation>Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="391"/>
      <source>Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.</source>
      <translation>Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="418"/>
      <source>Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}</source>
      <translation>Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="425"/>
      <source>Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}</source>
      <translation>Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="476"/>
      <source>Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
      <translation>Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="478"/>
      <source>Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
      <translation>Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="486"/>
      <source>Skipping sense that is of class: {className} for headword: {rawHeadWord}</source>
      <translation>Skipping sense that is of class: {className} for headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="488"/>
      <source>Skipping sense, no analysis object for headword: {rawHeadWord}</source>
      <translation>Skipping sense, no analysis object for headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="511"/>
      <source>No lexeme form. Skipping. Headword: {rawHeadWord}</source>
      <translation>No lexeme form. Skipping. Headword: {rawHeadWord}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="520"/>
      <source>No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}</source>
      <translation>No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="546"/>
      <source>There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.</source>
      <translation>There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="573"/>
      <source>There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.</source>
      <translation>There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="577"/>
      <source>Creation complete to the file: {filePath}.</source>
      <translation>Creation complete to the file: {filePath}.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="578"/>
      <source>{recordsDumpedCount} records created.</source>
      <translation>{recordsDumpedCount} records created.</translation>
    </message>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="247"/>
      <source>Encountered a sense that has an invalid feature while processing source headword: {rawHeadWord}</source>
      <translation>Encountered a sense that has an invalid feature while processing source headword: {rawHeadWord}</translation>
    </message>
  </context>
</TS>
