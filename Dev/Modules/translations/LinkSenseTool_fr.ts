<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1">
<context>
    <name>LinkSenseTool</name>
    <message>
        <location filename="../LinkSenseTool.py" line="198"/>
        <source>Sense Linker Tool</source>
        <translation>Outil de liaison de sens</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="201"/>
        <source>Link source and target senses.</source>
        <translation>Lier les sens source et cible.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="203"/>
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
        <translation>Ce module créera des liens
dans le projet source vers les sens dans le projet cible. Il affichera une fenêtre
avec une liste de tous les sens dans le texte. Les lignes à fond blanc indiquent des liens qui
existent déjà. Les lignes à fond bleu indiquent des liens suggérés basés sur une correspondance exacte
de la glose, les lignes à fond bleu clair indiquent des liens suggérés basés sur une correspondance proche
de la glose (actuellement 75% similaire), les lignes à fond rouge
n'ont pas encore de lien établi. Double-cliquez sur la colonne Mot-tête cible pour une ligne afin de copier
le sens cible actuellement sélectionné dans la liste déroulante supérieure dans cette ligne. Cliquez sur la case à cocher
pour créer un lien pour cette ligne. C'est-à-dire que le sens source sera lié au sens cible.
Décocher une case pour une ligne blanche déliera le sens spécifié de son sens cible.
Les correspondances proches ne sont tentées que pour les mots de cinq lettres ou plus.
Pour les paires de sens suggérées où
il y a une incompatibilité dans la catégorie grammaticale, les deux catégories sont colorées en rouge. Ceci
indique que vous ne voudrez peut-être pas lier les deux sens même si les gloses correspondent.
Ce module nécessite
un champ personnalisé au niveau du sens dans votre projet source. Il doit s'agir d'un champ de texte simple.
Le but du champ personnalisé est de contenir le lien vers un sens dans le projet cible.
Définissez quel champ personnalisé est utilisé pour la liaison dans les paramètres.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1144"/>
        <source>Save Changes</source>
        <translation>Enregistrer les modifications</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1144"/>
        <source>Do you want to save your changes?</source>
        <translation>Voulez-vous enregistrer vos modifications?</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1265"/>
        <source>Empty grammatical category found for the target word: </source>
        <translation>Catégorie grammaticale vide trouvée pour le mot cible : </translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1289"/>
        <source>Empty gloss found for the target word: </source>
        <translation>Glose vide trouvée pour le mot cible : </translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1294"/>
        <source>More than {num_warnings} empty glosses found. Suppressing further warnings for empty target glosses.</source>
        <translation>Plus de {num_warnings} gloses vides trouvées. Suppression des avertissements supplémentaires pour les gloses cibles vides.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1512"/>
        <source>No words with a valid root morph type were found. Please check the your settings, specifically Source Morpheme Types Counted As Roots.</source>
        <translation>Aucun mot avec un type de morphème racine valide n'a été trouvé. Veuillez vérifier vos paramètres, en particulier les types de morphèmes sources comptés comme racines.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1619"/>
        <source>1 link created.</source>
        <translation>1 lien créé.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1621"/>
        <source>{num} links created.</source>
        <translation>{num} liens créés.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1625"/>
        <source>1 link removed</source>
        <translation>1 lien supprimé</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1629"/>
        <source>{num} links removed</source>
        <translation>{num} liens supprimés</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1697"/>
        <source>Gloss</source>
        <translation>Glose</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1698"/>
        <source>Category</source>
        <translation>Catégorie</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1700"/>
        <source>Comment</source>
        <translation>Commentaire</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1799"/>
        <source>Permission error writing {htmlFileName}. Perhaps the file is in use in another program?</source>
        <translation>Erreur de permission lors de l'écriture de {htmlFileName}. Peut-être que le fichier est utilisé dans un autre programme?</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1803"/>
        <source>Error writing {htmlFileName}.</source>
        <translation>Erreur lors de l'écriture de {htmlFileName}.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1807"/>
        <source>{cnt} words written to the file: {htmlFileName}. You'll find it in the Output folder.</source>
        <translation>{cnt} mots écrits dans le fichier : {htmlFileName}. Vous le trouverez dans le dossier de sortie.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1810"/>
        <source>No unlinked words. Nothing exported.</source>
        <translation>Aucun mot non lié. Rien n'a été exporté.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1825"/>
        <source>No Source Text Name has been set. Please go to Settings and fix this.</source>
        <translation>Aucun nom de texte source n'a été défini. Veuillez aller dans les paramètres et corriger cela.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1830"/>
        <source>No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.</source>
        <translation>Aucun champ personnalisé source pour le lien d'entrée n'a été défini. Veuillez aller dans les paramètres et corriger cela.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1836"/>
        <source>No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation>Aucun type de morphème source compté comme racine n'a été sélectionné. Veuillez aller dans les paramètres et corriger cela.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1841"/>
        <source>No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.</source>
        <translation>Aucun type de morphème cible compté comme racine n'a été sélectionné. Veuillez aller dans les paramètres et corriger cela.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1855"/>
        <source>The text named: {sourceTextName} not found.</source>
        <translation>Le texte nommé : {sourceTextName} n'a pas été trouvé.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1872"/>
        <source>{linkField} field doesn't exist. Please read the instructions.</source>
        <translation>Le champ {linkField} n'existe pas. Veuillez lire les instructions.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1886"/>
        <source>The target project does not exist. Please check the configuration file.</source>
        <translation>Le projet cible n'existe pas. Veuillez vérifier le fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1889"/>
        <source>Opening: {targetProj} as the target project.</source>
        <translation>Ouverture de : {targetProj} en tant que projet cible.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1896"/>
        <source>Failed to open the target project.</source>
        <translation>Échec de l'ouverture du projet cible.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1899"/>
        <source>Starting {moduleName} for text: {sourceTextName}.</source>
        <translation>Démarrage de {moduleName} pour le texte : {sourceTextName}.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1928"/>
        <source>There were no senses found for linking. Please check your text and approve some words.</source>
        <translation>Aucun sens n'a été trouvé pour la liaison. Veuillez vérifier votre texte et approuver certains mots.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1944"/>
        <source>There was an error finding senses to link.</source>
        <translation>Il y a eu une erreur lors de la recherche des sens à lier.</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1946"/>
        <source>Link it!</source>
        <translation>Liez-le!</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1948"/>
        <source>Source Head Word</source>
        <translation>Mot-tête source</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1949"/>
        <source>Source Category</source>
        <translation>Catégorie source</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1950"/>
        <source>Source Gloss</source>
        <translation>Glose source</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1951"/>
        <source>Target Head Word</source>
        <translation>Mot-tête cible</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1952"/>
        <source>Target Category</source>
        <translation>Catégorie cible</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="1953"/>
        <source>Target Gloss</source>
        <translation>Glose cible</translation>
    </message>
    <message>
        <location filename="../LinkSenseTool.py" line="2009"/>
        <source>You need to run this module in &quot;modify mode.&quot;</source>
        <translation>Vous devez exécuter ce module en "mode modification".</translation>
    </message>
</context>
</TS>
