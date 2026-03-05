<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Attributes" match="def-attr" use="@n"/>
    <xsl:key name="Variables" match="def-var" use="@n"/>
    <xsl:key name="Macros" match="def-macro" use="@n"/>
    <pattern id="def-cat-n-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans def-cat/@n</dir>
        </title>
        <rule context="def-cat">
            <report test="contains(@n, ' ')">
                Erreur : Ce nom de catégorie ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-tags-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans cat-item/@tags</dir>
        </title>
        <rule context="cat-item">
            <report test="contains(@tags, ' ')">
                Erreur : Cette définition d'étiquettes ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-lemma-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans cat-item/@lemma</dir>
        </title>
        <rule context="cat-item">
            <report test="@lemma and (normalize-space(@lemma) != @lemma)">
                Erreur : Cette définition de lemme ne peut avoir d'espaces précédents ou suivants. De plus, les doubles espaces médiaux ne sont pas autorisés.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-attr-n-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans def-attr/@n</dir>
        </title>
        <rule context="def-attr">
            <report test="contains(@n, ' ')">
                Erreur : Ce nom d'attribut ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="attr-item-tags-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans attr-item/@tags</dir>
        </title>
        <rule context="attr-item">
            <report test="contains(@tags, ' ')">
                Erreur : Cette définition d'étiquettes ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-var-n-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans def-var/@n</dir>
        </title>
        <rule context="def-var">
            <report test="contains(@n, ' ')">
                Erreur : Cette définition de variable ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-list-n-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans def-list/@n</dir>
        </title>
        <rule context="def-list">
            <report test="contains(@n, ' ')">
                Erreur : Ce nom de liste ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="list-item-v-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans list-item/@v</dir>
        </title>
        <rule context="list-item">
            <report test="@v and (normalize-space(@v) != @v)">
                Erreur : Cet élément de liste ne peut avoir d'espaces précédents ou suivants. De plus, les doubles espaces médiaux ne sont pas autorisés.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-macro-n-no-spaces">
        <title>
            <dir value="ltr">Pas d'espaces dans def-macro/@n</dir>
        </title>
        <rule context="def-macro">
            <report test="contains(@n, ' ')">
                Erreur : Ce nom de macro ne peut contenir aucun espace.
            </report>
        </rule>
    </pattern>    
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Attributs bien formés</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Avertissement : L'attribut élément (pos) n'est pas un nombre valide. Il doit être un entier.</report>
        </rule>
        <rule context="@link-to">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Avertissement : L'attribut link-to n'est pas un nombre valide. Il doit être un entier.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='lemh' and .!='lemq' and .!='whole'">Avertissement : L'attribut part doit soit faire référence à un nom d'attribut valide, soit avoir une valeur de 'lem', 'lemh', 'lemq' ou 'whole'.</report>
        </rule>
        <rule context="@namefrom">
            <report test="name(key('Variables',.))!='def-var'">Avertissement : L'attribut namefrom doit faire référence à un nom de variable valide.</report>
        </rule>
    </pattern>
    <pattern id="clipInRule">
        <title>
            <dir value="ltr">Clip/@pos approprié dans une règle</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Avertissement : l'attribut élément (pos) fait référence à un pattern-item inexistant dans cette règle.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">Clip/@pos approprié dans une macro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Avertissement : l'attribut élément (pos) fait référence à un paramètre inexistant.</report>
        </rule>
    </pattern>

    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">With-param/@pos approprié dans une règle</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Avertissement : l'attribut élément (pos) fait référence à un pattern-item inexistant dans cette règle.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">With-param/@pos approprié dans une macro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Avertissement : l'attribut élément (pos) fait référence à un paramètre inexistant.</report>
        </rule>
    </pattern>
    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">Get-case-from/@pos approprié dans une règle</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Avertissement : l'attribut élément (pos) fait référence à un pattern-item inexistant dans cette règle.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">Get-case-from/@pos approprié dans une macro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Avertissement : l'attribut élément (pos) fait référence à un paramètre inexistant.</report>
        </rule>
    </pattern>    
    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">Case-of/@pos approprié dans une règle</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Avertissement : l'attribut élément (pos) fait référence à un pattern-item inexistant dans cette règle.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">Case-of/@pos approprié dans une macro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Avertissement : l'attribut élément (pos) fait référence à un paramètre inexistant.</report>
        </rule>
    </pattern>

    <pattern id="bInRule">
        <title>
            <dir value="ltr">B/@pos approprié dans une règle</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Avertissement : l'attribut élément (pos) fait référence à un pattern-item inexistant dans cette règle.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">B/@pos approprié dans une macro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Avertissement : l'attribut élément (pos) fait référence à un paramètre inexistant.</report>
        </rule>
    </pattern>
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">Clip/@link-to approprié dans une unité lexicale de morceau</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Avertissement : l'attribut link-to fait référence à une étiquette inexistante dans ce morceau.</report>
        </rule>
    </pattern>
</schema>
