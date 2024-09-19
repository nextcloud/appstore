<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/info">
        <app>
            <!-- must have attributes -->
            <id>
                <xsl:value-of select="id"/>
            </id>
            <categories type="list">
                <xsl:for-each select="category">
                    <category>
                        <id>
                            <xsl:value-of select="."/>
                        </id>
                    </category>
                </xsl:for-each>
            </categories>

            <description>
                <xsl:for-each select="description">
                    <xsl:choose>
                        <xsl:when test="@lang">
                            <xsl:element name="{@lang}">
                                <xsl:value-of select="."/>
                            </xsl:element>
                        </xsl:when>
                        <xsl:otherwise>
                            <en>
                                <xsl:value-of select="."/>
                            </en>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </description>

            <summary>
                <xsl:for-each select="summary">
                    <xsl:choose>
                        <xsl:when test="@lang">
                            <xsl:element name="{@lang}">
                                <xsl:value-of select="."/>
                            </xsl:element>
                        </xsl:when>
                        <xsl:otherwise>
                            <en>
                                <xsl:value-of select="."/>
                            </en>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </summary>

            <name>
                <xsl:for-each select="name">
                    <xsl:choose>
                        <xsl:when test="@lang">
                            <xsl:element name="{@lang}">
                                <xsl:value-of select="."/>
                            </xsl:element>
                        </xsl:when>
                        <xsl:otherwise>
                            <en>
                                <xsl:value-of select="."/>
                            </en>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </name>

            <authors type="list">
                <xsl:for-each select="author">
                    <author>
                        <name>
                            <xsl:value-of select="."/>
                        </name>
                        <homepage>
                            <xsl:value-of select="@homepage"/>
                        </homepage>
                        <mail>
                            <xsl:value-of select="@mail"/>
                        </mail>
                    </author>
                </xsl:for-each>
            </authors>

            <screenshots type="list">
                <xsl:for-each select="screenshot">
                    <screenshot>
                        <url>
                            <xsl:value-of select="."/>
                        </url>
                        <small-thumbnail>
                            <xsl:value-of select="@small-thumbnail"/>
                        </small-thumbnail>
                        <ordering type="int">
                            <xsl:value-of select="position()"/>
                        </ordering>
                    </screenshot>
                </xsl:for-each>
            </screenshots>

            <!-- optional elements need defaults -->

            <donations type="list">
                <xsl:for-each select="donation">
                    <donation>
                        <url>
                            <xsl:value-of select="."/>
                        </url>
                        <xsl:choose>
                            <xsl:when test="@title">
                                <title>
                                    <xsl:value-of select="@title"/>
                                </title>
                            </xsl:when>
                            <xsl:otherwise>
                                <title>Donate to support this app</title>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:choose>
                            <xsl:when test="@type">
                                <type>
                                    <xsl:value-of select="@type"/>
                                </type>
                            </xsl:when>
                            <xsl:otherwise>
                                <type>other</type>
                            </xsl:otherwise>
                        </xsl:choose>
                        <ordering type="int">
                            <xsl:value-of select="position()"/>
                        </ordering>
                    </donation>
                </xsl:for-each>
            </donations>

            <xsl:if test="documentation/admin[starts-with(., 'https://')]">
                <admin-docs>
                    <xsl:value-of select="documentation/admin"/>
                </admin-docs>
            </xsl:if>


            <xsl:if test="documentation/user[starts-with(., 'https://')]">
                <user-docs>
                    <xsl:value-of select="documentation/user"/>
                </user-docs>
            </xsl:if>


            <xsl:if test="documentation/developer[starts-with(., 'https://')]">
                <developer-docs>
                    <xsl:value-of select="documentation/developer"/>
                </developer-docs>
            </xsl:if>

            <website>
                <xsl:value-of select="website"/>
            </website>
            <discussion>
                <xsl:value-of select="discussion"/>
            </discussion>
            <issue-tracker>
                <xsl:value-of select="bugs"/>
            </issue-tracker>

            <!-- release -->
            <release>
                <version>
                    <xsl:value-of select="version"/>
                </version>
                <licenses type="list">
                    <xsl:for-each select="licence">
                        <license>
                            <id>
                                <xsl:value-of select="."/>
                            </id>
                        </license>
                    </xsl:for-each>
                </licenses>

                <xsl:apply-templates select="dependencies"/>
                <xsl:apply-templates select="external-app"/>
            </release>
        </app>
    </xsl:template>

    <xsl:template match="external-app">
        <external-app>
            <docker-install>
                <registry type="string">
                    <xsl:value-of select="docker-install/registry"/>
                </registry>
                <image type="string">
                    <xsl:value-of select="docker-install/image"/>
                </image>
                <image-tag type="string">
                    <xsl:value-of select="docker-install/image-tag"/>
                </image-tag>
            </docker-install>
            <scopes type="list">
                <xsl:for-each select="scopes/value">
                    <value type="string">
                        <xsl:value-of select="."/>
                    </value>
                </xsl:for-each>
            </scopes>
            <system type="boolean">
                <xsl:value-of select="system"/>
            </system>
        </external-app>
    </xsl:template>

    <xsl:template match="dependencies">
        <php-min-version type="min-version">
            <xsl:value-of select="php/@min-version"/>
        </php-min-version>
        <php-max-version type="max-version">
            <xsl:value-of select="php/@max-version"/>
        </php-max-version>
        <xsl:choose>
            <xsl:when test="php/@min-int-size">
                <min-int-size type="int">
                    <xsl:value-of select="php/@min-int-size"/>
                </min-int-size>
            </xsl:when>
            <xsl:otherwise>
                <min-int-size type="int">32</min-int-size>
            </xsl:otherwise>
        </xsl:choose>
        <platform-min-version type="min-version">
            <xsl:value-of select="nextcloud/@min-version"/>
        </platform-min-version>
        <platform-max-version type="max-version">
            <xsl:value-of select="nextcloud/@max-version"/>
        </platform-max-version>

        <php-extensions type="list">
            <xsl:for-each select="lib">
                <php-extension>
                    <min-version type="min-version">
                        <xsl:value-of select="@min-version"/>
                    </min-version>
                    <max-version type="max-version">
                        <xsl:value-of select="@max-version"/>
                    </max-version>
                    <id>
                        <xsl:value-of select="."/>
                    </id>
                </php-extension>
            </xsl:for-each>
        </php-extensions>
        <databases type="list">
            <xsl:for-each select="database">
                <database>
                    <min-version type="min-version">
                        <xsl:value-of select="@min-version"/>
                    </min-version>
                    <max-version type="max-version">
                        <xsl:value-of select="@max-version"/>
                    </max-version>
                    <id>
                        <xsl:value-of select="."/>
                    </id>
                </database>
            </xsl:for-each>
        </databases>
        <shell-commands type="list">
            <xsl:for-each select="command">
                <shell-command>
                    <name>
                        <xsl:value-of select="."/>
                    </name>
                </shell-command>
            </xsl:for-each>
        </shell-commands>
    </xsl:template>
</xsl:stylesheet>
