<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>GenerateParses</name>
    <message>
        <location filename="../GenerateParses.py" line="94"/>
        <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
        <translation>Crea todos los análisis posibles de un proyecto FLEx en formato Apertium.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="96"/>
        <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</source>
        <translation>Este módulo crea un archivo Apertium (que puede convertirse para la entrada a un proceso de sintetizador) con
todos los análisis que se pueden generar a partir del proyecto FLEx objetivo, basándose en sus plantillas de flexión.
(No genera basándose en información de derivación en el proyecto y aún no maneja
clíticos o variantes.)
En FLExTrans &gt; Configuración, en la configuración de Prueba de Síntesis, es posible limitar la salida a
un solo POS o Forma de Citación, o a un número especificado de raíces (las raíces se elegirán
aleatoriamente). Este módulo también genera una versión legible por humanos de los análisis (con glosas de raíces
y afijos) en el archivo de salida de análisis especificado en la configuración.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="159"/>
        <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
        <translation>No se encontraron etiquetas para el slot {slotName} de la plantilla {templateName}. Omitiendo.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="233"/>
        <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
        <translation>  No se agrega la plantilla inactiva {templateName} para la categoría {categoryAbbrev}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="237"/>
        <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
        <translation>  Agregando plantilla {templateName} para la categoría {categoryAbbrev}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="301"/>
        <source>Logging to {logFile}</source>
        <translation>Registrando en {logFile}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="303"/>
        <source>There was a problem creating the log file: {logFile}.</source>
        <translation>Hubo un problema al crear el archivo de registro: {logFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="308"/>
        <source>  No focus POS. Please select at least one POS with a template.</source>
        <translation>  Sin POS de enfoque. Por favor, seleccione al menos un POS con una plantilla.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="314"/>
        <source>  Only collecting templates for these POS: {focusPOS}</source>
        <translation>  Solo recopilando plantillas para estos POS: {focusPOS}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="318"/>
        <source>Collecting templates from FLEx project...</source>
        <translation>Recopilando plantillas del proyecto FLEx...</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="329"/>
        <source>  Not limiting number of stems</source>
        <translation>  No limitando el número de raíces</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="332"/>
        <source>  Only generating on the first {maxStems} stems</source>
        <translation>  Solo generando en las primeras {maxStems} raíces</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="337"/>
        <source>Processing entries</source>
        <translation>Procesando entradas</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="367"/>
        <source>  Only generating on stem [{lex}]
</source>
        <translation>  Solo generando en la raíz [{lex}]
</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="377"/>
        <source>  Skipping Variant with {count} Senses: {lex}</source>
        <translation>  Omitiendo variante con {count} sentidos: {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="410"/>
        <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
        <translation>  Agregando [{thisGloss}]{lex}&lt;{pos}&gt; a la lista de raíces</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="414"/>
        <source>Using NoGloss as the gloss for {lex}.</source>
        <translation>Usando NoGloss como la glosa para {lex}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="435"/>
        <source>Skipping deriv MSA for {lex}</source>
        <translation>Omitiendo deriv MSA para {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="489"/>
        <source>MSA missing POS in {lexForm} {lex}</source>
        <translation>MSA falta POS en {lexForm} {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="492"/>
        <source>POS msaPOS missing Abbreviation label</source>
        <translation>POS msaPOS falta etiqueta de abreviatura</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="497"/>
        <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
        <translation>      Agregando afijo {lexForm} {lex} al slot [{slotName}]</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="501"/>
        <source>Morph type {morphType} ignored.</source>
        <translation>Tipo de morfema {morphType} ignorado.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="508"/>
        <source>Finished collecting templates. Now generating words.</source>
        <translation>Finalizada la recopilación de plantillas. Ahora generando palabras.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="525"/>
        <source>There was a problem creating the Apertium file: {aperFile}.</source>
        <translation>Hubo un problema al crear el archivo Apertium: {aperFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="533"/>
        <source>There was a problem creating the words file: {outFile}.</source>
        <translation>Hubo un problema al crear el archivo de palabras: {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="561"/>
        <source>{wrdcnt} words generated.</source>
        <translation>{wrdcnt} palabras generadas.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="564"/>
        <source>Creation complete to the file: {outFile}.</source>
        <translation>Creación completada en el archivo: {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="565"/>
        <source>{wrdCount} words generated.</source>
        <translation>{wrdCount} palabras generadas.</translation>
    </message>
</context>
</TS>
