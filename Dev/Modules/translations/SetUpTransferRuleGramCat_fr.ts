<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en">
<context>
    <name>SetUpTransferRuleGramCat</name>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="102"/>
        <source>Set Up Transfer Rule Categories and Attributes</source>
        <translation>Configurer les catégories et attributs de règles de transfert</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="105"/>
        <source>Set up the transfer rule file with categories and attributes from source and target FLEx projects.</source>
        <translation>Configurer le fichier de règles de transfert avec les catégories et attributs des projets FLEx source et cible.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="107"/>
        <source>This module first goes through both the source and target FLEx projects and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.</source>
        <translation>Ce module parcourt d'abord les projets FLEx source et cible et extrait
les listes de catégories grammaticales. Il remplacera ce qui est actuellement listé pour les
balises de l'attribut a_gram_cat avec les listes extraites. Les catégories en double
seront supprimées. De plus, les conventions de nommage seront suivies comme dans le lexique
bilingue. C'est-à-dire que les espaces sont convertis en traits de soulignement, les points et barres obliques sont supprimés.
Ce module remplira également la section des catégories du fichier de règles de transfert avec
les catégories grammaticales du projet FLEx source. Ce module créera également des
attributs dans le fichier de règles de transfert à partir des caractéristiques d'inflexion FLEx, des classes d'inflexion
et des emplacements de modèle. Vous pouvez décider lesquels sont utilisés et si les attributs existants
doivent être écrasés.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="536"/>
        <source>There was a problem finding the transfer rules file. Check your configuration.</source>
        <translation>Il y a eu un problème pour trouver le fichier de règles de transfert. Vérifiez votre configuration.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="548"/>
        <source>The transfer rules file is malformed or not valid XML.</source>
        <translation>Le fichier de règles de transfert est mal formé ou n'est pas un XML valide.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="558"/>
        <source>The transfer rules file is missing required sections.</source>
        <translation>Le fichier de règles de transfert manque des sections requises.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="593"/>
        <source>There was a problem writing the transfer rules file: {error}</source>
        <translation>Il y a eu un problème lors de l'écriture du fichier de règles de transfert : {error}</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="596"/>
        <source>{attrCount} attributes added to the attributes section.</source>
        <translation>{attrCount} attributs ajoutés à la section des attributs.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="597"/>
        <source>{num} categories created for the a_gram_cat attribute.</source>
        <translation>{num} catégories créées pour l'attribut a_gram_cat.</translation>
    </message>
    <message>
        <location filename="../SetUpTransferRuleGramCat.py" line="598"/>
        <source>{catCount} categories added to the categories section.</source>
        <translation>{catCount} catégories ajoutées à la section des catégories.</translation>
    </message>
</context>
</TS>
