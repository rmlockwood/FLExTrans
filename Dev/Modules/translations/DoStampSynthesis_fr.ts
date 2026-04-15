<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
  <context>
    <name>DoStampSynthesis</name>
    <message>
      <location filename="../DoStampSynthesis.py" line="182"/>
      <source>This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the &apos;Build&apos; folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the source project is being used. Actually the target project is being used.</source>
      <translation>Ce module exécute STAMP pour créer le texte synthétisé.
Avant de créer le texte synthétisé, ce module extrait les fichiers du lexique de la langue cible, un pour chacun des racines, préfixes, suffixes et infixes. Ils sont au format STAMP pour la synthèse. Les fichiers du lexique sont placés dans le dossier désigné dans les Paramètres comme Dossier de fichiers du lexique cible. Habituellement, c'est le dossier 'Build'.
Le texte synthétisé sera stocké dans le fichier spécifié par le paramètre Fichier de synthèse de sortie cible.
Cela s'appelle généralement target_text-syn.txt et se trouve habituellement dans le dossier Output.
REMARQUE : Les messages indiqueront que le projet source est utilisé. En réalité, c'est le projet cible qui est utilisé.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="191"/>
      <source>Synthesize Text with STAMP</source>
      <translation>Synthétiser le texte avec STAMP</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="194"/>
      <source>Synthesizes the target text with the tool STAMP.</source>
      <translation>Synthétise le texte cible avec l'outil STAMP.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="921"/>
      <source>Null grapheme found for natural class: {natClassName}. Skipping.</source>
      <translation>Graphème nul trouvé pour la classe naturelle : {natClassName}. Ignoré.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="963"/>
      <source>Aborting target lexicon export because the custom XAMPLE field is not a list. When you define the custom XAMPLE field, it must be a list.</source>
      <translation>Abandon de l'exportation du lexique cible car le champ XAMPLE personnalisé n'est pas une liste. Lorsque vous définissez le champ XAMPLE personnalisé, il doit être une liste.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="974"/>
      <source>Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.</source>
      <translation>Sens ignoré car la forme du lexème est inconnue : lors du traitement de l'entrée de dictionnaire : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="982"/>
      <source>Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.</source>
      <translation>Sens ignoré car le type du morphème est inconnu : lors du traitement de l'entrée de dictionnaire : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1066"/>
      <source>Skipping sense because the POS is unknown: while processing target headword: {headword}.</source>
      <translation>Saut de la sens car le POS est inconnu : lors du traitement du mot principal cible : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1069"/>
      <source>Skipping sense that is of class: {className} for headword: {headword}.</source>
      <translation>Saut de la sens qui est de classe : {className} pour le mot principal : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1072"/>
      <source>Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.</source>
      <translation>Saut de la sens qui n'a pas d'analyse morphosyntaxique. Mot principal : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1092"/>
      <source>No gloss. Skipping. Headword: {headword}.</source>
      <translation>Pas de gloss. Ignoré. Mot principal : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1096"/>
      <source>No lexeme form. Skipping. Headword: {headword}.</source>
      <translation>Pas de forme de lexème. Ignoré. Mot principal : {headword}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1100"/>
      <source>No Morph Type. Skipping. {headword} Best Vern: {vernacular}.</source>
      <translation>Pas de type de morphème. Ignoré. {headword} Meilleur Vern: {vernacular}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1110"/>
      <source>Skipping entry since the lexeme is of type: {className}.</source>
      <translation>Saut de l'entrée car le lexème est de type : {className}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1196"/>
      <source>Skipping entry because the morph type is: {morphType}.</source>
      <translation>Saut de l'entrée car le type de morphème est : {morphType}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1132"/>
      <source>STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.</source>
      <translation>Dictionnaires STAMP créés : {roots} racines, {prefixes} préfixes, {suffixes} suffixes et {infixes} infixes.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1367"/>
      <source>Configuration file problem.</source>
      <translation>Problème avec le fichier de configuration.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1211"/>
      <source>Configuration file problem with TargetProject.</source>
      <translation>Problème avec le fichier de configuration pour TargetProject.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1382"/>
      <source>Configuration file problem with {folder}.</source>
      <translation>Problème avec le fichier de configuration pour {folder}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1387"/>
      <source>Lexicon files folder: {folder} does not exist.</source>
      <translation>Le dossier des fichiers de lexique : {folder} n'existe pas.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1231"/>
      <source>Configuration file problem with {cacheData}.</source>
      <translation>Problème avec le fichier de configuration pour {cacheData}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1238"/>
      <source>The target project does not exist. Please check the configuration file.</source>
      <translation>Le projet cible n'existe pas. Veuillez vérifier le fichier de configuration.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1243"/>
      <source>Problem accessing the target project.</source>
      <translation>Problème d'accès au projet cible.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1248"/>
      <source>Failed to open the target project.</source>
      <translation>Échec de l'ouverture du projet cible.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1254"/>
      <source>Target lexicon files are up to date.</source>
      <translation>Les fichiers de lexique cible sont à jour.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1415"/>
      <source>The synthesized target text is in the file: {filePath}.</source>
      <translation>Le texte cible synthétisé se trouve dans le fichier : {filePath}.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1416"/>
      <source>Synthesis complete.</source>
      <translation>Synthèse terminée.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1408"/>
      <source>An error happened when running the STAMP tool.</source>
      <translation>An error happened when running the STAMP tool.</translation>
    </message>
    <message>
      <location filename="../DoStampSynthesis.py" line="1439"/>
      <source>The {modname} module must be run before this module. The file: ...\{filePath} does not exist.</source>
      <translation>The {modname} module must be run before this module. The file: ...\{filePath} does not exist.</translation>
    </message>
  </context>
</TS>
