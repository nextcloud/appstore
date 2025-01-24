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
                    <!--
                        convert deprecated shorthand aliases to full SPDX identifiers where possible,
                        leave agpl/gpl3 aliases as is for now (A/GPL-3.0 are also deprecated and thus not added to list of valid licenses)
                    -->
                    <xsl:variable name="licenseAlias" select="translate(., $uppercase, $lowercase)"/>
                    <xsl:choose>
                        <xsl:when test="$licenseAlias = 'agpl'">agpl</xsl:when>
                        <xsl:when test="$licenseAlias = 'apache'">Apache-2.0</xsl:when>
                        <xsl:when test="$licenseAlias = 'gpl3'">gpl3</xsl:when>
                        <xsl:when test="$licenseAlias = 'mit'">MIT</xsl:when>
                        <xsl:when test="$licenseAlias = 'mpl'">MPL-2.0</xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="."/>
                        </xsl:otherwise>
                    </xsl:choose>
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
            <xsl:copy-of select="discussion"/>
            <xsl:copy-of select="bugs"/>
            <xsl:copy-of select="repository"/>
            <xsl:copy-of select="screenshot"/>
            <xsl:copy-of select="donation"/>
            <xsl:apply-templates select="dependencies"/>
            <xsl:copy-of select="background-jobs"/>
            <xsl:apply-templates select="repair-steps"/>
            <xsl:copy-of select="two-factor-providers"/>
            <xsl:copy-of select="commands"/>
            <xsl:apply-templates select="settings"/>
            <xsl:apply-templates select="activity"/>
            <xsl:copy-of select="dashboard"/>
            <xsl:copy-of select="fulltextsearch"/>
            <xsl:apply-templates select="navigations"/>
            <xsl:copy-of select="contactsmenu"/>
            <xsl:copy-of select="collaboration" />

            <!-- copy invalid elements to fail if they are present -->
            <xsl:copy-of select="standalone"/>
            <xsl:copy-of select="default_enable"/>
            <xsl:copy-of select="shipped"/>
            <xsl:copy-of select="public"/>
            <xsl:copy-of select="remote"/>
            <xsl:copy-of select="requiremin"/>
            <xsl:copy-of select="requiremax"/>

            <xsl:apply-templates select="external-app"/>
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

    <xsl:template match="navigations">
        <navigations>
            <xsl:apply-templates select="navigation"/>
        </navigations>
    </xsl:template>

    <xsl:template match="category">
        <xsl:choose>
            <xsl:when test="text() = 'auth'">
                <category>security</category>
            </xsl:when>
            <xsl:otherwise>
                <category>
                    <xsl:value-of select="."/>
                </category>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="navigation">
        <navigation>
            <!-- test if attribute exists, otherwise an empty value will be
            used which leads to validation failure -->
            <xsl:if test="@role">
                <xsl:attribute name="role">
                        <xsl:value-of select="@role"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:copy-of select="id"/>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="route"/>
            <xsl:copy-of select="icon"/>
            <xsl:copy-of select="order"/>
            <xsl:copy-of select="type"/>
        </navigation>
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
            <xsl:copy-of select="nextcloud"/>
            <xsl:copy-of select="backend"/>
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

    <xsl:template match="external-app">
        <external-app>
            <xsl:apply-templates select="docker-install"/>
            <xsl:copy-of select="scopes"/>
            <xsl:copy-of select="system"/>
            <xsl:apply-templates select="environment-variables"/>
        </external-app>
    </xsl:template>

    <xsl:template match="docker-install">
        <docker-install>
            <xsl:copy-of select="registry"/>
            <xsl:copy-of select="image"/>
            <xsl:copy-of select="image-tag"/>
        </docker-install>
    </xsl:template>

    <xsl:template match="environment-variables">
        <environment-variables>
            <xsl:apply-templates select="variable"/>
        </environment-variables>
    </xsl:template>

    <xsl:template match="variable">
        <variable>
            <xsl:copy-of select="name"/>
            <xsl:copy-of select="display-name"/>
            <xsl:copy-of select="description"/>
            <xsl:copy-of select="default"/>
        </variable>
    </xsl:template>

</xsl:stylesheet>
