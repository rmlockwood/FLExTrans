<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es-ES" sourcelanguage="en">
  <context>
    <name>GenerateParses</name>
    <message>
      <location filename="../GenerateParses.py" line="100"/>
      <source>Generate All Parses</source>
      <translation>Generar todos los análisis</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="103"/>
      <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
      <translation>Crea todos los análisis posibles de un proyecto FLEx en formato Apertium.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="105"/>
      <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn't generate based on derivation information in the project and it doesn't yet handle
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
      <location filename="../GenerateParses.py" line="168"/>
      <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
      <translation>No se encontraron etiquetas para el slot {slotName} de la plantilla {templateName}. Omitiendo.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="242"/>
      <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
      <translation>  No se agrega la plantilla inactiva {templateName} para la categoría {categoryAbbrev}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="246"/>
      <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
      <translation>  Agregando plantilla {templateName} para la categoría {categoryAbbrev}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="314"/>
      <source>Logging to {logFile}</source>
      <translation>Registrando en {logFile}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="316"/>
      <source>There was a problem creating the log file: {logFile}.</source>
      <translation>Hubo un problema al crear el archivo de registro: {logFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="321"/>
      <source>  No focus POS. Please select at least one POS with a template.</source>
      <translation>  Sin POS de enfoque. Por favor, seleccione al menos un POS con una plantilla.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="327"/>
      <source>  Only collecting templates for these POS: {focusPOS}</source>
      <translation>  Solo recopilando plantillas para estos POS: {focusPOS}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="331"/>
      <source>Collecting templates from FLEx project...</source>
      <translation>Recopilando plantillas del proyecto FLEx...</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="342"/>
      <source>  Not limiting number of stems</source>
      <translation>  No limitando el número de raíces</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="345"/>
      <source>  Only generating on the first {maxStems} stems</source>
      <translation>  Solo generando en las primeras {maxStems} raíces</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="350"/>
      <source>Processing entries</source>
      <translation>Procesando entradas</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="380"/>
      <source>  Only generating on stem [{lex}]
</source>
      <translation>  Solo generando en la raíz [{lex}]
</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="390"/>
      <source>  Skipping Variant with {count} Senses: {lex}</source>
      <translation>  Omitiendo variante con {count} sentidos: {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="423"/>
      <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
      <translation>  Agregando [{thisGloss}]{lex}&lt;{pos}&gt; a la lista de raíces</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="427"/>
      <source>Using NoGloss as the gloss for {lex}.</source>
      <translation>Usando NoGloss como la glosa para {lex}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="448"/>
      <source>Skipping deriv MSA for {lex}</source>
      <translation>Omitiendo deriv MSA para {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="502"/>
      <source>MSA missing POS in {lexForm} {lex}</source>
      <translation>MSA falta POS en {lexForm} {lex}</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="505"/>
      <source>POS msaPOS missing Abbreviation label</source>
      <translation>POS msaPOS falta etiqueta de abreviatura</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="510"/>
      <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
      <translation>      Agregando afijo {lexForm} {lex} al slot [{slotName}]</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="514"/>
      <source>Morph type {morphType} ignored.</source>
      <translation>Tipo de morfema {morphType} ignorado.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="521"/>
      <source>Finished collecting templates. Now generating words.</source>
      <translation>Finalizada la recopilación de plantillas. Ahora generando palabras.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="538"/>
      <source>There was a problem creating the Apertium file: {aperFile}.</source>
      <translation>Hubo un problema al crear el archivo Apertium: {aperFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="546"/>
      <source>There was a problem creating the words file: {outFile}.</source>
      <translation>Hubo un problema al crear el archivo de palabras: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="574"/>
      <source>{wrdcnt} words generated.</source>
      <translation>{wrdcnt} palabras generadas.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="577"/>
      <source>Creation complete to the file: {outFile}.</source>
      <translation>Creación completada en el archivo: {outFile}.</translation>
    </message>
    <message>
      <location filename="../GenerateParses.py" line="578"/>
      <source>{wrdCount} words generated.</source>
      <translation>{wrdCount} palabras generadas.</translation>
    </message>
  </context>
</TS>
