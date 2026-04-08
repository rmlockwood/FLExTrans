<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>DoHermitCrabSynthesis</name>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="148"/>
        <source>Synthesize Text with HermitCrab</source>
        <translation>Synthétiser le texte avec HermitCrab</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="151"/>
        <source>Synthesizes the target text with the tool HermitCrab.</source>
        <translation>Synthétise le texte cible avec l'outil HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="153"/>
        <source>This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like 'target_text-syn.txt'. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named 'HermitCrab.config' and will be in the 'Build' folder. 
NOTE: Messages will say the source project
is being used. Actually the target project is being used.
Advanced Information: This module runs HermitCrab against a list of target parses ('target_words-parses.txt') to
produce surface forms ('target_words-surface.txt'). 
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
        <location filename="../DoHermitCrabSynthesis.py" line="205"/>
        <source>Configuration file problem with TargetProject.</source>
        <translation>Problème de fichier de configuration avec TargetProject.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="216"/>
        <source>Failed to open the target project: {targetProj}.</source>
        <translation>Échec de l'ouverture du projet cible : {targetProj}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="225"/>
        <source>A value for {cacheData} not found in the configuration file.</source>
        <translation>Une valeur pour {cacheData} non trouvée dans le fichier de configuration.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="256"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)</source>
        <translation>Une erreur s'est produite lors du chargement du fichier de configuration HermitCrab pour l'objet HC Synthesis. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="248"/>
        <source>An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}</source>
        <translation>Une exception s'est produite lors de la tentative d'obtention du fichier XML HermitCrab depuis l'objet DLL : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="298"/>
        <source>An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative de définition du fichier XML HermitCrab dans l'objet DLL. Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="264"/>
        <source>The HermitCrab configuration file is up to date.</source>
        <translation>Le fichier de configuration HermitCrab est à jour.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="274"/>
        <source>Generated the HermitCrab config. file: {filePath}.</source>
        <translation>Fichier de configuration HermitCrab généré : {filePath}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="303"/>
        <source>An error happened when running the Generate HermitCrab Configuration tool.</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil Générer la configuration HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="281"/>
        <source>The error contains a 'KeyNotFoundException' and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.</source>
        <translation>L'erreur contient une 'KeyNotFoundException' et cela indique souvent que l'utilitaire FLEx Rechercher et Réparer devrait être exécuté sur le projet {projectName}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="282"/>
        <source>The full error message is:</source>
        <translation>Le message d'erreur complet est :</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="293"/>
        <source>An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)</source>
        <translation>Une erreur s'est produite lors du chargement du fichier de configuration HermitCrab pour l'objet HC Synthesis. Cela s'est produit après la génération du fichier de configuration. (DLL)</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="333"/>
        <source>There was an error opening the HermitCrab surface forms file.</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier de formes de surface HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="342"/>
        <source>The file: {transferResultsFile} was not found. Did you run the {runApertium} module?</source>
        <translation>Le fichier : {transferResultsFile} n'a pas été trouvé. Avez-vous exécuté le module {runApertium} ?</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="357"/>
        <source>The number of surface forms does not match the number of Lexical Units.</source>
        <translation>Le nombre de formes de surface ne correspond pas au nombre d'unités lexicales.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="387"/>
        <source>Synthesis failed. ({saveStr})</source>
        <translation>Échec de la synthèse. ({saveStr})</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="411"/>
        <source>Error writing the file: {synFile}.</source>
        <translation>Erreur lors de l'écriture du fichier : {synFile}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="428"/>
        <source>There was an error opening the HermitCrab master file. Do you have the setting &quot;Use HermitCrab Synthesis&quot; turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier maître HermitCrab. Avez-vous activé le paramètre &quot;Utiliser la synthèse HermitCrab&quot; ? Avez-vous exécuté le module Convertir le texte au format du synthétiseur ? Fichier : {parsesFile}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="437"/>
        <source>There was an error opening the HermitCrab parses file.</source>
        <translation>Une erreur s'est produite lors de l'ouverture du fichier d'analyses HermitCrab.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="452"/>
        <source>Malformed Lexical Unit in HermitCrab master file skipping this line: {line}</source>
        <translation>Unité lexicale mal formée dans le fichier maître HermitCrab, cette ligne est ignorée : {line}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="648"/>
        <source>Unable to open the HC master file.</source>
        <translation>Impossible d'ouvrir le fichier maître HC.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="674"/>
        <source>An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Une erreur s'est produite lors de la définition du fichier de gloses pour l'outil HermitCrab Synthétiser par glose (DLL).</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="679"/>
        <source>An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative de définition du fichier de gloses pour l'outil HermitCrab Synthétiser par glose (DLL). Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="685"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil HermitCrab Synthétiser par glose (DLL).</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="690"/>
        <source>An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}</source>
        <translation>Une exception s'est produite lors de la tentative d'exécution (en appelant Process) de l'outil HermitCrab Synthétiser par glose (DLL). Erreur : {e}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="710"/>
        <source>An error happened when running the HermitCrab Synthesize By Gloss tool.</source>
        <translation>Une erreur s'est produite lors de l'exécution de l'outil HermitCrab Synthétiser par glose.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="723"/>
        <source>An error happened when trying to open the file: {parsesFile}</source>
        <translation>Une erreur s'est produite lors de la tentative d'ouverture du fichier : {parsesFile}</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="726"/>
        <source>Processing {LUsCount} unique lexical units.</source>
        <translation>Traitement de {LUsCount} unités lexicales uniques.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="741"/>
        <source>Configuration file problem with the value: {val}.</source>
        <translation>Problème de fichier de configuration avec la valeur : {val}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="756"/>
        <source>The synthesized target text is in the file: {file}.</source>
        <translation>Le texte cible synthétisé se trouve dans le fichier : {file}.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="757"/>
        <source>Synthesis complete.</source>
        <translation>Synthèse terminée.</translation>
    </message>
    <message>
        <location filename="../DoHermitCrabSynthesis.py" line="795"/>
        <source>{master} or {parses} or {surface} or {transfer} not found in the configuration file.</source>
        <translation>{master} ou {parses} ou {surface} ou {transfer} non trouvé dans le fichier de configuration.</translation>
    </message>
</context>
</TS>
