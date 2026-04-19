<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
<context>
    <name>GenerateParses</name>
    <message>
        <location filename="../GenerateParses.py" line="103"/>
        <source>Generate All Parses</source>
        <translation>Générer toutes les analyses</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="106"/>
        <source>Creates all possible parses from a FLEx project, in Apertium format.</source>
        <translation>Crée toutes les analyses possibles à partir d'un projet FLEx, au format Apertium.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="108"/>
        <source>This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn&apos;t generate based on derivation information in the project and it doesn&apos;t yet handle
clitics or variants.)
In FLExTrans &gt; Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.</source>
        <translation>Ce module crée un fichier Apertium (qui peut être converti pour l'entrée dans un processus de synthétiseur) avec
toutes les analyses qui peuvent être générées à partir du projet FLEx cible, en fonction de ses modèles flexionnels.
(Il ne génère pas à partir des informations de dérivation dans le projet et il ne gère pas encore
les clitiques ou les variantes.)
Dans FLExTrans &gt; Paramètres, sous les paramètres de test de synthèse, il est possible de limiter la sortie à
une seule catégorie grammaticale ou forme de citation, ou à un nombre spécifié de radicaux (les radicaux seront choisis
aléatoirement). Ce module produit également une version lisible par l'homme des analyses (avec les gloses des racines
et des affixes) dans le fichier de sortie des analyses spécifié dans les paramètres.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="171"/>
        <source>No tags found for slot {slotName} of template {templateName}. Skipping.</source>
        <translation>Aucune étiquette trouvée pour l'emplacement {slotName} du modèle {templateName}. Ignoré.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="245"/>
        <source>  Not adding Inactive template {templateName} for Category {categoryAbbrev}</source>
        <translation>  Modèle inactif {templateName} non ajouté pour la catégorie {categoryAbbrev}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="249"/>
        <source>  Adding template {templateName} for Category {categoryAbbrev}</source>
        <translation>  Ajout du modèle {templateName} pour la catégorie {categoryAbbrev}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="317"/>
        <source>Logging to {logFile}</source>
        <translation>Journalisation dans {logFile}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="319"/>
        <source>There was a problem creating the log file: {logFile}.</source>
        <translation>Il y a eu un problème lors de la création du fichier journal : {logFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="324"/>
        <source>  No focus POS. Please select at least one POS with a template.</source>
        <translation>  Aucune catégorie grammaticale ciblée. Veuillez sélectionner au moins une catégorie grammaticale avec un modèle.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="330"/>
        <source>  Only collecting templates for these POS: {focusPOS}</source>
        <translation>  Collecte des modèles uniquement pour ces catégories grammaticales : {focusPOS}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="334"/>
        <source>Collecting templates from FLEx project...</source>
        <translation>Collecte des modèles du projet FLEx...</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="345"/>
        <source>  Not limiting number of stems</source>
        <translation>  Pas de limitation du nombre de radicaux</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="348"/>
        <source>  Only generating on the first {maxStems} stems</source>
        <translation>  Génération uniquement sur les {maxStems} premiers radicaux</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="353"/>
        <source>Processing entries</source>
        <translation>Traitement des entrées</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="383"/>
        <source>  Only generating on stem [{lex}]
</source>
        <translation>  Génération uniquement sur le radical [{lex}]
</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="393"/>
        <source>  Skipping Variant with {count} Senses: {lex}</source>
        <translation>  Variante ignorée avec {count} sens : {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="426"/>
        <source>  Adding [{thisGloss}]{lex}&lt;{pos}&gt; to roots list</source>
        <translation>  Ajout de [{thisGloss}]{lex}&lt;{pos}&gt; à la liste des racines</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="430"/>
        <source>Using NoGloss as the gloss for {lex}.</source>
        <translation>Utilisation de NoGloss comme glose pour {lex}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="451"/>
        <source>Skipping deriv MSA for {lex}</source>
        <translation>MSA de dérivation ignoré pour {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="505"/>
        <source>MSA missing POS in {lexForm} {lex}</source>
        <translation>MSA sans catégorie grammaticale dans {lexForm} {lex}</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="508"/>
        <source>POS msaPOS missing Abbreviation label</source>
        <translation>POS msaPOS sans étiquette d'abréviation</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="513"/>
        <source>      Adding affix {lexForm} {lex} to slot [{slotName}]</source>
        <translation>      Ajout de l'affixe {lexForm} {lex} à l'emplacement [{slotName}]</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="517"/>
        <source>Morph type {morphType} ignored.</source>
        <translation>Type morphologique {morphType} ignoré.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="524"/>
        <source>Finished collecting templates. Now generating words.</source>
        <translation>Collecte des modèles terminée. Génération des mots en cours.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="541"/>
        <source>There was a problem creating the Apertium file: {aperFile}.</source>
        <translation>Il y a eu un problème lors de la création du fichier Apertium : {aperFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="549"/>
        <source>There was a problem creating the words file: {outFile}.</source>
        <translation>Il y a eu un problème lors de la création du fichier de mots : {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="577"/>
        <source>{wrdcnt} words generated.</source>
        <translation>{wrdcnt} mots générés.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="580"/>
        <source>Creation complete to the file: {outFile}.</source>
        <translation>Création terminée dans le fichier : {outFile}.</translation>
    </message>
    <message>
        <location filename="../GenerateParses.py" line="581"/>
        <source>{wrdCount} words generated.</source>
        <translation>{wrdCount} mots générés.</translation>
    </message>
</context>
</TS>
