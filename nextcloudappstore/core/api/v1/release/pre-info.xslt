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
            <xsl:apply-templates select="category"/>
            <xsl:if test="not(category)">
                <category>tools</category>
            </xsl:if>

            <xsl:copy-of select="website"/>
            <xsl:copy-of select="bugs"/>
            <xsl:copy-of select="repository"/>
            <xsl:copy-of select="screenshot"/>
            <xsl:apply-templates select="dependencies"/>
            <xsl:copy-of select="background-jobs"/>
            <xsl:apply-templates select="repair-steps"/>
            <xsl:copy-of select="two-factor-providers"/>
            <xsl:copy-of select="commands"/>
            <xsl:copy-of select="ocsid"/>
            <xsl:apply-templates select="settings"/>
            <xsl:apply-templates select="activity"/>

            <!-- copy invalid elements to fail if they are present -->
            <xsl:copy-of select="standalone"/>
            <xsl:copy-of select="default_enable"/>
            <xsl:copy-of select="shipped"/>
            <xsl:copy-of select="public"/>
            <xsl:copy-of select="remote"/>
            <xsl:copy-of select="requiremin"/>
            <xsl:copy-of select="requiremax"/>
        </info>
    </xsl:template>

    <xsl:template match="activity">
        <activity>
            <xsl:copy-of select="admin"/>
            <xsl:copy-of select="admin-section"/>
        </activity>
    </xsl:template>

    <xsl:template match="settings">
        <settings>
            <xsl:copy-of select="settings"/>
            <xsl:copy-of select="filters"/>
            <xsl:copy-of select="providers"/>
        </settings>
    </xsl:template>

    <xsl:template match="documentation">
        <documentation>
            <xsl:copy-of select="user"/>
            <xsl:copy-of select="admin"/>
            <xsl:copy-of select="developer"/>
        </documentation>
    </xsl:template>

    <xsl:template match="category">
        <xsl:choose>
            <xsl:when test=". = 'tool' or . = 'other' or . = 'game'">
                <category>tools</category>
            </xsl:when>
            <xsl:when test=". = 'productivity'">
                <category>organization</category>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
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
            <xsl:copy-of select="nextcloud"/>
            <xsl:if test="not(nextcloud)">
                <xsl:variable name="min" select="owncloud/@min-version[.='9.0' or '9.1' or '9.2']"/>
                <xsl:variable name="max" select="owncloud/@max-version[.='9.0' or '9.1' or '9.2']"/>
                <!-- if someone knows a better way to do this in xslt 1.0 feel free to patch it :) -->
                <xsl:if test="$min or $max">
                    <nextcloud>
                        <xsl:choose>
                            <xsl:when test="$min = '9.0'">
                                <xsl:attribute name="min-version">
                                    <xsl:value-of select="'9'"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:when test="$min = '9.1'">
                                <xsl:attribute name="min-version">
                                    <xsl:value-of select="'10'"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:when test="$min = '9.2'">
                                <xsl:attribute name="min-version">
                                    <xsl:value-of select="'11'"/>
                                </xsl:attribute>
                            </xsl:when>
                        </xsl:choose>
                        <xsl:choose>
                            <xsl:when test="$max = '9.0'">
                                <xsl:attribute name="max-version">
                                    <xsl:value-of select="'9'"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:when test="$max = '9.1'">
                                <xsl:attribute name="max-version">
                                    <xsl:value-of select="'10'"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:when test="$max = '9.2'">
                                <xsl:attribute name="max-version">
                                    <xsl:value-of select="'11'"/>
                                </xsl:attribute>
                            </xsl:when>
                        </xsl:choose>
                    </nextcloud>
                </xsl:if>
            </xsl:if>
        </dependencies>
    </xsl:template>

    <xsl:template match="repair-steps">
        <repair-steps>
            <xsl:copy-of select="pre-migration"/>
            <xsl:copy-of select="post-migration"/>
            <xsl:copy-of select="live-migration"/>
            <xsl:copy-of select="install"/>
            <xsl:copy-of select="uninstall"/>
        </repair-steps>
    </xsl:template>

</xsl:stylesheet>
