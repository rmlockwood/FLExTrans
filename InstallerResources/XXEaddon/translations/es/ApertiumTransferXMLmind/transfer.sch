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
                Error: Este nombre de categoría no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@tags</dir>
        </title>
        <rule context="cat-item">
            <report test="contains(@tags, ' ')">
                Error: Esta definición de etiquetas no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="cat-item-lemma-no-spaces">
        <title>
            <dir value="ltr">No spaces in cat-item/@lemma</dir>
        </title>
        <rule context="cat-item">
            <report test="@lemma and (normalize-space(@lemma) != @lemma)">
                Error: La definición de lema no debe tener espacios al principio ni al final.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-attr-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-attr/@n</dir>
        </title>
        <rule context="def-attr">
            <report test="contains(@n, ' ')">
                Error: Este nombre de atributo no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="attr-item-tags-no-spaces">
        <title>
            <dir value="ltr">No spaces in attr-item/@tags</dir>
        </title>
        <rule context="attr-item">
            <report test="contains(@tags, ' ')">
                Error: Esta definición de etiquetas no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-var-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-var/@n</dir>
        </title>
        <rule context="def-var">
            <report test="contains(@n, ' ')">
                Error: Esta definición de variable no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-list-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-list/@n</dir>
        </title>
        <rule context="def-list">
            <report test="contains(@n, ' ')">
                Error: Este nombre de lista no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="list-item-v-no-spaces">
        <title>
            <dir value="ltr">No spaces in list-item/@v</dir>
        </title>
        <rule context="list-item">
            <report test="@v and (normalize-space(@v) != @v)">
                Error: Este elemento de lista no debe tener espacios al principio ni al final.
            </report>
        </rule>
    </pattern>    
    <pattern id="def-macro-n-no-spaces">
        <title>
            <dir value="ltr">No spaces in def-macro/@n</dir>
        </title>
        <rule context="def-macro">
            <report test="contains(@n, ' ')">
                Error: Este nombre de macro no puede contener espacios.
            </report>
        </rule>
    </pattern>    
    <pattern id="clip.pos">
        <title>
            <dir value="ltr">Well-formed attributes</dir>
        </title>
        <rule context="@pos">
            <report test="string-length(normalize-space(.)) &gt; 0 and string(number(.))='NaN'">Advertencia: El atributo item (pos) no es un número válido. Debe ser un número entero.</report>
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
            <dir value="ltr">Appropriate clip/@pos in a rule</dir>
        </title>
        <rule context="clip[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo item (pos) se refiere a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="clipInMacro">
        <title>
            <dir value="ltr">Appropriate clip/@pos in a macro.</dir>
        </title>
        <rule context="clip[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo item (pos) se refiere a un parámetro inexistente.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInRule">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a rule</dir>
        </title>
        <rule context="with-param[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo item (pos) se refiere a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="with-paramInMacro">
        <title>
            <dir value="ltr">Appropriate with-param/@pos in a macro.</dir>
        </title>
        <rule context="with-param[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo item (pos) se refiere a un parámetro inexistente.</report>
        </rule>
    </pattern>
    
    <pattern id="get-case-fromInRule">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a rule</dir>
        </title>
        <rule context="get-case-from[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo item (pos) se refiere a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="get-case-fromInMacro">
        <title>
            <dir value="ltr">Appropriate get-case-from/@pos in a macro.</dir>
        </title>
        <rule context="get-case-from[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo item (pos) se refiere a un parámetro inexistente.</report>
        </rule>
    </pattern>    
    
    <pattern id="case-ofInRule">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a rule</dir>
        </title>
        <rule context="case-of[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo item (pos) se refiere a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="case-ofInMacro">
        <title>
            <dir value="ltr">Appropriate case-of/@pos in a macro.</dir>
        </title>
        <rule context="case-of[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo item (pos) se refiere a un parámetro inexistente.</report>
        </rule>
    </pattern>

    <pattern id="bInRule">
        <title>
            <dir value="ltr">Appropriate b/@pos in a rule</dir>
        </title>
        <rule context="b[ancestor::rule]">
            <report test="number(@pos) &gt; count(ancestor::rule/pattern/pattern-item)">Advertencia: el atributo item (pos) se refiere a un pattern-item inexistente en esta regla.</report>
        </rule>
    </pattern>
    <pattern id="bInMacro">
        <title>
            <dir value="ltr">Appropriate b/@pos in a macro.</dir>
        </title>
        <rule context="b[ancestor::def-macro]">
            <report test="number(@pos) &gt; ancestor::def-macro/@npar">Advertencia: el atributo item (pos) se refiere a un parámetro inexistente.</report>
        </rule>
    </pattern>
    <pattern id="link-toInTagList">
        <title>
            <dir value="ltr">Appropriate clip/@link-to in a chunk lexical unit</dir>
        </title>
        <rule context="clip[ancestor::chunk/lu]">
            <report test="number(@link-to) &gt; count(ancestor::out/chunk/tags/tag)">Advertencia: el atributo link-to se refiere a una etiqueta inexistente en este chunk.</report>
        </rule>
    </pattern>
</schema>
