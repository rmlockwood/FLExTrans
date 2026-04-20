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
                Error: This category name cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@tags</dir>
        </title>
        <rule context="cat-item">
            <report test="contains(@tags, ' ')">
                Error: This tags definition cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-lemma-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@lemma</dir>
        </title>
        <rule context="cat-item">
            <report test="@lemma and (normalize-space(@lemma) != @lemma)">
                Error: This lemma definition cannot have any preceding or trailing spaces. Also, medial double-spaces are not allowed.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-attr-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-attr/@n</dir>
        </title>
        <rule context="def-attr">
            <report test="contains(@n, ' ')">
                Error: This attribute name cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="attr-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in attr-item/@tags</dir>
        </title>
        <rule context="attr-item">
            <report test="contains(@tags, ' ')">
                Error: This tags definition cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-var-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-var/@n</dir>
        </title>
        <rule context="def-var">
            <report test="contains(@n, ' ')">
                Error: This variable definition cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-list-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-list/@n</dir>
        </title>
        <rule context="def-list">
            <report test="contains(@n, ' ')">
                Error: This list name cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="list-item-v-no-spaces">
        <title>
            <dir value="ltr">No spaces in list-item/@v</dir>
        </title>
        <rule context="list-item">
            <report test="@v and (normalize-space(@v) != @v)">
                Error: This list element cannot have any preceding or trailing spaces. Also, medial double-spaces are not allowed.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-macro-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-macro/@n</dir>
        </title>
        <rule context="def-macro">
            <report test="contains(@n, ' ')">
                Error: This macro name cannot contain any spaces.
            </report>
        </rule>
    </pattern>    
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Well-formed attributes</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warning: The item (pos) attribute is not a valid number.  It must be an integer.</report>
        </rule>
        <rule context="@link-to">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Warning: The link-to attribute is not a valid number.  It must be an integer.</report>
        </rule>
        <rule context="@part">
            <report test="name(key('Attributes',.))!='def-attr' and .!='lem' and .!='lemh' and .!='lemq' and .!='whole'">Warning: The part attribute must either refer to a valid attribute name or have a value of 'lem', 'lemh', 'lemq', or 'whole'.</report>
        </rule>
        <rule context="@namefrom">
            <report test="name(key('Variables',.))!='def-var'">Warning: The namefrom attribute must refer to a valid variable name.</report>
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
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">Appropriate clip/@link-to in a chunk lexical unit</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Warning: the link-to attribute refers to a non-existent tag in this chunk.</report>
        </rule>
    </pattern>
</schema>
