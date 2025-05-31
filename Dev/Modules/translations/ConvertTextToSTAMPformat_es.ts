<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ConvertTextToSTAMPformat</name>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="171"/>
      <source>Convert the file produced by Run Apertium into a text file in a Synthesizer format</source>
      <translation>Convierte el archivo producido por Run Apertium en un archivo de texto en formato de sintetizador</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="173"/>
      <source>This module will take the Target Transfer Results File created by Apertium and convert it to a format suitable 
for synthesis, using information from the Target Project indicated in the settings.  Depending on the setting for 
HermitCrab synthesis, the output file will either be in STAMP format or in a format suitable for the HermitCrab 
synthesis program. 
The output file will be stored in different files depending on whether you are doing STAMP synthesis (default) or
HermitCrab synthesis. For STAMP, the file is what you specified by the Target Output ANA File setting -- typically
called target_text-ana.txt.
For HermitCrab, the file is what you specified by the Hermit Crab Master File setting -- typically called 
target_words-HC.txt. Both files are usually in the Build folder.
NOTE: messages and the task bar will show the SOURCE database as being used. Actually the target database 
is being used.</source>
      <translation>Este módulo tomará el archivo de resultados de transferencia de destino creado por Apertium y lo convertirá en un formato adecuado 
para la síntesis, utilizando información del proyecto de destino indicado en la configuración. Dependiendo de la configuración para 
la síntesis de HermitCrab, el archivo de salida estará en formato STAMP o en un formato adecuado para el programa de síntesis HermitCrab. 
El archivo de salida se almacenará en diferentes archivos dependiendo de si está realizando una síntesis STAMP (predeterminado) o 
una síntesis HermitCrab. Para STAMP, el archivo es el que especificó en la configuración del archivo de salida ANA de destino, típicamente 
llamado target_text-ana.txt. 
Para HermitCrab, el archivo es el que especificó en la configuración del archivo maestro de Hermit Crab, típicamente llamado 
target_words-HC.txt. Ambos archivos suelen estar en la carpeta Build. 
NOTA: los mensajes y la barra de tareas mostrarán la base de datos FUENTE como utilizada. En realidad, se está utilizando la base de datos 
de destino.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="440"/>
      <source>Configuration file problem with {fileType}.</source>
      <translation>Problema con el archivo de configuración para {fileType}.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="431"/>
      <source>Lexicon files folder: {fileType} does not exist.</source>
      <translation>La carpeta de archivos de léxico: {fileType} no existe.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="460"/>
      <source>Failed to open the target database.</source>
      <translation>No se pudo abrir la base de datos de destino.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1164"/>
      <source>The file: {fileName} was not found. Did you run the Run Apertium module?</source>
      <translation>El archivo: {fileName} no se encontró. ¿Ejecutó el módulo Run Apertium?</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1250"/>
      <source>Lemma or grammatical category missing for a target word near word {wordNum}. Found only: {morphs}. The preceding two words were: {prevWords}. The following two words were: {follWords}. Processing stopped.</source>
      <translation>Falta el lema o la categoría gramatical para una palabra de destino cerca de la palabra {wordNum}. Solo se encontró: {morphs}. Las dos palabras anteriores eran: {prevWords}. Las dos palabras siguientes eran: {follWords}. Procesamiento detenido.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1327"/>
      <source>Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct</source>
      <translation>Problema con el archivo de configuración para targetANAFile, affixFile, transferResultsFile o sentPunct</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1338"/>
      <source>Configuration file problem with: {property}.</source>
      <translation>Problema con el archivo de configuración para: {property}.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1388"/>
      <source>Error writing the output file.</source>
      <translation>Error al escribir el archivo de salida.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1415"/>
      <source>Converted target words put in the file: {filePath}.</source>
      <translation>Las palabras de destino convertidas se colocaron en el archivo: {filePath}.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1416"/>
      <source>{count} records exported in ANA format.</source>
      <translation>{count} registros exportados en formato ANA.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1418"/>
      <source>Converted target words put in the file: {filePath}</source>
      <translation>Las palabras de destino convertidas se colocaron en el archivo: {filePath}</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1419"/>
      <source>{count} records exported in HermitCrab format.</source>
      <translation>{count} registros exportados en formato HermitCrab.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1438"/>
      <source>The Catalog Target Affixes module must be run before this module. The {fileType}: {filePath} does not exist.</source>
      <translation>El módulo Catalog Target Affixes debe ejecutarse antes de este módulo. El archivo {fileType}: {filePath} no existe.</translation>
    </message>
    <message>
      <location filename="../ConvertTextToSTAMPformat.py" line="1454"/>
      <source>Configuration file problem with: {fileType}.</source>
      <translation>Problema con el archivo de configuración para: {fileType}.</translation>
    </message>
  </context>
</TS>
