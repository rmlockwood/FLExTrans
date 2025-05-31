<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="142"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation>Sintetizar texto con HermitCrab</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="150"/>
        <source>Synthesizes the target text with the tool HermitCrab.</source>
        <translation>Sintetiza el texto objetivo con la herramienta HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="152"/>
        <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like &apos;target_text-syn.txt&apos;. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named &apos;HermitCrab.config&apos; and will be in the &apos;Build&apos; folder. 
NOTE: Messages will say the SOURCE database
is being used. Actually the target database is being used.
Advanced Information: This module runs HermitCrab against a list of target parses (&apos;target_words-parses.txt&apos;) to
produce surface forms (&apos;target_words-surface.txt&apos;). 
These forms are then used to create the target text.</source>
        <translation>Este módulo ejecuta HermitCrab para crear el texto sintetizado. Los resultados se colocan en el archivo designado en la configuración como Archivo de Síntesis de Salida de Destino. 
Por defecto, será algo como 'target_text-syn.txt'. 
Antes de crear el texto sintetizado, este módulo extrae el léxico del idioma objetivo en forma de un archivo de configuración de HermitCrab. 
Se llama 'HermitCrab.config' y estará en la carpeta 'Build'. 
NOTA: Los mensajes dirán que se está utilizando la base de datos FUENTE. En realidad, se está utilizando la base de datos de destino. 
Información avanzada: Este módulo ejecuta HermitCrab contra una lista de análisis de destino ('target_words-parses.txt') para producir formas superficiales ('target_words-surface.txt'). 
Estas formas se utilizan luego para crear el texto objetivo.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="204"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problema con el archivo de configuración para TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="215"/>
        <source>Failed to open the target database: {targetProj}.</source>
        <translation>No se pudo abrir la base de datos de destino: {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="224"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation>No se encontró un valor para {cacheData} en el archivo de configuración.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="239"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation>Ocurrió un error al cargar el archivo de configuración de HermitCrab para el objeto de síntesis HC. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="242"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation>El archivo de configuración de HermitCrab está actualizado.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="252"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation>Se generó el archivo de configuración de HermitCrab: {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="274"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation>Ocurrió un error al ejecutar la herramienta Generar Configuración de HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="259"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} database.</source>
        <translation>El error contiene una 'KeyNotFoundException' y esto a menudo indica que se debe ejecutar la utilidad FLEx Find and Fix en la base de datos {projectName}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="260"/>
        <source>The full error message is:</source>
        <translation>El mensaje de error completo es:</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="269"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation>Ocurrió un error al cargar el archivo de configuración de HermitCrab para el objeto de síntesis HC. Esto ocurrió después de que se generó el archivo de configuración. (DLL)</translation>
    </message>
</context>
</TS>
