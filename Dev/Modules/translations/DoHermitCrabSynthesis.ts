<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="151"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation>Synthétiser le texte avec HermitCrab</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="154"/>
        <source>Synthesizes the target text with the tool HermitCrab.</source>
        <translation>Synthétise le texte cible avec l'outil HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="156"/>
        <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like &apos;target_text-syn.txt&apos;. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named &apos;HermitCrab.config&apos; and will be in the &apos;Build&apos; folder. 
NOTE: Messages will say the source project
is being used. Actually the target project is being used.
Advanced Information: This module runs HermitCrab against a list of target parses (&apos;target_words-parses.txt&apos;) to
produce surface forms (&apos;target_words-surface.txt&apos;). 
These forms are then used to create the target text.</source>
        <translation>Ce module exécute HermitCrab pour créer le texte synthétisé. Les résultats sont placés dans le fichier désigné dans les Paramètres comme Fichier de synthèse de sortie cible.
Par défaut, ce sera quelque chose comme 'target_text-syn.txt'.
Avant de créer le texte synthétisé, ce module extrait le lexique de la langue cible sous forme de fichier de configuration HermitCrab.
Il se nomme 'HermitCrab.config' et sera dans le dossier 'Build'.
REMARQUE : Les messages indiqueront que le projet source est utilisé. En réalité, c'est le projet cible qui est utilisé.
Informations avancées : Ce module exécute HermitCrab sur une liste d'analyses cibles ('target_words-parses.txt') pour produire des formes de surface ('target_words-surface.txt').
Ces formes sont ensuite utilisées pour créer le texte cible.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="208"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problème de fichier de configuration avec TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="219"/>
        <source>Failed to open the target project: {targetProj}.</source>
        <translation>Échec de l'ouverture du projet cible : {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="228"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation>Une valeur pour {cacheData} non trouvée dans le fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="259"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation>Une erreur s'est produite lors du chargement du fichier de configuration HermitCrab pour l'objet HC Synthesis. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="251"/>
        <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
        <translation>Une exception s'est produite lors de la tentative d'obtention du fichier XML HermitCrab depuis l'objet DLL : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="301"/>
        <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative de définition du fichier XML HermitCrab dans l'objet DLL. Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="267"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation>Le fichier de configuration HermitCrab est à jour.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="277"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation>Fichier de configuration HermitCrab généré : {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="306"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil Générer la configuration HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="284"/>
        <source>The error contains a &apos;KeyNotFoundException&apos; and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.</source>
        <translation>L'erreur contient une 'KeyNotFoundException' et cela indique souvent que l'utilitaire FLEx Rechercher et Réparer devrait être exécuté sur le projet {projectName}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="285"/>
        <source>The full error message is:</source>
        <translation>Le message d'erreur complet est :</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="296"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation>Une erreur s'est produite lors du chargement du fichier de configuration HermitCrab pour l'objet HC Synthesis. Cela s'est produit après la génération du fichier de configuration. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="336"/>
        <source>There was an error opening the HermitCrab surface forms file.</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier de formes de surface HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="345"/>
        <source>The file: {transferResultsFile} was not found. Did you run the {runApertium} module?</source>
        <translation>Le fichier : {transferResultsFile} n'a pas été trouvé. Avez-vous exécuté le module {runApertium} ?</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="360"/>
        <source>The number of surface forms does not match the number of Lexical Units.</source>
        <translation>Le nombre de formes de surface ne correspond pas au nombre d'unités lexicales.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="390"/>
        <source>Synthesis failed. ({saveStr})</source>
        <translation>Échec de la synthèse. ({saveStr})</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="414"/>
        <source>Error writing the file: {synFile}.</source>
        <translation>Erreur lors de l'écriture du fichier : {synFile}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="431"/>
        <source>There was an error opening the HermitCrab master file. Do you have the setting &quot;Use HermitCrab Synthesis&quot; turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier maître HermitCrab. Avez-vous activé le paramètre &quot;Utiliser la synthèse HermitCrab&quot; ? Avez-vous exécuté le module Convertir le texte au format du synthétiseur ? Fichier : {parsesFile}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="440"/>
        <source>There was an error opening the HermitCrab parses file.</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier d'analyses HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="455"/>
        <source>Malformed Lexical Unit in HermitCrab master file skipping this line: {line}</source>
        <translation>Unité lexicale mal formée dans le fichier maître HermitCrab, cette ligne est ignorée : {line}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="651"/>
        <source>Unable to open the HC master file.</source>
        <translation>Impossible d'ouvrir le fichier maître HC.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="677"/>
        <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Une erreur s'est produite lors de la définition du fichier de gloses pour l'outil HermitCrab Synthétiser par glose (DLL).</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="682"/>
        <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative de définition du fichier de gloses pour l'outil HermitCrab Synthétiser par glose (DLL). Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="688"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil HermitCrab Synthétiser par glose (DLL).</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="693"/>
        <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative d'exécution (en appelant Process) de l'outil HermitCrab Synthétiser par glose (DLL). Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="713"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil HermitCrab Synthétiser par glose.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="726"/>
        <source>An error happened when trying to open the file: {parsesFile}</source>
        <translation>Une erreur s'est produite lors de la tentative d'ouverture du fichier : {parsesFile}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="729"/>
        <source>Processing {LUsCount} unique lexical units.</source>
        <translation>Traitement de {LUsCount} unités lexicales uniques.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="744"/>
        <source>Configuration file problem with the value: {val}.</source>
        <translation>Problème de fichier de configuration avec la valeur : {val}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="759"/>
        <source>The synthesized target text is in the file: {file}.</source>
        <translation>Le texte cible synthétisé se trouve dans le fichier : {file}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="760"/>
        <source>Synthesis complete.</source>
        <translation>Synthèse terminée.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="798"/>
        <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
        <translation>{master} ou {parses} ou {surface} ou {transfer} non trouvé dans le fichier de configuration.</translation>
    </message>
</context>
</TS>
