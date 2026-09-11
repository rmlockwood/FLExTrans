<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
<context>
    <name>MergeTexts</name>
    <message>
        <location filename="../MergeTexts.py" line="103" />
        <source>Merge Texts</source>
        <translation>Fusionner des textes</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="149" />
        <source>The text "{sourceName}" has no paragraphs. Skipping it.</source>
        <translation>Le texte "{sourceName}" n'a aucun paragraphe. Il est ignoré.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="183" />
        <source>The text "{sourceName}" no longer exists in the project, so it could not be deleted.</source>
        <translation>Le texte "{sourceName}" n'existe plus dans le projet, il n'a donc pas pu être supprimé.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="188" />
        <source>The text "{sourceName}" is now empty but could not be deleted. Delete it in FLEx.</source>
        <translation>Le texte "{sourceName}" est maintenant vide mais n'a pas pu être supprimé. Supprimez-le dans FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="235" />
        <source>The source text setting was "{activeTextName}", which has been merged away, so it now names the merged text "{targetName}".</source>
        <translation>Le paramètre du texte source était "{activeTextName}", qui a été fusionné ; il désigne donc maintenant le texte fusionné "{targetName}".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="245" />
        <source>Counting the interlinear analyses...</source>
        <translation>Comptage des analyses interlinéaires...</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="268" />
        <source>The text "{sourceName}" has no contents and was skipped.</source>
        <translation>Le texte "{sourceName}" n'a aucun contenu et a été ignoré.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="279" />
        <source>Moved {paraCount} paragraph(s) from "{sourceName}".</source>
        <translation>{paraCount} paragraphe(s) déplacé(s) depuis "{sourceName}".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="310" />
        <source>These texts were not deleted because they have media files, which belong to the text rather than to its paragraphs: {nameList}.</source>
        <translation>Ces textes n'ont pas été supprimés car ils contiennent des fichiers multimédias, qui appartiennent au texte et non à ses paragraphes : {nameList}.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="314" />
        <source>{count} text tag(s) were moved to the merged text.</source>
        <translation>{count} étiquette(s) de texte ont été déplacées vers le texte fusionné.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="319" />
        <source>Something went wrong: the source texts had {wordsBefore} analyzed word(s) but the merged text has {wordsAfter}. Restore your backup of the FLEx project and report this.</source>
        <translation>Un problème est survenu : les textes sources comptaient {wordsBefore} mot(s) analysé(s) alors que le texte fusionné en compte {wordsAfter}. Restaurez votre sauvegarde du projet FLEx et signalez ce problème.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="325" />
        <source>{count} source text(s) were deleted.</source>
        <translation>{count} texte(s) source(s) ont été supprimés.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="349" />
        <source>You need to run this module in "modify mode."</source>
        <translation>Vous devez exécuter ce module en "mode modification".</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="364" />
        <source>The {projectName} project has fewer than two texts, so there is nothing to merge.</source>
        <translation>Le projet {projectName} contient moins de deux textes, il n'y a donc rien à fusionner.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="377" />
        <source>No texts were merged.</source>
        <translation>Aucun texte n'a été fusionné.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="106" />
        <source>Combine multiple texts into one, keeping all of the interlinear analyses.</source>
        <translation>Combine plusieurs textes en un seul, en conservant toutes les analyses interlinéaires.</translation>
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
        <translation>Combine plusieurs textes en un nouveau texte. Cette fonction est destinée aux livres bibliques importés chapitre par chapitre : les textes nommés
Matthieu 01, Matthieu 02, Matthieu 03-04, etc., sont fusionnés en un seul texte nommé d'après la plage de chapitres, par ex. Matthieu 01-28.
Le module propose ces groupes en examinant les noms des textes, et vous pouvez aussi choisir les textes vous-même et les mettre dans n'importe quel ordre.
Aucun travail interlinéaire n'est perdu. Chaque mot conserve l'analyse et la glose qui ont été approuvées pour lui, et chaque phrase conserve sa traduction
libre et ses notes.
Les textes que vous fusionnez sont supprimés, c'est pourquoi le module vous demande
de confirmer. Une telle fusion est IRRÉVERSIBLE, dans FLExTrans comme dans FLEx : sauvegardez donc d'abord votre projet FLEx. Avant de l'exécuter,
assurez-vous de ne pas être dans la section Textes et mots de FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="211" />
        <source>An empty discourse chart could not be deleted. Delete it in the FLEx Discourse area.</source>
        <translation>Un graphique de discours vide n'a pas pu être supprimé. Supprimez-le dans la section Discours de FLEx.</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="322" />
        <source>Text "{targetName}" created in the {projectName} project from {textCount} text(s).</source>
        <translation>Texte "{targetName}" créé dans le projet {projectName} à partir de {textCount} texte(s).</translation>
    </message>
    <message>
        <location filename="../MergeTexts.py" line="329" />
        <source>{count} empty discourse chart(s) were deleted along with their texts.</source>
        <translation>{count} graphique(s) de discours vide(s) ont été supprimés avec leurs textes.</translation>
    </message>
</context>
</TS>
