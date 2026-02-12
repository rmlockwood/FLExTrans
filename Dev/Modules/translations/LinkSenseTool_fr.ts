<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>LinkSenseTool</name>
    <message>
        <location filename="../LinkSenseTool.py" line="198"/>
        <source>Sense Linker Tool</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="201"/>
        <source>Link source and target senses.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="203"/>
        <source>This module will create links 
in the source project to senses in the target project. It will show a window
with a list of all the senses in the text. White background rows indicate links that
already exist. blue background rows indicate suggested links based on an exact match
on gloss, light blue background rows indicate suggested links based on a close match on
gloss (currently 75% similar), red background rows
have no link yet established. Double-click on the Target Head Word column for a row to copy
the currently selected target sense in the upper combo box into that row. Click the checkbox
to create a link for that row. I.e. the source sense will be linked to the target sense.
Unchecking a checkbox for white row will unlink the specified sense from its target sense.
Close matches are only attempted for words with five letters or longer.
For suggested sense pairs where
there is a mismatch in the grammatical category, both categories are colored red. This
is to indicate you may not want to link the two sense even though the glosses match. 
This module requires
a sense-level custom field in your source project. It should be simple text field.
The purpose of the custom field is to hold the link to a sense in the target project.
Set which custom field is used for linking in the settings.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1144"/>
        <source>Save Changes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1144"/>
        <source>Do you want to save your changes?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1265"/>
        <source>Empty grammatical category found for the target word: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1289"/>
        <source>Empty gloss found for the target word: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1294"/>
        <source>More than {num_warnings} empty glosses found. Suppressing further warnings for empty target glosses.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1512"/>
        <source>No words with a valid root morph type were found. Please check the your settings, specifically Source Morpheme Types Counted As Roots.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1619"/>
        <source>1 link created.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1621"/>
        <source>{num} links created.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1625"/>
        <source>1 link removed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1629"/>
        <source>{num} links removed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1697"/>
        <source>Gloss</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1698"/>
        <source>Category</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1700"/>
        <source>Comment</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1799"/>
        <source>Permission error writing {htmlFileName}. Perhaps the file is in use in another program?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1803"/>
        <source>Error writing {htmlFileName}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1807"/>
        <source>{cnt} words written to the file: {htmlFileName}. You&apos;ll find it in the Output folder.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1810"/>
        <source>No unlinked words. Nothing exported.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1825"/>
        <source>No Source Text Name has been set. Please go to Settings and fix this.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1830"/>
        <source>No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1836"/>
        <source>No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1841"/>
        <source>No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1855"/>
        <source>The text named: {sourceTextName} not found.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1872"/>
        <source>{linkField} field doesn&apos;t exist. Please read the instructions.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1886"/>
        <source>The target project does not exist. Please check the configuration file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1889"/>
        <source>Opening: {targetProj} as the target project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1896"/>
        <source>Failed to open the target project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1899"/>
        <source>Starting {moduleName} for text: {sourceTextName}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1928"/>
        <source>There were no senses found for linking. Please check your text and approve some words.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1944"/>
        <source>There was an error finding senses to link.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1946"/>
        <source>Link it!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1948"/>
        <source>Source Head Word</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1949"/>
        <source>Source Category</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1950"/>
        <source>Source Gloss</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1951"/>
        <source>Target Head Word</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1952"/>
        <source>Target Category</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1953"/>
        <source>Target Gloss</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="2009"/>
        <source>You need to run this module in &quot;modify mode.&quot;</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
