<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/release">
        <release>
            <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'" />
            <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

            <!-- reformat info.xml to have everything in order and excluded unknown elements -->
            <xsl:copy-of select="changelog"/>
            <xsl:apply-templates select="whatsNew"/>
        </release>
    </xsl:template>

    <xsl:template match="whatsNew">
        <whatsNew>
            <xsl:if test="@lang">
                <xsl:attribute name="lang">
                        <xsl:value-of select="@lang"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates select="regular"/>
            <xsl:apply-templates select="admin"/>
        </whatsNew>
    </xsl:template>

    <xsl:template match="regular">
        <regular>
            <xsl:copy-of select="item"/>
        </regular>
    </xsl:template>

    <xsl:template match="admin">
        <admin>
            <xsl:copy-of select="item"/>
        </admin>
    </xsl:template>
</xsl:stylesheet>
