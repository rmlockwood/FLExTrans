<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractBilingualLexicon</name>
    <message>
      <location filename="../ExtractBilingualLexicon.py" line="118"/>
      <source>Build Bilingual Lexicon</source>
      <translation>Construir léxico bilingüe</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="180"/>
        <source>Builds an Apertium-style bilingual lexicon.</source>
        <translation>Construye un léxico bilingüe al estilo de Apertium.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="182"/>
        <source>This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.

You can make custom changes to the bilingual lexicon by using Replacement Dictionary Editor. See the help
document for more details.</source>
        <translation>Este módulo construirá un léxico bilingüe para dos proyectos. El proyecto al que está configurado FlexTools es su proyecto fuente. Configure el Proyecto Destino en Configuración con el nombre de su proyecto destino.
Este módulo construye el léxico bilingüe basado en los enlaces de sentidos fuente a sentidos destino que están en su proyecto fuente. Use el módulo Sense Linker para crear estos enlaces.
El léxico bilingüe se almacenará en el archivo especificado por la configuración &quot;Archivo de Salida del Diccionario Bilingüe&quot;. Este archivo generalmente se llama bilingual.dix y suele estar en la carpeta de Salida.

Puede realizar cambios personalizados en el léxico bilingüe utilizando el Editor de Diccionario de Reemplazo. Consulte el documento de ayuda para más detalles.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="300"/>
        <source>Custom field for linking doesn&apos;t exist. Please read the instructions.</source>
        <translation>El campo personalizado para enlazar no existe. Por favor, lea las instrucciones.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="303"/>
        <source>No Source Morphnames to count as root found. Review your Settings.</source>
        <translation>No se encontraron nombres de morfemas fuente para contar como raíz. Revise su configuración.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="306"/>
        <source>No Sentence Punctuation found. Review your Settings.</source>
        <translation>No se encontraron signos de puntuación de oración. Revise su configuración.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="315"/>
        <source>Ill-formed property: &quot;CategoryAbbrevSubstitutionList&quot;. Expected pairs of categories.</source>
        <translation>Propiedad mal formada: &quot;CategoryAbbrevSubstitutionList&quot;. Se esperaban pares de categorías.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="325"/>
        <source>Custom field: {linkField} doesn&apos;t exist. Please read the instructions.</source>
        <translation>El campo personalizado: {linkField} no existe. Por favor, lea las instrucciones.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="344"/>
        <source>A value for {key} not found in the configuration file.</source>
        <translation>No se encontró un valor para {key} en el archivo de configuración.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="356"/>
        <source>The bilingual dictionary is up to date.</source>
        <translation>El diccionario bilingüe está actualizado.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="374"/>
        <source>Error retrieving categories.</source>
        <translation>Error al recuperar categorías.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="410"/>
        <source>Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.</source>
        <translation>Se encontró una entrada con espacios al principio o al final mientras se procesaba la entrada fuente: {rawHeadWord}. Los espacios fueron eliminados, pero por favor corríjalo en el léxico.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="413"/>
        <source>Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.</source>
        <translation>Se encontró una entrada con uno de los siguientes caracteres no válidos: {chars} en {rawHeadWord}. Por favor, corríjalo en el léxico antes de continuar.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="440"/>
        <source>Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}</source>
        <translation>Se encontró un sentido con categoría gramatical desconocida mientras se procesaba la entrada fuente: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="447"/>
        <source>Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}</source>
        <translation>Se encontró una entrada que solo difiere en mayúsculas/minúsculas de otra entrada con la misma categoría gramatical ({sourcePOSabbrev}). Este sentido será omitido. Entrada fuente: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="498"/>
        <source>Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Omitiendo sentido porque la categoría gramatical del destino no está definida para la entrada destino: {targetHeadWord} mientras se procesaba la entrada fuente: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="500"/>
        <source>Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Omitiendo sentido porque pertenece a esta clase: {className} para la entrada destino: {targetHeadWord} mientras se procesaba la entrada fuente: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="508"/>
        <source>Skipping sense that is of class: {className} for headword: {rawHeadWord}</source>
        <translation>Omitiendo sentido que pertenece a la clase: {className} para la entrada: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="510"/>
        <source>Skipping sense, no analysis object for headword: {rawHeadWord}</source>
        <translation>Omitiendo sentido, no hay objeto de análisis para la entrada: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="533"/>
        <source>No lexeme form. Skipping. Headword: {rawHeadWord}</source>
        <translation>Sin forma de lexema. Omitiendo. Entrada: {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="542"/>
        <source>No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}</source>
        <translation>Sin tipo de morfema. Omitiendo. {rawHeadWord} Mejor Vern: {vernString}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="568"/>
        <source>There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.</source>
        <translation>Hay un problema con el Archivo de Reemplazo del Diccionario Bilingüe: {replFile}. Por favor, revise la configuración del archivo.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="595"/>
        <source>There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.</source>
        <translation>Hubo un problema al crear el Archivo de Salida del Diccionario Bilingüe: {fullPathBilingFile}. Por favor, revise la configuración del archivo.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="599"/>
        <source>Creation complete to the file: {filePath}.</source>
        <translation>Creación completada en el archivo: {filePath}.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="600"/>
        <source>{recordsDumpedCount} records created.</source>
        <translation>{recordsDumpedCount} registros creados.</translation>
    </message>
</context>
</TS>
