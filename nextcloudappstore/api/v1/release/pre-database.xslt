<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/database">
        <database>
            <!-- reformat database.xml to have everything in order -->
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="create"/>
            <xsl:copy-of select="overwrite"/>
            <xsl:copy-of select="charset"/>
            <xsl:apply-templates select="table"/>
        </database>
    </xsl:template>

    <xsl:template match="table">
        <table>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="create"/>
            <xsl:copy-of select="overwrite"/>
            <xsl:copy-of select="charset"/>
            <xsl:apply-templates select="declaration"/>
        </table>
    </xsl:template>

    <xsl:template match="declaration">
        <declaration>
            <xsl:apply-templates select="field"/>
            <xsl:apply-templates select="index"/>
        </declaration>
    </xsl:template>

    <xsl:template match="field">
        <field>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="type"/>
            <xsl:copy-of select="length"/>
            <xsl:copy-of select="unsigned"/>
            <xsl:copy-of select="notnull"/>
            <xsl:copy-of select="autoincrement"/>
            <xsl:copy-of select="default"/>
            <xsl:copy-of select="comments"/>
            <xsl:copy-of select="primary"/>
            <xsl:copy-of select="precision"/>
            <xsl:copy-of select="scale"/>
        </field>
    </xsl:template>

    <xsl:template match="index">
        <index>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="primary"/>
            <xsl:copy-of select="unique"/>
            <xsl:apply-templates select="field" mode="index"/>
        </index>
    </xsl:template>

    <xsl:template match="field" mode="index">
        <field>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="sorting"/>
        </field>
    </xsl:template>
</xsl:stylesheet>
