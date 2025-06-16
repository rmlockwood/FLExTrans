<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Attributes" match="def-attr" use="@n"/>
    <xsl:key name="Variables" match="def-var" use="@n"/>
    <xsl:key name="Macros" match="def-macro" use="@n"/>
    <pattern id="def-cat-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-cat/@n</dir>
        </title>
        <rule context="def-cat">
            <report test="contains(@n, ' ')">
                Fehler: Dieser Kategoriename darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@tags</dir>
        </title>
        <rule context="cat-item">
            <report test="contains(@tags, ' ')">
                Fehler: Diese Tag-Definition darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-lemma-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@lemma</dir>
        </title>
        <rule context="cat-item">
            <report test="@lemma and (normalize-space(@lemma) != @lemma)">
                Fehler: Die Lemma-Definition darf keine führenden oder abschließenden Leerzeichen haben.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-attr-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-attr/@n</dir>
        </title>
        <rule context="def-attr">
            <report test="contains(@n, ' ')">
                Fehler: Dieser Attributname darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="attr-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in attr-item/@tags</dir>
        </title>
        <rule context="attr-item">
            <report test="contains(@tags, ' ')">
                Fehler: Diese Tag-Definition darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-var-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-var/@n</dir>
        </title>
        <rule context="def-var">
            <report test="contains(@n, ' ')">
                Fehler: Diese Variablendefinition darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-list-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-list/@n</dir>
        </title>
        <rule context="def-list">
            <report test="contains(@n, ' ')">
                Fehler: Dieser Listenname darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="list-item-v-no-spaces">
        <title>
            <dir value="ltr">No spaces in list-item/@v</dir>
        </title>
        <rule context="list-item">
            <report test="@v and (normalize-space(@v) != @v)">
                Fehler: Dieses Listenelement darf keine führenden oder abschließenden Leerzeichen haben.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-macro-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-macro/@n</dir>
        </title>
        <rule context="def-macro">
            <report test="contains(@n, ' ')">
                Fehler: Dieser Makroname darf keine Leerzeichen enthalten.
            </report>
        </rule>
    </pattern>    
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Well-formed attributes</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warnung: Das Attribut item (pos) ist keine gültige Zahl. Es muss eine ganze Zahl sein.</report>
        </rule>
        <rule context="@link-to">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warnung: Das Attribut link-to ist keine gültige Zahl. Es muss eine ganze Zahl sein.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='lemh' and .!='lemq' and .!='whole'">Warnung: Das Attribut part muss auf einen gültigen Attributnamen verweisen oder den Wert 'lem', 'lemh', 'lemq' oder 'whole' haben.</report>
        </rule>
        <rule context="@namefrom">
            <report test="name(key('Variables',.))!='def-var'">Warnung: Das Attribut namefrom muss auf einen gültigen Variablennamen verweisen.</report>
        </rule>
    </pattern>
    <pattern id="clipInRule">
        <title>
            <dir value="ltr">Appropriate clip/@pos in a rule</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut item (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">Appropriate clip/@pos in a macro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut item (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a rule</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut item (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a macro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut item (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a rule</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut item (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a macro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut item (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a rule</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut item (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a macro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut item (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>
    <pattern id="bInRule">
        <title>
            <dir value="ltr">Appropriate b/@pos in a rule</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut item (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">Appropriate b/@pos in a macro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut item (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">Appropriate clip/@link-to in a chunk lexical unit</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Warnung: Das Attribut link-to verweist auf ein nicht existierendes Tag in diesem Chunk.</report>
        </rule>
    </pattern>
</schema>
