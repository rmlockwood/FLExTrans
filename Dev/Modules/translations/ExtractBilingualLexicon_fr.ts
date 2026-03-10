<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ExtractBilingualLexicon</name>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="132"/>
        <source>Build Bilingual Lexicon</source>
        <translation>Construire le lexique bilingue</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="135"/>
        <source>Builds an Apertium-style bilingual lexicon.</source>
        <translation>Construit un lexique bilingue de style Apertium.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="137"/>
        <source>This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.

You can make custom changes to the bilingual lexicon by using the {replEditorModule}. See the help
document for more details.</source>
        <translation>Ce module construira un lexique bilingue pour deux projets. Le
projet sur lequel FlexTools est configuré est votre projet source. Définissez le projet cible
dans les paramètres avec le nom de votre projet cible.
Ce module construit le lexique bilingue basé sur les liens entre les sens sources et les sens cibles
qui se trouvent dans votre projet source. Utilisez le module de liaison de sens pour créer ces liens.
Le lexique bilingue sera stocké dans le fichier spécifié par le paramètre Fichier de sortie du dictionnaire bilingue.
Il s'appelle généralement bilingual.dix et se trouve habituellement dans le dossier Output.

Vous pouvez apporter des modifications personnalisées au lexique bilingue en utilisant le {replEditorModule}. Consultez le document
d'aide pour plus de détails.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="255"/>
        <source>Custom field for linking doesn't exist. Please read the instructions.</source>
        <translation>Le champ personnalisé pour la liaison n'existe pas. Veuillez lire les instructions.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="258"/>
        <source>No Source Morphnames to count as root found. Review your Settings.</source>
        <translation>Aucun nom morphologique source à compter comme racine trouvé. Vérifiez vos paramètres.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="261"/>
        <source>No Sentence Punctuation found. Review your Settings.</source>
        <translation>Aucune ponctuation de phrase trouvée. Vérifiez vos paramètres.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="270"/>
        <source>Ill-formed property: &quot;CategoryAbbrevSubstitutionList&quot;. Expected pairs of categories.</source>
        <translation>Propriété mal formée : « CategoryAbbrevSubstitutionList ». Paires de catégories attendues.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="280"/>
        <source>Custom field: {linkField} doesn't exist. Please read the instructions.</source>
        <translation>Le champ personnalisé : {linkField} n'existe pas. Veuillez lire les instructions.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="299"/>
        <source>A value for {key} not found in the configuration file.</source>
        <translation>Une valeur pour {key} introuvable dans le fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="311"/>
        <source>The bilingual dictionary is up to date.</source>
        <translation>Le dictionnaire bilingue est à jour.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="329"/>
        <source>Error retrieving categories.</source>
        <translation>Erreur lors de la récupération des catégories.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="365"/>
        <source>Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.</source>
        <translation>Un mot-vedette avec des espaces au début ou à la fin a été trouvé lors du traitement du mot-vedette source : {rawHeadWord}. Les espaces ont été supprimés, mais veuillez corriger cela dans le lexique.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="368"/>
        <source>Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.</source>
        <translation>Un mot-vedette avec l'un des caractères invalides suivants a été trouvé : {chars} dans {rawHeadWord}. Veuillez corriger cela dans le lexique avant de continuer.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="395"/>
        <source>Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}</source>
        <translation>Un sens avec une catégorie grammaticale inconnue a été rencontré lors du traitement du mot-vedette source : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="402"/>
        <source>Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}</source>
        <translation>Un mot-vedette qui ne diffère que par la casse d'un autre mot-vedette avec la même catégorie grammaticale ({sourcePOSabbrev}) a été rencontré. Ce sens est ignoré. Mot-vedette source : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="453"/>
        <source>Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Sens ignoré car la catégorie grammaticale cible est indéfinie pour le mot-vedette cible : {targetHeadWord} lors du traitement du mot-vedette source : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="455"/>
        <source>Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}</source>
        <translation>Sens ignoré car il est de cette classe : {className} pour le mot-vedette cible : {targetHeadWord} lors du traitement du mot-vedette source : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="463"/>
        <source>Skipping sense that is of class: {className} for headword: {rawHeadWord}</source>
        <translation>Sens ignoré car il est de la classe : {className} pour le mot-vedette : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="465"/>
        <source>Skipping sense, no analysis object for headword: {rawHeadWord}</source>
        <translation>Sens ignoré, aucun objet d'analyse pour le mot-vedette : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="488"/>
        <source>No lexeme form. Skipping. Headword: {rawHeadWord}</source>
        <translation>Aucune forme de lexème. Ignoré. Mot-vedette : {rawHeadWord}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="497"/>
        <source>No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}</source>
        <translation>Aucun type morphologique. Ignoré. {rawHeadWord} Meilleur vernaculaire : {vernString}</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="523"/>
        <source>There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.</source>
        <translation>Il y a un problème avec le fichier de remplacement du dictionnaire bilingue : {replFile}. Veuillez vérifier le paramètre du fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="550"/>
        <source>There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.</source>
        <translation>Il y a eu un problème lors de la création du fichier de sortie du dictionnaire bilingue : {fullPathBilingFile}. Veuillez vérifier le paramètre du fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="554"/>
        <source>Creation complete to the file: {filePath}.</source>
        <translation>Création terminée dans le fichier : {filePath}.</translation>
    </message>
    <message>
        <location filename="../ExtractBilingualLexicon.py" line="555"/>
        <source>{recordsDumpedCount} records created.</source>
        <translation>{recordsDumpedCount} enregistrements créés.</translation>
    </message>
</context>
</TS>
