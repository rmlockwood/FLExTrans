<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>LinkSenseTool</name>
    <message>
      <location filename="../LinkSenseTool.py" line="229"/>
      <source>Link source and target senses.</source>
      <translation>Verknüpfen Sie Quell- und Zielbedeutungen.</translation>
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
      <translation>Dieses Modul erstellt Verknüpfungen 
im Quellprojekt zu Bedeutungen im Zielprojekt. Es zeigt ein Fenster
mit einer Liste aller Bedeutungen im Text. Weiße Hintergrundzeilen zeigen Verknüpfungen an, die
bereits existieren. Blaue Hintergrundzeilen zeigen vorgeschlagene Verknüpfungen basierend auf einer exakten Übereinstimmung
der Glosse, hellblaue Hintergrundzeilen zeigen vorgeschlagene Verknüpfungen basierend auf einer engen Übereinstimmung
der Glosse (derzeit 75% ähnlich), rote Hintergrundzeilen
haben noch keine Verknüpfung. Doppelklicken Sie auf die Spalte &quot;Ziel-Stichwort&quot; für eine Zeile, um
die aktuell ausgewählte Zielbedeutung aus der oberen Kombobox in diese Zeile zu kopieren. Aktivieren Sie das Kontrollkästchen,
um eine Verknüpfung für diese Zeile zu erstellen. D. h., die Quellbedeutung wird mit der Zielbedeutung verknüpft.
Das Deaktivieren eines Kontrollkästchens für eine weiße Zeile hebt die Verknüpfung der angegebenen Bedeutung mit ihrer Zielbedeutung auf.
Enge Übereinstimmungen werden nur für Wörter mit fünf oder mehr Buchstaben versucht.
Für vorgeschlagene Bedeutungs-Paare, bei denen
es eine Diskrepanz in der grammatischen Kategorie gibt, werden beide Kategorien rot markiert. Dies
zeigt an, dass Sie die beiden Bedeutungen möglicherweise nicht verknüpfen möchten, obwohl die Glossen übereinstimmen.
Dieses Modul erfordert
ein benutzerdefiniertes Feld auf Bedeutungsebene in Ihrem Quellprojekt. Es sollte ein einfaches Textfeld sein.
Der Zweck des benutzerdefinierten Feldes besteht darin, die Verknüpfung zu einer Bedeutung im Zielprojekt zu speichern.
Legen Sie in den Einstellungen fest, welches benutzerdefinierte Feld für die Verknüpfung verwendet wird.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1127"/>
      <source>Save Changes</source>
      <translation>Änderungen speichern</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1127"/>
      <source>Do you want to save your changes?</source>
      <translation>Möchten Sie Ihre Änderungen speichern?</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1235"/>
      <source>Empty grammatical category found for the target word: </source>
      <translation>Leere grammatische Kategorie für das Zielwort gefunden: </translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1259"/>
      <source>Empty gloss found for the target word: </source>
      <translation>Leere Glosse für das Zielwort gefunden: </translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1264"/>
      <source>More than {num_warnings} empty glosses found. Suppressing further warnings for empty target glosses.</source>
      <translation>Mehr als {num_warnings} leere Glossen gefunden. Weitere Warnungen für leere Zielglossen werden unterdrückt.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1580"/>
      <source>1 link created.</source>
      <translation>1 Verknüpfung erstellt.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1582"/>
      <source>{num} links created.</source>
      <translation>{num} Verknüpfungen erstellt.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1586"/>
      <source>1 link removed</source>
      <translation>1 Verknüpfung entfernt.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1590"/>
      <source> links removed</source>
      <translation>Verknüpfungen entfernt.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1658"/>
      <source>Gloss</source>
      <translation>Glosse</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1659"/>
      <source>Category</source>
      <translation>Kategorie</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1661"/>
      <source>Comment</source>
      <translation>Kommentar</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1760"/>
      <source>Permission error writing {htmlFileName}. Perhaps the file is in use in another program?</source>
      <translation>Berechtigungsfehler beim Schreiben von {htmlFileName}. Vielleicht wird die Datei in einem anderen Programm verwendet?</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1764"/>
      <source>Error writing {htmlFileName}.</source>
      <translation>Fehler beim Schreiben von {htmlFileName}.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1768"/>
      <source>{cnt} words written to the file: {htmlFileName}. You&apos;ll find it in the Output folder.</source>
      <translation>{cnt} Wörter in die Datei geschrieben: {htmlFileName}. Sie finden sie im Ausgabeverzeichnis.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1771"/>
      <source>No unlinked words. Nothing exported.</source>
      <translation>Keine nicht verknüpften Wörter. Nichts exportiert.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1786"/>
      <source>No Source Text Name has been set. Please go to Settings and fix this.</source>
      <translation>Kein Quelltextname wurde festgelegt. Bitte gehen Sie zu den Einstellungen und beheben Sie dies.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1791"/>
      <source>No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.</source>
      <translation>Kein benutzerdefiniertes Quellfeld für Eintragsverknüpfung wurde festgelegt. Bitte gehen Sie zu den Einstellungen und beheben Sie dies.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1797"/>
      <source>No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
      <translation>Keine Quellmorphemtypen, die als Wurzeln gezählt werden, wurden ausgewählt. Bitte gehen Sie zu den Einstellungen und beheben Sie dies.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1802"/>
      <source>No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
      <translation>Keine Zielmorphemtypen, die als Wurzeln gezählt werden, wurden ausgewählt. Bitte gehen Sie zu den Einstellungen und beheben Sie dies.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1815"/>
      <source>The text named: {sourceTextName} not found.</source>
      <translation>Der Text mit dem Namen: {sourceTextName} wurde nicht gefunden.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1831"/>
      <source>{linkField} field doesn&apos;t exist. Please read the instructions.</source>
      <translation>Das Feld {linkField} existiert nicht. Bitte lesen Sie die Anweisungen.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1845"/>
      <source>The Target Database does not exist. Please check the configuration file.</source>
      <translation>Die Zieldatenbank existiert nicht. Bitte überprüfen Sie die Konfigurationsdatei.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1848"/>
      <source>Opening: {targetProj} as the target database.</source>
      <translation>Öffnen von: {targetProj} als Zieldatenbank.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1855"/>
      <source>Failed to open the target database.</source>
      <translation>Die Zieldatenbank konnte nicht geöffnet werden.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1858"/>
      <source>Starting {moduleName} for text: {sourceTextName}.</source>
      <translation>Starte {moduleName} für den Text: {sourceTextName}.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1902"/>
      <source>There were no senses found for linking. Please check your text and approve some words.</source>
      <translation>Es wurden keine Bedeutungen zum Verknüpfen gefunden. Bitte überprüfen Sie Ihren Text und genehmigen Sie einige Wörter.</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1904"/>
      <source>Link it!</source>
      <translation>Verknüpfen!</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1906"/>
      <source>Source Head Word</source>
      <translation>Quell-Stichwort</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1907"/>
      <source>Source Category</source>
      <translation>Quellkategorie</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1908"/>
      <source>Source Gloss</source>
      <translation>Quellglosse</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1909"/>
      <source>Target Head Word</source>
      <translation>Ziel-Stichwort</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1910"/>
      <source>Target Category</source>
      <translation>Zielkategorie</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1911"/>
      <source>Target Gloss</source>
      <translation>Zielglosse</translation>
    </message>
    <message>
      <location filename="../LinkSenseTool.py" line="1963"/>
      <source>You need to run this module in &quot;modify mode.&quot;</source>
      <translation>Sie müssen dieses Modul im &quot;Änderungsmodus&quot; ausführen.</translation>
    </message>
  </context>
</TS>
