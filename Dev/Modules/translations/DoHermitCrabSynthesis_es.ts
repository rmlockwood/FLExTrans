<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es-ES" sourcelanguage="en">
  <context>
    <name>DoHermitCrabSynthesis</name>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="151" />
      <source>Synthesize Text with HermitCrab</source>
      <translation>Sintetizar texto con HermitCrab</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="154" />
      <source>Synthesizes the target text with the tool HermitCrab.</source>
      <translation>Sintetiza el texto objetivo con la herramienta HermitCrab.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="156" />
      <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like 'target_text-syn.txt'. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named 'HermitCrab.config' and will be in the 'Build' folder. 
NOTE: Messages will say the source project
is being used. Actually the target project is being used.
Advanced Information: This module runs HermitCrab against a list of target parses ('target_words-parses.txt') to
produce surface forms ('target_words-surface.txt'). 
These forms are then used to create the target text.</source>
      <translation>Este módulo ejecuta HermitCrab para crear el texto sintetizado. Los resultados se guardan en el archivo designado en la configuración como Archivo de Síntesis de Salida de Destino.
Este archivo predeterminado será similar a 'target_text-syn.txt'.
Antes de crear el texto sintetizado, este módulo extrae el léxico del idioma de destino en un archivo de configuración de HermitCrab.
Este archivo se llama 'HermitCrab.config' y se encuentra en la carpeta 'Build'.

NOTA: Los mensajes indicarán que se está utilizando el proyecto de origen. En realidad, se está utilizando el proyecto de destino.
Información avanzada: Este módulo ejecuta HermitCrab con una lista de análisis de destino ('target_words-parses.txt') para producir formas de superficie ('target_words-surface.txt').
Estas formas se utilizan para crear el texto de destino.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="208" />
      <source>Configuration file problem with TargetProject.</source>
      <translation>Problema con el archivo de configuración para TargetProject.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="219" />
      <source>Failed to open the target project: {targetProj}.</source>
      <translation>No se pudo abrir el proyecto de destino: {targetProj}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="228" />
      <source>A value for {cacheData} not found in the configuration file.</source>
      <translation>No se encontró un valor para {cacheData} en el archivo de configuración.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="259" />
      <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
      <translation>Ocurrió un error al cargar el archivo de configuración de HermitCrab para el objeto de síntesis HC. (DLL)</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="251" />
      <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
      <translation>Ocurrió una excepción al intentar obtener el archivo XML de HermitCrab desde el objeto DLL: {e}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="301" />
      <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
      <translation>Ocurrió una excepción al intentar establecer el archivo XML de HermitCrab en el objeto DLL. Error: {e}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="267" />
      <source>The HermitCrab configuration file is up to date.</source>
      <translation>El archivo de configuración de HermitCrab está actualizado.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="277" />
      <source>Generated the HermitCrab config. file: {filePath}.</source>
      <translation>Se generó el archivo de configuración de HermitCrab: {filePath}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="306" />
      <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
      <translation>Ocurrió un error al ejecutar la herramienta Generar Configuración de HermitCrab.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="284" />
      <source>The error contains a 'KeyNotFoundException' and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.</source>
      <translation>El error contiene una 'KeyNotFoundException' y esto a menudo indica que se debe ejecutar la utilidad FLEx Find and Fix en el proyecto {projectName}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="285" />
      <source>The full error message is:</source>
      <translation>El mensaje de error completo es:</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="296" />
      <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
      <translation>Ocurrió un error al cargar el archivo de configuración de HermitCrab para el objeto de síntesis HC. Esto ocurrió después de que se generó el archivo de configuración. (DLL)</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="336" />
      <source>There was an error opening the HermitCrab surface forms file.</source>
      <translation>Ocurrió un error al abrir el archivo de formas superficiales de HermitCrab.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="345" />
      <source>The file: {transferResultsFile} was not found. Did you run the {runApertium} module?</source>
      <translation>El archivo: {transferResultsFile} no fue encontrado. ¿Ejecutó el módulo {runApertium}?</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="360" />
      <source>The number of surface forms does not match the number of Lexical Units.</source>
      <translation>El número de formas superficiales no coincide con el número de Unidades Léxicas.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="390" />
      <source>Synthesis failed. ({saveStr})</source>
      <translation>La síntesis falló. ({saveStr})</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="414" />
      <source>Error writing the file: {synFile}.</source>
      <translation>Error al escribir el archivo: {synFile}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="431" />
      <source>There was an error opening the HermitCrab master file. Do you have the setting "Use HermitCrab Synthesis" turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
      <translation>Ocurrió un error al abrir el archivo maestro de HermitCrab. ¿Tiene activada la opción "Usar síntesis HermitCrab"? ¿Ejecutó el módulo Convertir texto a formato de sintetizador? Archivo: {parsesFile}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="440" />
      <source>There was an error opening the HermitCrab parses file.</source>
      <translation>Ocurrió un error al abrir el archivo de análisis de HermitCrab.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="455" />
      <source>Malformed Lexical Unit in HermitCrab master file skipping this line: {line}</source>
      <translation>Unidad léxica mal formada en el archivo maestro de HermitCrab, omitiendo esta línea: {line}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="651" />
      <source>Unable to open the HC master file.</source>
      <translation>No se pudo abrir el archivo maestro de HC.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="677" />
      <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
      <translation>Ocurrió un error al establecer el archivo de glosas para la herramienta HermitCrab Synthesize By Gloss (DLL).</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="682" />
      <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
      <translation>Ocurrió una excepción al intentar establecer el archivo de glosas para la herramienta HermitCrab Synthesize By Gloss (DLL). Error: {e}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="688" />
      <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
      <translation>Ocurrió un error al ejecutar la herramienta HermitCrab Synthesize By Gloss (DLL).</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="693" />
      <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
      <translation>Ocurrió una excepción al intentar ejecutar (llamando a Process) la herramienta HermitCrab Synthesize By Gloss (DLL). Error: {e}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="713" />
      <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
      <translation>Ocurrió un error al ejecutar la herramienta HermitCrab Synthesize By Gloss.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="726" />
      <source>An error happened when trying to open the file: {parsesFile}</source>
      <translation>Ocurrió un error al intentar abrir el archivo: {parsesFile}</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="729" />
      <source>Processing {LUsCount} unique lexical units.</source>
      <translation>Procesando {LUsCount} unidades léxicas únicas.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="744" />
      <source>Configuration file problem with the value: {val}.</source>
      <translation>Problema con el archivo de configuración en el valor: {val}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="759" />
      <source>The synthesized target text is in the file: {file}.</source>
      <translation>El texto objetivo sintetizado está en el archivo: {file}.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="760" />
      <source>Synthesis complete.</source>
      <translation>Síntesis completa.</translation>
    </message>
    <message>
      <location filename="../DoHermitCrabSynthesis.py" line="798" />
      <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
      <translation>{master} o {parses} o {surface} o {transfer} no se encontró en el archivo de configuración.</translation>
    </message>
  </context>
</TS>