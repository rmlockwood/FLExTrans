<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="Symbols" match="sdef" use="@n"/>
    <pattern id="SymbolExists">
        <title>
            <dir value="ltr">Well-formed symbols</dir>
        </title>
        <rule context="@s">
            <report test="name(key('Symbols',.))!='sdef'">Warning: The symbol attribute must refer to a valid symbol name.</report>
        </rule>
    </pattern>
</schema>

