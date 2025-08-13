<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractSourceText</name>
    <message>
      <location filename="../ExtractSourceText.py" line="118"/>
      <source>Extract Source Text</source>
      <translation>Extraer texto fuente</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="97"/>
        <source>Exports an Analyzed FLEx text into Apertium format.</source>
        <translation>Exporta un texto FLEx analizado al formato Apertium.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="99"/>
        <source>This module will use the Source Text Name set in the Settings. It will first check 
to see if each word in the selected text is
fully analyzed (word gloss or category is not necessary). If the text is not
fully analyzed you will get warnings.
Next, this module will go through each bundle in the interlinear text and export
information in the format that Apertium needs. The general idea is that
affixes and clitics will be exported as &lt;gloss&gt; and root/stems will be exported
as head_word&lt;pos&gt;&lt;feat1&gt;...&lt;featN&gt;&lt;class1&gt;...&lt;classN&gt;. Where feat1 to featN are one or more 
inflection features that may be present for the root/stem 
and class1 to classN are inflection classes that may be present on the stem.
The exported sentences will be stored in the file specified by the Analyzed Text Output File setting.
This is typically called source_text-aper.txt and is usually in the Build folder.</source>
        <translation>Este módulo usará el Nombre del Texto Fuente configurado en los Ajustes. Primero verificará si cada palabra en el texto seleccionado está completamente analizada (el glosario de palabras o la categoría no son necesarios). Si el texto no está completamente analizado, recibirá advertencias. Luego, este módulo recorrerá cada paquete en el texto interlineal y exportará información en el formato que necesita Apertium. La idea general es que los afijos y clíticos se exportarán como &lt;gloss&gt; y las raíces/tallos se exportarán como head_word&lt;pos&gt;&lt;feat1&gt;...&lt;featN&gt;&lt;class1&gt;...&lt;classN&gt;. Donde feat1 a featN son una o más características flexivas que pueden estar presentes para la raíz/tallo y class1 a classN son clases flexivas que pueden estar presentes en el tallo. Las oraciones exportadas se almacenarán en el archivo especificado por la configuración &quot;Archivo de Salida del Texto Analizado&quot;. Este archivo generalmente se llama source_text-aper.txt y suele estar en la carpeta Build.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="268"/>
        <source>There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.</source>
        <translation>Hay un problema con la ruta del Archivo de Salida del Texto Analizado: {path}. Por favor, revise la configuración del archivo.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="283"/>
        <source>The text named: {textName} not found.</source>
        <translation>No se encontró el texto llamado: {textName}.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="315"/>
        <source>There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.</source>
        <translation>Hay un problema con la ruta del Archivo de Resultados de Tree Tran: {path}. Por favor, revise la configuración del archivo.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="363"/>
        <source>Sentence {sentNum} from TreeTran not found</source>
        <translation>No se encontró la oración {sentNum} de TreeTran.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="384"/>
        <source>Null Guid in sentence {sentNum}, word {wordNum}</source>
        <translation>GUID nulo en la oración {sentNum}, palabra {wordNum}</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="392"/>
        <source>Could not find the desired Guid in sentence {sentNum}, word {wordNum}</source>
        <translation>No se pudo encontrar el GUID deseado en la oración {sentNum}, palabra {wordNum}</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="449"/>
        <source>Sentence: {sentNum} not found. Check that the right parses are present.</source>
        <translation>No se encontró la oración: {sentNum}. Verifique que los análisis correctos estén presentes.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="457"/>
        <source>Exported: {count} sentence(s) using TreeTran results.</source>
        <translation>Exportado: {count} oración(es) usando los resultados de TreeTran.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="460"/>
        <source>No parses found for {count} sentence(s).</source>
        <translation>No se encontraron análisis para {count} oración(es).</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="467"/>
        <source>Exported {count} sentence(s) to {path}.</source>
        <translation>Exportadas {count} oración(es) a {path}.</translation>
    </message>
    <message>
        <location filename="../ExtractSourceText.py" line="471"/>
        <source>Export of {textName} complete.</source>
        <translation>Exportación de {textName} completada.</translation>
    </message>
</context>
</TS>
