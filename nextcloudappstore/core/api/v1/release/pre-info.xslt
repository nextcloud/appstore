<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/info">
        <info>
            <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'" />
            <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

            <!-- reformat info.xml to have everything in order and excluded unknown elements -->
            <xsl:copy-of select="id"/>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="summary"/>
            <xsl:if test="not(summary)">
                <summary><xsl:value-of select="description"/></summary>
            </xsl:if>
            <xsl:copy-of select="description"/>
            <xsl:copy-of select="version"/>
            <xsl:for-each select="licence">
                <licence>
                    <xsl:value-of select="translate(., $uppercase, $lowercase)"/>
                </licence>
            </xsl:for-each>
            <xsl:copy-of select="author"/>
            <xsl:copy-of select="namespace"/>
            <xsl:apply-templates select="types"/>
            <xsl:apply-templates select="documentation"/>
            <xsl:if test="not(category)">
                <category>tools</category>
            </xsl:if>
            <xsl:copy-of select="category"/>
            <xsl:copy-of select="website"/>
            <xsl:copy-of select="bugs"/>
            <xsl:copy-of select="repository"/>
            <xsl:copy-of select="discussion"/>
            <xsl:copy-of select="screenshot"/>
            <xsl:apply-templates select="dependencies"/>
        </info>
    </xsl:template>

    <xsl:template match="documentation">
        <documentation>
            <xsl:copy-of select="user"/>
            <xsl:copy-of select="admin"/>
            <xsl:copy-of select="developer"/>
        </documentation>
    </xsl:template>

    <xsl:template match="types">
        <types>
            <xsl:copy-of select="prelogin"/>
            <xsl:copy-of select="filesystem"/>
            <xsl:copy-of select="authentication"/>
            <xsl:copy-of select="logging"/>
            <xsl:copy-of select="prevent_group_restriction"/>
        </types>
    </xsl:template>

    <xsl:template match="dependencies">
        <dependencies>
            <xsl:copy-of select="php"/>
            <xsl:copy-of select="database"/>
            <xsl:copy-of select="command"/>
            <xsl:copy-of select="lib"/>
            <xsl:copy-of select="owncloud"/>
        </dependencies>
    </xsl:template>
</xsl:stylesheet>
