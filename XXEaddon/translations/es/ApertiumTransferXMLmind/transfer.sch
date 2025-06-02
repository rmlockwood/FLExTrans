<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Attributes" match="def-attr" use="@n"/>
    <xsl:key name="Variables" match="def-var" use="@n"/>
    <xsl:key name="Macros" match="def-macro" use="@n"/>
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Atributos bien formados</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Advertencia: El atributo (pos) no es un número válido. Debe ser un número entero.</report>
        </rule>
        <rule context="@link-to">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Advertencia: El atributo link-to no es un número válido. Debe ser un número entero.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='lemh' and .!='lemq' and .!='whole'">Advertencia: El atributo part debe referirse a un nombre de atributo válido o tener el valor 'lem', 'lemh', 'lemq' o 'whole'.</report>
        </rule>
        <rule context="@namefrom">
            <report test="name(key('Variables',.))!='def-var'">Advertencia: El atributo namefrom debe referirse a un nombre de variable válido.</report>
        </rule>
    </pattern>
    <pattern id="clipInRule">
        <title>
            <dir value="ltr">clip/@pos apropiado en una regla</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo (pos) hace referencia a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">clip/@pos apropiado en una macro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo (pos) hace referencia a un parámetro inexistente.</report>
        </rule>
    </pattern>

    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">with-param/@pos apropiado en una regla</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo (pos) hace referencia a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">with-param/@pos apropiado en una macro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo (pos) hace referencia a un parámetro inexistente.</report>
        </rule>
    </pattern>
    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">get-case-from/@pos apropiado en una regla</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo (pos) hace referencia a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">get-case-from/@pos apropiado en una macro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo (pos) hace referencia a un parámetro inexistente.</report>
        </rule>
    </pattern>    
    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">case-of/@pos apropiado en una regla</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo (pos) hace referencia a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">case-of/@pos apropiado en una macro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo (pos) hace referencia a un parámetro inexistente.</report>
        </rule>
    </pattern>

    <pattern id="bInRule">
        <title>
            <dir value="ltr">b/@pos apropiado en una regla</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo (pos) hace referencia a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">b/@pos apropiado en una macro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo (pos) hace referencia a un parámetro inexistente.</report>
        </rule>
    </pattern>
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">clip/@link-to apropiado en una unidad léxica de chunk</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Advertencia: el atributo link-to hace referencia a una etiqueta inexistente en este chunk.</report>
        </rule>
    </pattern>
</schema>