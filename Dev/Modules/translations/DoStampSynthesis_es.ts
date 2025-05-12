<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoStampSynthesis</name>
    <message>
        <location filename="../DoStampSynthesis.py" line="142"/>
        <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the SOURCE database is being used. Actually the target database is being used.</source>
        <translation>Este módulo ejecuta STAMP para crear el texto sintetizado. 
Antes de crear el texto sintetizado, este módulo extrae los archivos de léxico del idioma objetivo, uno para 
raíces, prefijos, sufijos e infijos. Están en el formato STAMP para la síntesis. Los archivos de léxico 
se colocan en la carpeta designada en la configuración como Carpeta de Archivos de Léxico de Destino. Normalmente, esta es la carpeta &apos;Build&apos;. 
El texto sintetizado se almacenará en el archivo especificado por la configuración Archivo de Síntesis de Salida de Destino. 
Este archivo se llama típicamente target_text-syn.txt y generalmente está en la carpeta &apos;Output&apos;. 
NOTA: Los mensajes indicarán que se está utilizando la base de datos FUENTE. En realidad, se está utilizando la base de datos de destino.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="154"/>
        <source>Synthesizes the target text with the tool STAMP.</source>
        <translation>Sintetiza el texto objetivo con la herramienta STAMP.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="742"/>
        <source>Null grapheme found for natural class: {natClassName}. Skipping.</source>
        <translation>Se encontró un grafema nulo para la clase natural: {natClassName}. Omitiendo.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="770"/>
        <source>Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.</source>
        <translation>Omitiendo el sentido porque la forma del lexema es desconocida: mientras se procesa la palabra principal objetivo: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="778"/>
        <source>Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.</source>
        <translation>Omitiendo el sentido porque el tipo de morfema es desconocido: mientras se procesa la palabra principal objetivo: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="853"/>
        <source>Skipping sense because the POS is unknown: while processing target headword: {headword}.</source>
        <translation>Omitiendo el sentido porque la categoría gramatical (POS) es desconocida: mientras se procesa la palabra principal objetivo: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="856"/>
        <source>Skipping sense that is of class: {className} for headword: {headword}.</source>
        <translation>Omitiendo el sentido que pertenece a la clase: {className} para la palabra principal: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="859"/>
        <source>Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.</source>
        <translation>Omitiendo el sentido que no tiene análisis morfosintáctico. Palabra principal: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="877"/>
        <source>No gloss. Skipping. Headword: {headword}.</source>
        <translation>Sin glosa. Omitiendo. Palabra principal: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="881"/>
        <source>No lexeme form. Skipping. Headword: {headword}.</source>
        <translation>Sin forma de lexema. Omitiendo. Palabra principal: {headword}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="885"/>
        <source>No Morph Type. Skipping. {headword} Best Vern: {vernacular}.</source>
        <translation>Sin tipo de morfema. Omitiendo. {headword} Mejor Vernáculo: {vernacular}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="895"/>
        <source>Skipping entry since the lexeme is of type: {className}.</source>
        <translation>Omitiendo la entrada ya que el lexema es del tipo: {className}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="981"/>
        <source>Skipping entry because the morph type is: {morphType}.</source>
        <translation>Omitiendo la entrada porque el tipo de morfema es: {morphType}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="917"/>
        <source>STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.</source>
        <translation>Diccionarios STAMP creados. {roots} raíces, {prefixes} prefijos, {suffixes} sufijos y {infixes} infijos.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1110"/>
        <source>Configuration file problem.</source>
        <translation>Problema con el archivo de configuración.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="996"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problema con el archivo de configuración para TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1125"/>
        <source>Configuration file problem with {folder}.</source>
        <translation>Problema con el archivo de configuración para {folder}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1007"/>
        <source>Lexicon files folder: {folder} does not exist.</source>
        <translation>La carpeta de archivos de léxico: {folder} no existe.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1016"/>
        <source>Configuration file problem with {cacheData}.</source>
        <translation>Problema con el archivo de configuración para {cacheData}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1023"/>
        <source>The Target Database does not exist. Please check the configuration file.</source>
        <translation>La base de datos de destino no existe. Por favor, revise el archivo de configuración.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1028"/>
        <source>Problem accessing the target project.</source>
        <translation>Problema al acceder al proyecto de destino.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1033"/>
        <source>Failed to open the target database.</source>
        <translation>No se pudo abrir la base de datos de destino.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1039"/>
        <source>Target lexicon files are up to date.</source>
        <translation>Los archivos de léxico de destino están actualizados.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1147"/>
        <source>The synthesized target text is in the file: {filePath}.</source>
        <translation>El texto objetivo sintetizado está en el archivo: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1148"/>
        <source>Synthesis complete.</source>
        <translation>Síntesis completa.</translation>
    </message>
    <message>
        <location filename="../DoStampSynthesis.py" line="1171"/>
        <source>The Convert Text to STAMP Format module must be run before this module. The {fileType}: {filePath} does not exist.</source>
        <translation>El módulo Convertir Texto al Formato STAMP debe ejecutarse antes de este módulo. El archivo {fileType}: {filePath} no existe.</translation>
    </message>
</context>
</TS>