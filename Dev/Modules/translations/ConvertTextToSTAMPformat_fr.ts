<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ConvertTextToSTAMPformat</name>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="146"/>
        <source>Convert Text to Synthesizer Format</source>
        <translation>Convertir le texte au format du synthétiseur</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="149"/>
        <source>Convert the file produced by {runApert} into a text file in a Synthesizer format</source>
        <translation>Convertir le fichier produit par {runApert} en un fichier texte au format du synthétiseur</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="151"/>
        <source>This module will take the Target Transfer Results File created by {runApert} and convert it to a format suitable
for synthesis, using information from the Target Project indicated in the settings.  Depending on the setting for
HermitCrab synthesis, the output file will either be in STAMP format or in a format suitable for the HermitCrab
synthesis program.
The output file will be stored in different files depending on whether you are doing STAMP synthesis (default) or
HermitCrab synthesis. For STAMP, the file is what you specified by the Target Output ANA File setting -- typically
called target_text-ana.txt.
For HermitCrab, the file is what you specified by the HermitCrab Master File setting -- typically called
target_words-HC.txt. Both files are usually in the Build folder.
NOTE: messages and the task bar will show the source project as being used. Actually the target project
is being used.</source>
        <translation>Ce module prendra le fichier de résultats de transfert cible créé par {runApert} et le convertira dans un format approprié
pour la synthèse, en utilisant les informations du projet cible indiqué dans les paramètres. Selon le paramètre pour
la synthèse HermitCrab, le fichier de sortie sera soit au format STAMP, soit dans un format approprié pour le
programme de synthèse HermitCrab.
Le fichier de sortie sera stocké dans différents fichiers selon que vous faites une synthèse STAMP (par défaut) ou
une synthèse HermitCrab. Pour STAMP, le fichier est celui que vous avez spécifié par le paramètre Fichier ANA de sortie cible -- généralement
appelé target_text-ana.txt.
Pour HermitCrab, le fichier est celui que vous avez spécifié par le paramètre Fichier maître HermitCrab -- généralement appelé
target_words-HC.txt. Les deux fichiers sont généralement dans le dossier Build.
REMARQUE : les messages et la barre des tâches afficheront le projet source comme étant utilisé. En réalité, c'est le projet cible
qui est utilisé.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="418"/>
        <source>Configuration file problem with {fileType}.</source>
        <translation>Problème de fichier de configuration avec {fileType}.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="409"/>
        <source>Lexicon files folder: {fileType} does not exist.</source>
        <translation>Le dossier des fichiers de lexique : {fileType} n'existe pas.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="438"/>
        <source>Failed to open the target project.</source>
        <translation>Échec de l'ouverture du projet cible.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1142"/>
        <source>The file: {fileName} was not found. Did you run the {runApert} module?</source>
        <translation>Le fichier : {fileName} n'a pas été trouvé. Avez-vous exécuté le module {runApert} ?</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1228"/>
        <source>Lemma or grammatical category missing for a target word near word {wordNum}. Found only: {morphs}. The preceding two words were: {prevWords}. The following two words were: {follWords}. Processing stopped.</source>
        <translation>Lemme ou catégorie grammaticale manquant pour un mot cible près du mot {wordNum}. Trouvé seulement : {morphs}. Les deux mots précédents étaient : {prevWords}. Les deux mots suivants étaient : {follWords}. Traitement arrêté.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1305"/>
        <source>Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct</source>
        <translation>Problème de fichier de configuration avec targetANAFile ou affixFile ou transferResultsFile ou sentPunct</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1316"/>
        <source>Configuration file problem with: {property}.</source>
        <translation>Problème de fichier de configuration avec : {property}.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1366"/>
        <source>Error writing the output file.</source>
        <translation>Erreur lors de l'écriture du fichier de sortie.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1393"/>
        <source>Converted target words put in the file: {filePath}.</source>
        <translation>Mots cibles convertis mis dans le fichier : {filePath}.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1394"/>
        <source>{count} records exported in ANA format.</source>
        <translation>{count} enregistrements exportés au format ANA.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1396"/>
        <source>Converted target words put in the file: {filePath}</source>
        <translation>Mots cibles convertis mis dans le fichier : {filePath}</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1397"/>
        <source>{count} records exported in HermitCrab format.</source>
        <translation>{count} enregistrements exportés au format HermitCrab.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1416"/>
        <source>The Catalog Target Affixes module must be run before this module. The {fileType}: {filePath} does not exist.</source>
        <translation>Le module Catalogue des affixes cibles doit être exécuté avant ce module. Le {fileType} : {filePath} n'existe pas.</translation>
    </message>
    <message>
        <location filename="../ConvertTextToSTAMPformat.py" line="1432"/>
        <source>Configuration file problem with: {fileType}.</source>
        <translation>Problème de fichier de configuration avec : {fileType}.</translation>
    </message>
</context>
</TS>
