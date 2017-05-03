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
            <xsl:copy-of
                    select="*[not(self::name) and not(self::create) and not(self::overwrite) and not(self::charset) and not(self::table)]"/>
        </database>
    </xsl:template>

    <xsl:template match="table">
        <table>
            <!-- name has to appear before declaration -->
            <xsl:copy-of select="declaration/preceding-sibling::name"/>
            <xsl:copy-of select="create"/>
            <xsl:copy-of select="overwrite"/>
            <xsl:copy-of select="charset"/>
            <xsl:apply-templates select="declaration"/>
            <xsl:copy-of select="declaration/following-sibling::name"/>
            <xsl:copy-of
                    select="*[not(self::name) and not(self::create) and not(self::overwrite) and not(self::charset) and not(self::declaration)]"/>
        </table>
    </xsl:template>

    <xsl:template match="declaration">
        <declaration>
            <xsl:apply-templates select="field"/>
            <xsl:apply-templates select="index"/>
            <xsl:copy-of select="*[not(self::field) and not(self::index)]"/>
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
            <xsl:copy-of
                    select="*[not(self::name) and not(self::type) and not(self::length) and not(self::unsigned) and not(self::notnull) and not(self::autoincrement) and not(self::default) and not(self::comments) and not(self::primary) and not(self::precision) and not(self::scale)]"/>
        </field>
    </xsl:template>

    <xsl:template match="index">
        <index>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="primary"/>
            <xsl:copy-of select="unique"/>
            <xsl:apply-templates select="field" mode="index"/>
            <xsl:copy-of
                    select="*[not(self::name) and not(self::primary) and not(self::unique) and not(self::field)]"/>
        </index>
    </xsl:template>

    <xsl:template match="field" mode="index">
        <field>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="sorting"/>
            <xsl:copy-of select="*[not(self::name) and not(self::sorting)]"/>
        </field>
    </xsl:template>
</xsl:stylesheet>
