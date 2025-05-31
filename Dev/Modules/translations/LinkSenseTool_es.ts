<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>LinkSenseTool</name>
    <message>
        <location filename="../LinkSenseTool.py" line="229"/>
        <source>Link source and target senses.</source>
        <translation>Vincular sentidos de origen y destino.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="231"/>
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
        <translation>Este módulo creará enlaces 
en el proyecto de origen a los sentidos en el proyecto de destino. Mostrará una ventana
con una lista de todos los sentidos en el texto. Las filas con fondo blanco indican enlaces que
ya existen. Las filas con fondo azul indican enlaces sugeridos basados en una coincidencia exacta
en la glosa, las filas con fondo azul claro indican enlaces sugeridos basados en una coincidencia cercana
en la glosa (actualmente 75% similar), las filas con fondo rojo
aún no tienen un enlace establecido. Haga doble clic en la columna &quot;Palabra principal del destino&quot; para una fila para copiar
el sentido de destino seleccionado actualmente en el cuadro combinado superior a esa fila. Marque la casilla
para crear un enlace para esa fila. Es decir, el sentido de origen se vinculará al sentido de destino.
Desmarcar una casilla para una fila blanca desvinculará el sentido especificado de su sentido de destino.
Las coincidencias cercanas solo se intentan para palabras con cinco letras o más.
Para pares de sentidos sugeridos donde
hay una discrepancia en la categoría gramatical, ambas categorías se colorean en rojo. Esto
es para indicar que puede que no desee vincular los dos sentidos aunque las glosas coincidan.
Este módulo requiere
un campo personalizado a nivel de sentido en su proyecto de origen. Debe ser un campo de texto simple.
El propósito del campo personalizado es contener el enlace a un sentido en el proyecto de destino.
Configure qué campo personalizado se utiliza para vincular en la configuración.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1127"/>
        <source>Save Changes</source>
        <translation>Guardar cambios</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1127"/>
        <source>Do you want to save your changes?</source>
        <translation>¿Desea guardar los cambios?</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1235"/>
        <source>Empty grammatical category found for the target word: </source>
        <translation>Se encontró una categoría gramatical vacía para la palabra de destino: </translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1259"/>
        <source>Empty gloss found for the target word: </source>
        <translation>Se encontró una glosa vacía para la palabra de destino: </translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1264"/>
        <source>More than {num_warnings} empty glosses found. Suppressing further warnings for empty target glosses.</source>
        <translation>Se encontraron más de {num_warnings} glosas vacías. Se suprimirán más advertencias para glosas de destino vacías.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1580"/>
        <source>1 link created.</source>
        <translation>1 enlace creado.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1582"/>
        <source>{num} links created.</source>
        <translation>{num} enlaces creados.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1586"/>
        <source>1 link removed</source>
        <translation>1 enlace eliminado.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1590"/>
        <source> links removed</source>
        <translation>enlaces eliminados.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1658"/>
        <source>Gloss</source>
        <translation>Glosa</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1659"/>
        <source>Category</source>
        <translation>Categoría</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1661"/>
        <source>Comment</source>
        <translation>Comentario</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1760"/>
        <source>Permission error writing {htmlFileName}. Perhaps the file is in use in another program?</source>
        <translation>Error de permisos al escribir {htmlFileName}. ¿Quizás el archivo está en uso en otro programa?</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1764"/>
        <source>Error writing {htmlFileName}.</source>
        <translation>Error al escribir {htmlFileName}.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1768"/>
        <source>{cnt} words written to the file: {htmlFileName}. You&apos;ll find it in the Output folder.</source>
        <translation>{cnt} palabras escritas en el archivo: {htmlFileName}. Lo encontrará en la carpeta de salida.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1771"/>
        <source>No unlinked words. Nothing exported.</source>
        <translation>No hay palabras no vinculadas. Nada exportado.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1786"/>
        <source>No Source Text Name has been set. Please go to Settings and fix this.</source>
        <translation>No se ha establecido un nombre de texto de origen. Por favor, vaya a Configuración y solucione esto.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1791"/>
        <source>No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.</source>
        <translation>No se ha establecido un campo personalizado de origen para el enlace de entrada. Por favor, vaya a Configuración y solucione esto.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1797"/>
        <source>No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation>No se han seleccionado tipos de morfemas de origen contados como raíces. Por favor, vaya a Configuración y solucione esto.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1802"/>
        <source>No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation>No se han seleccionado tipos de morfemas de destino contados como raíces. Por favor, vaya a Configuración y solucione esto.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1815"/>
        <source>The text named: {sourceTextName} not found.</source>
        <translation>No se encontró el texto llamado: {sourceTextName}.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1831"/>
        <source>{linkField} field doesn&apos;t exist. Please read the instructions.</source>
        <translation>El campo {linkField} no existe. Por favor, lea las instrucciones.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1845"/>
        <source>The Target Database does not exist. Please check the configuration file.</source>
        <translation>La base de datos de destino no existe. Por favor, revise el archivo de configuración.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1848"/>
        <source>Opening: {targetProj} as the target database.</source>
        <translation>Abriendo: {targetProj} como la base de datos de destino.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1855"/>
        <source>Failed to open the target database.</source>
        <translation>No se pudo abrir la base de datos de destino.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1858"/>
        <source>Starting {moduleName} for text: {sourceTextName}.</source>
        <translation>Iniciando {moduleName} para el texto: {sourceTextName}.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1902"/>
        <source>There were no senses found for linking. Please check your text and approve some words.</source>
        <translation>No se encontraron sentidos para vincular. Por favor, revise su texto y apruebe algunas palabras.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1904"/>
        <source>Link it!</source>
        <translation>¡Vincúlalo!</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1906"/>
        <source>Source Head Word</source>
        <translation>Palabra principal de origen</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1907"/>
        <source>Source Category</source>
        <translation>Categoría de origen</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1908"/>
        <source>Source Gloss</source>
        <translation>Glosa de origen</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1909"/>
        <source>Target Head Word</source>
        <translation>Palabra principal de destino</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1910"/>
        <source>Target Category</source>
        <translation>Categoría de destino</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1911"/>
        <source>Target Gloss</source>
        <translation>Glosa de destino</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1963"/>
        <source>You need to run this module in &quot;modify mode.&quot;</source>
        <translation>Debe ejecutar este módulo en &quot;modo de modificación&quot;.</translation>
    </message>
</context>
</TS>
