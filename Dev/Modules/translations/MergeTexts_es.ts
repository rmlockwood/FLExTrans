<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es" sourcelanguage="en">
<context>
    <name>MergeTexts</name>
    <message>
        <location filename="../MergeTexts.py" line="103" />
        <source>Merge Texts</source>
        <translation>Combinar textos</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="149" />
        <source>The text "{sourceName}" has no paragraphs. Skipping it.</source>
        <translation>El texto "{sourceName}" no tiene párrafos. Se omite.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="183" />
        <source>The text "{sourceName}" no longer exists in the project, so it could not be deleted.</source>
        <translation>El texto "{sourceName}" ya no existe en el proyecto, por lo que no se pudo eliminar.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="188" />
        <source>The text "{sourceName}" is now empty but could not be deleted. Delete it in FLEx.</source>
        <translation>El texto "{sourceName}" ahora está vacío pero no se pudo eliminar. Elimínelo en FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="235" />
        <source>The source text setting was "{activeTextName}", which has been merged away, so it now names the merged text "{targetName}".</source>
        <translation>La configuración del texto fuente era "{activeTextName}", que se ha combinado, por lo que ahora indica el texto combinado "{targetName}".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="245" />
        <source>Counting the interlinear analyses...</source>
        <translation>Contando los análisis interlineales...</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="268" />
        <source>The text "{sourceName}" has no contents and was skipped.</source>
        <translation>El texto "{sourceName}" no tiene contenido y se omitió.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="279" />
        <source>Moved {paraCount} paragraph(s) from "{sourceName}".</source>
        <translation>Se trasladaron {paraCount} párrafo(s) de "{sourceName}".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="310" />
        <source>These texts were not deleted because they have media files, which belong to the text rather than to its paragraphs: {nameList}.</source>
        <translation>Estos textos no se eliminaron porque tienen archivos multimedia, que pertenecen al texto y no a sus párrafos: {nameList}.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="314" />
        <source>{count} text tag(s) were moved to the merged text.</source>
        <translation>Se trasladaron {count} etiqueta(s) de texto al texto combinado.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="319" />
        <source>Something went wrong: the source texts had {wordsBefore} analyzed word(s) but the merged text has {wordsAfter}. Restore your backup of the FLEx project and report this.</source>
        <translation>Algo salió mal: los textos de origen tenían {wordsBefore} palabra(s) analizada(s), pero el texto combinado tiene {wordsAfter}. Restaure su copia de seguridad del proyecto de FLEx e informe de esto.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="325" />
        <source>{count} source text(s) were deleted.</source>
        <translation>Se eliminaron {count} texto(s) de origen.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="349" />
        <source>You need to run this module in "modify mode."</source>
        <translation>Debe ejecutar este módulo en "modo de modificación".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="364" />
        <source>The {projectName} project has fewer than two texts, so there is nothing to merge.</source>
        <translation>El proyecto {projectName} tiene menos de dos textos, por lo que no hay nada que combinar.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="377" />
        <source>No texts were merged.</source>
        <translation>No se combinó ningún texto.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="106" />
        <source>Combine multiple texts into one, keeping all of the interlinear analyses.</source>
        <translation>Combina varios textos en uno solo, conservando todos los análisis interlineales.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="108" />
        <source>Combine multiple texts into one new text. This is meant for Bible books that were imported one chapter at a time - texts named
Matthew 01, Matthew 02, Matthew 03-04 and so on get merged into a single text named for the range of chapters, e.g. Matthew 01-28.
The module suggests these groups by looking at the text names, and you can also choose the texts yourself and put them in any order.
No interlinear work is lost. Each word keeps the analysis and gloss that was approved for it, and each sentence keeps its free
translation and notes.
The texts you merge are deleted, so the module asks you
to confirm. Merging this way CANNOT be undone, in FLExTrans or in FLEx, so back up your FLEx project first. Before running it, make
sure you are not in the Texts &amp; Words section of FLEx.</source>
        <translation>Combina varios textos en un texto nuevo. Está pensado para libros de la Biblia que se importaron capítulo por capítulo: los textos llamados
Mateo 01, Mateo 02, Mateo 03-04, etc., se combinan en un único texto que recibe el nombre del intervalo de capítulos, p. ej. Mateo 01-28.
El módulo sugiere estos grupos a partir de los nombres de los textos, y también puede elegir los textos usted mismo y ponerlos en cualquier orden.
No se pierde nada del trabajo interlineal. Cada palabra conserva el análisis y la glosa que se aprobaron para ella, y cada oración conserva su traducción
libre y sus notas.
Los textos que combine se eliminan, por lo que el módulo le pide
confirmación. Combinar de esta manera NO se puede deshacer, ni en FLExTrans ni en FLEx, así que haga primero una copia de seguridad de su proyecto de FLEx. Antes de ejecutarlo,
asegúrese de no estar en la sección Textos y palabras de FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="211" />
        <source>An empty discourse chart could not be deleted. Delete it in the FLEx Discourse area.</source>
        <translation>No se pudo eliminar un gráfico de discurso vacío. Elimínelo en el área Discurso de FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="322" />
        <source>Text "{targetName}" created in the {projectName} project from {textCount} text(s).</source>
        <translation>Texto "{targetName}" creado en el proyecto {projectName} a partir de {textCount} texto(s).</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="329" />
        <source>{count} empty discourse chart(s) were deleted along with their texts.</source>
        <translation>Se eliminaron {count} gráfico(s) de discurso vacío(s) junto con sus textos.</translation>
    </message>
</context>
</TS>
