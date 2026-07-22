<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
<context>
    <name>WorkOnRulesWithAI</name>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="49"/>
        <source>This module uses AI to create new Apertium transfer rules or modify existing ones in the transfer rules file. You describe the rule you want; the AI drafts it, it is validated, and you review and approve it before it is written.</source>
        <translation>Ce module utilise l'IA pour créer de nouvelles règles de transfert Apertium ou modifier celles qui existent dans le fichier de règles de transfert. Vous décrivez la règle que vous voulez ; l'IA la rédige, elle est validée, et vous la relisez et l'approuvez avant qu'elle soit écrite.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="50"/>
        <source>AI Rule Studio</source>
        <translation>Studio de règles IA</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="53"/>
        <source>Create or modify Apertium transfer rules with AI assistance.</source>
        <translation>Créer ou modifier des règles de transfert Apertium avec l'aide de l'IA.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="101"/>
        <source>This module sends your rule description, the transfer file's categories, attributes, and the project's grammatical categories, features, and affixes to your configured AI provider ({provider}) to generate transfer rules. Also, if you chose to include example language data, that will be sent as well. Your lexicon entries and texts are not sent (except for what is in the example data). Do you want to allow this?
There is a separate setting for sending FLEx project names.</source>
        <translation>Ce module envoie votre description de la règle, les catégories et les attributs du fichier de transfert, ainsi que les catégories grammaticales, les traits et les affixes du projet à votre fournisseur d'IA configuré ({provider}) pour générer des règles de transfert. De plus, si vous avez choisi d'inclure des données linguistiques d'exemple, celles-ci seront également envoyées. Vos entrées de lexique et vos textes ne sont pas envoyés (sauf ce qui figure dans les données d'exemple). Voulez-vous l'autoriser ?
Il existe un paramètre distinct pour l'envoi des noms des projets FLEx.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="147"/>
        <source>AI rule assistance was declined. No data was sent.</source>
        <translation>L'assistance IA pour les règles a été refusée. Aucune donnée n'a été envoyée.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="139"/>
        <source>Before you can use this module, choose the AI Provider and AI Model in the FLExTrans Settings tool, in the AI Assistant section (shown in the Full view). Then come back to this module; it will ask for your API key.

Do you want to open the Settings tool now?</source>
        <translation>Avant de pouvoir utiliser ce module, choisissez le Fournisseur d'IA et le Modèle d'IA dans l'outil Paramètres de FLExTrans, dans la section Assistant IA (visible dans la vue Complet). Revenez ensuite à ce module ; il vous demandera votre clé API.

Voulez-vous ouvrir l'outil Paramètres maintenant ?</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="161"/>
        <source>No API key provided for {provider}; nothing was done.</source>
        <translation>Aucune clé API fournie pour {provider} ; rien n'a été fait.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="172"/>
        <source>Transfer rules file not found: {path}</source>
        <translation>Fichier de règles de transfert introuvable : {path}</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="182"/>
        <source>Missing WorkOnRulesWithAI-Conventions.md in the Lib/AI subfolder under {libDir}. Reinstall FLExTrans or copy that file there.</source>
        <translation>WorkOnRulesWithAI-Conventions.md manque dans le sous-dossier Lib/AI sous {libDir}. Réinstallez FLExTrans ou copiez ce fichier à cet endroit.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="194"/>
        <source>AI prompt logging is on. Prompts and responses are appended to: {path}</source>
        <translation>La journalisation des prompts IA est activée. Les prompts et les réponses sont ajoutés à : {path}</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="150"/>
        <source>The configured AI model ({model}) goes with {owner}, not {provider}. Fix the AI Model setting in the FLExTrans Settings tool.</source>
        <translation>Le modèle d'IA configuré ({model}) va avec {owner}, pas avec {provider}. Corrigez le paramètre Modèle d'IA dans l'outil Paramètres de FLExTrans.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="223"/>
        <source>Could not open the target FLEx project. Check the target-project setting and try again.</source>
        <translation>Impossible d'ouvrir le projet FLEx cible. Vérifiez le paramètre du projet cible et réessayez.</translation>
    </message>
</context>
</TS>
