<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Attributes" match="def-attr" use="@n"/>
    <xsl:key name="Variables" match="def-var" use="@n"/>
    <xsl:key name="Macros" match="def-macro" use="@n"/>
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Korrekte Attribute</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warnung: Das Attribut (pos) ist keine gültige Zahl. Es muss eine ganze Zahl sein.</report>
        </rule>
        <rule context="@link-to">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warnung: Das Attribut link-to ist keine gültige Zahl. Es muss eine ganze Zahl sein.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='lemh' and .!='lemq' and .!='whole'">Warnung: Das Attribut part muss entweder auf einen gültigen Attributnamen verweisen oder den Wert 'lem', 'lemh', 'lemq' oder 'whole' haben.</report>
        </rule>
        <rule context="@namefrom">
            <report test="name(key('Variables',.))!='def-var'">Warnung: Das Attribut namefrom muss auf einen gültigen Variablennamen verweisen.</report>
        </rule>
    </pattern>
    <pattern id="clipInRule">
        <title>
            <dir value="ltr">Passendes clip/@pos in einer Regel</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">Passendes clip/@pos in einem Makro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>

    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">Passendes with-param/@pos in einer Regel</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">Passendes with-param/@pos in einem Makro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>
    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">Passendes get-case-from/@pos in einer Regel</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">Passendes get-case-from/@pos in einem Makro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>    
    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">Passendes case-of/@pos in einer Regel</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">Passendes case-of/@pos in einem Makro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>

    <pattern id="bInRule">
        <title>
            <dir value="ltr">Passendes b/@pos in einer Regel</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warnung: Das Attribut (pos) verweist auf ein nicht existierendes pattern-item in dieser Regel.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">Passendes b/@pos in einem Makro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warnung: Das Attribut (pos) verweist auf einen nicht existierenden Parameter.</report>
        </rule>
    </pattern>
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">Passendes clip/@link-to in einer Chunk-Lexikoneinheit</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Warnung: Das Attribut link-to verweist auf ein nicht existierendes tag in diesem Chunk.</report>
        </rule>
    </pattern>
</schema>
