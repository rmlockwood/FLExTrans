<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Attributes" match="def-attr" use="@n"/>
    <xsl:key name="Variables" match="def-var" use="@n"/>
    <xsl:key name="Macros" match="def-macro" use="@n"/>
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Well-formed attributes</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warning: The item (pos) attribute is not a valid number.  It must be an integer.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='leh' and .!='lemq' and .!='whole' and .!='tags' and .!='chcontent'">
            Warning: The part attribute must either refer to a valid attribute name or have a value of 'lem', 'lemh', 'lemq', 'tags', 'chcontent' or 'whole'.
            </report>
        </rule>
    </pattern>
    <pattern id="clipInRule">
        <title>
            <dir value="ltr">Appropriate clip/@pos in a rule</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warning: the item (pos) attribute refers to a non-existent pattern-item in this rule.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">Appropriate clip/@pos in a macro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warning: the item (pos) attribute refers to a non-existent parameter.</report>
        </rule>
    </pattern>

    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a rule</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warning: the item (pos) attribute refers to a non-existent pattern-item in this rule.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a macro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warning: the item (pos) attribute refers to a non-existent parameter.</report>
        </rule>
    </pattern>
    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a rule</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warning: the item (pos) attribute refers to a non-existent pattern-item in this rule.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a macro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warning: the item (pos) attribute refers to a non-existent parameter.</report>
        </rule>
    </pattern>    
    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a rule</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warning: the item (pos) attribute refers to a non-existent pattern-item in this rule.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a macro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warning: the item (pos) attribute refers to a non-existent parameter.</report>
        </rule>
    </pattern>

    <pattern id="bInRule">
        <title>
            <dir value="ltr">Appropriate b/@pos in a rule</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Warning: the item (pos) attribute refers to a non-existent pattern-item in this rule.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">Appropriate b/@pos in a macro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Warning: the item (pos) attribute refers to a non-existent parameter.</report>
        </rule>
    </pattern>
</schema>
