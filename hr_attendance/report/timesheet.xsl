<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format">

    <xsl:import href="hr_custom_default.xsl"/>
    <xsl:import href="hr_custom_rml.xsl"/>

	<xsl:template match="/">
        <xsl:call-template name="rml" />
    </xsl:template>


    <xsl:template name="stylesheet">
		<document filename="timesheet.pdf">
			<template pageSize="29.7cm,21cm" leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Timesheets" author="Generated by Open ERP, Fabien Pinckaers" allowSplitting="20">
				<pageTemplate id="first">
					<pageGraphics>
						<drawRightString x="19.0cm" y="26.0cm"><xsl:value-of select="date"/></drawRightString>
					</pageGraphics>
					<frame id="col1" x1="2.0cm" y1="2.5cm" width="22.7cm" height="18cm"/>
				</pageTemplate>
			</template>
			
			<stylesheet>
			   <paraStyle name="title" fontName="Helvetica-Bold" fontSize="15.0" leading="17" alignment="CENTER" spaceBefore="12.0" spaceAfter="6.0"/>
			   <paraStyle name="emp" fontSize="13.0"/>
		       <blockTableStyle id="week">
		           <blockFont name="Helvetica" size="12" colorName="red" start="0,0" stop="-1,-1"/>
		           <blockFont name="Helvetica-BoldOblique" start="0,0" stop="0,0"/>
		           <blockBackground colorName="lightgrey" start="1,0" stop="-1,0"/>
		           <blockFont name="Helvetica-BoldOblique" start="-1,0" stop="-1,-1"/>
		            <lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,0" />
                    <lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
                    <lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
                    <lineStyle kind="LINEBELOW" colorName="black" start="0,0" stop="-1,-1"/>
		           <blockValign value="TOP"/>
		       </blockTableStyle>
			</stylesheet>

			<story>
				<xsl:call-template name="story"/>
			</story>
		</document>
    </xsl:template>

    <xsl:template name="story">
        <spacer length="1cm" />
        <xsl:apply-templates select="report/title"/>
        <xsl:apply-templates select="report/user"/>
    </xsl:template>

    <xsl:template match="title">
        <para style="title">
            <xsl:value-of select="."/>
        </para>
        <spacer length="1cm"/>
    </xsl:template>

    <xsl:template match="user">
        <spacer length="1cm" />
        <para style="emp">
            <b>Employee: </b>
            <i><xsl:value-of select="name" /></i>
        </para>
        <spacer length="0.5cm" />
        <xsl:for-each select="week">
            <blockTable colWidths="8cm,2cm,2cm,2cm,2cm,2cm,2cm,2cm,2cm" style="week">
                <tr>
                    <td>From <xsl:value-of select="weekstart" /> to <xsl:value-of select="weekend" /></td>
                    <td>Mon</td>
                    <td>Tue</td>
                    <td>Wed</td>
                    <td>Thu</td>
                    <td>Fri</td>
                    <td>Sat</td>
                    <td>Sun</td>
                    <td>Total</td>
                </tr>
                <tr>
                    <td>Worked hours</td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Monday/workhours">
                                <xsl:value-of select="Monday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Tuesday/workhours">
                                <xsl:value-of select="Tuesday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Wednesday/workhours">
                                <xsl:value-of select="Wednesday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Thursday/workhours">
                                <xsl:value-of select="Thursday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Friday/workhours">
                                <xsl:value-of select="Friday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Saturday/workhours">
                                <xsl:value-of select="Saturday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="Sunday/workhours">
                                <xsl:value-of select="Sunday/workhours" />
                            </xsl:when>
                            <xsl:otherwise>0h00</xsl:otherwise>
                        </xsl:choose>							
                    </td>
                    <td>
                        <xsl:value-of select="total/worked" />
                    </td>
                </tr>
            </blockTable>
            <xsl:if test="position() != last()">
                <blockTable colWidths="24cm" style="week">
                    <tr>
                        <td colspan="6"></td>
                    </tr>
                </blockTable>
            </xsl:if>
        </xsl:for-each>
        <xsl:if test="position() != last()">
            <pageBreak/>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
