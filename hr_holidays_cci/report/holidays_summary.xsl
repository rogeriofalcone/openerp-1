<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:template match="/">
		<xsl:call-template name="rml" />
	</xsl:template>

	<xsl:template name="rml">
		<document filename="example.pdf">
			<template pageSize="74.7cm,30cm" leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Timesheets" author="Generated by Tiny ERP, Fabien Pinckaers" allowSplitting="20">
				<pageTemplate id="first">
					<frame id="col1" x1="2.0cm" y1="2.5cm" width="70.7cm" height="25cm"/>
				</pageTemplate>
			</template>

			<stylesheet>
				<paraStyle name="normal" fontName="Helvetica" fontSize="8" alignment="left" />
				<paraStyle name="normal-title" fontName="Helvetica" fontSize="6" />
				<paraStyle name="title" fontName="Helvetica" fontSize="18" alignment="center" />
				<paraStyle name="dept" fontName="Helvetica-Bold" fontSize="11" alignment="left" />
				<paraStyle name="employee" fontName="Helvetica-Bold" fontSize="10" textColor="black" />
				<paraStyle name="glande" textColor="red" />
				<paraStyle name="normal_people" textColor="green" />
				<paraStyle name="esclave" textColor="blue" />
				<blockTableStyle id="products">
					 <blockAlignment value="CENTER" start="1,0" stop="-1,-1"/>
					 <lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,-1" />
					 <lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
					 <lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
					 <lineStyle kind="LINEBELOW" colorName="black" start="0,-1" stop="-1,-1"/>
					 <blockFont name="Helvetica-Bold" size="10" start="0,-1" stop="-1,-1"/>
					 <blockValign value="TOP"/>
				</blockTableStyle>
				<blockTableStyle id="legend">
					<blockAlignment value="LEFT" start="1,0" stop="-1,-1" />
					<blockFont name="Helvetica" size="8" start="0,-1" stop="-1,-1"/>
					<lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,-1" />
					<lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
					<lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
					<lineStyle kind="LINEBELOW" colorName="black" start="0,-1" stop="-1,-1"/>
					<blockBackground colorName="#FFFFFF" start="0,0" stop="-1,-1"/>
					<xsl:for-each select="/report/legend">
						<blockBackground>
							<xsl:attribute name="colorName">
							<xsl:value-of select="attribute::color" />
							</xsl:attribute>
							<xsl:attribute name="start">
								<xsl:text>0,</xsl:text>
								<xsl:value-of select="attribute::row" />
							</xsl:attribute>
							<xsl:attribute name="stop">
								<xsl:text>0,</xsl:text>
								<xsl:value-of select="attribute::row" />
							</xsl:attribute>
						</blockBackground>
					</xsl:for-each>
					<blockValign value="TOP"/>
				</blockTableStyle>
				<blockTableStyle id="month">
					<blockAlignment value="CENTER" start="1,0" stop="-1,-1" />
					<blockFont name="Helvetica" size="8" start="0,0" stop="-1,1"/>
					<blockFont name="Helvetica" size="6" start="0,2" stop="-2,-2"/>
					<blockFont name="Helvetica-BoldOblique" size="8" start="0,-1" stop="-1,-1"/>
					<blockBackground colorName="#FFFFFF" start="1,0" stop="-2,1"/>
					<xsl:for-each select="/report/days/dayy[@name='Sat' or @name='Sun']">
						<xsl:variable name="col" select="attribute::cell" />
						<blockBackground>
							<xsl:attribute name="colorName">lightgrey</xsl:attribute>
							<xsl:attribute name="start">
								<xsl:value-of select="$col" />
								<xsl:text>,0</xsl:text>
							</xsl:attribute>
							<xsl:attribute name="stop">
								<xsl:value-of select="$col" />
								<xsl:text>,-1</xsl:text>
							</xsl:attribute>
						</blockBackground>
					</xsl:for-each>
					<xsl:for-each select="/report/info">
						<xsl:variable name="val" select="attribute::val" />
						<xsl:variable name="col" select="attribute::number" />
						<xsl:variable name="row" select="attribute::id" />
						<xsl:for-each select="/report/legend">
							<xsl:variable name="val_id" select="attribute::id" />
							<xsl:variable name="color" select="attribute::color" />
							<xsl:if test="$val_id = $val ">
								<blockBackground>
									<xsl:attribute name="colorName"><xsl:value-of select="$color" /></xsl:attribute>
									<xsl:attribute name="start">
										<xsl:value-of select="$col" />
										<xsl:text>,</xsl:text>
										<xsl:value-of select="$row + 1" />
									</xsl:attribute>
									<xsl:attribute name="stop">
										<xsl:value-of select="$col" />
										<xsl:text>,</xsl:text>
										<xsl:value-of select="$row + 1" />
									</xsl:attribute>
								</blockBackground>
							</xsl:if>
						</xsl:for-each>
					</xsl:for-each>
					<xsl:for-each select="report/employee">
						<xsl:variable name="dept" select="attribute::id" />
						<xsl:variable name="row" select="attribute::row" />
						<xsl:if test="$dept = 1">
							<blockBackground>
								<xsl:attribute name="colorName">lightgrey</xsl:attribute>
								<xsl:attribute name="start">
									<xsl:text>0,</xsl:text>
									<xsl:value-of select="$row +1" />
								</xsl:attribute>
								<xsl:attribute name="stop">
									<xsl:text>0,</xsl:text>
									<xsl:value-of select="$row +1" />
								</xsl:attribute>
							</blockBackground>
						</xsl:if>
					</xsl:for-each>
					<lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,-1" />
					<lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
					<lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
					<lineStyle kind="LINEBELOW" colorName="black" start="0,-1" stop="-1,-1"/>
					<blockValign value="TOP"/>
				</blockTableStyle>

			</stylesheet>

			<story>
				<xsl:call-template name="story"/>
			</story>
		</document>
	</xsl:template>

	<xsl:template name="story">
		<para style="title" t="1">Holidays Summary</para>
		<spacer length="1cm" />
		<xsl:variable name="cols_legend">
			<xsl:text>1.2cm,7.0cm</xsl:text>
		</xsl:variable>
		<blockTable>
			<xsl:attribute name="style">products</xsl:attribute>
			<xsl:attribute name="colWidths"><xsl:value-of select="report/cols_months"/></xsl:attribute>
			<tr>
			 	<td>Month</td>
				<xsl:for-each select="report/months">
					<td>
						<xsl:value-of select="attribute::name" />
					</td>
				</xsl:for-each>
			</tr>
		</blockTable>

		<blockTable>
			<xsl:attribute name="style">month</xsl:attribute>
			<xsl:attribute name="colWidths"><xsl:value-of select="report/cols" /></xsl:attribute>
			<tr>
				<td> </td>
				<xsl:for-each select="report/days/dayy">
					<td>
						<xsl:value-of select="attribute::name" />
					</td>
				</xsl:for-each>
			</tr>
			<tr>
				<td><para>
						<xsl:attribute name="style">employee</xsl:attribute>
								Employee Name
					</para>
				</td>
				<xsl:for-each select="report/days/dayy">
					<td>
						<xsl:value-of select="attribute::number" />
					</td>
				</xsl:for-each>
            </tr>
			<xsl:apply-templates select="report/employee"/>
			<xsl:for-each select="report/employee">
				<xsl:variable name="id" select="attribute::id"/>

				<tr>
					<td t="1">
						<para>
							<xsl:choose>
   								 <xsl:when test="$id = 1">
      							 	<xsl:attribute name="style">dept</xsl:attribute>
      							 </xsl:when>
								<xsl:otherwise>
      								<xsl:attribute name="style">normal</xsl:attribute>
   								</xsl:otherwise>
							</xsl:choose>
							<xsl:value-of select="attribute::name"/>
						</para>
					</td>
					<xsl:for-each select="//report/days/dayy">
						<xsl:variable name="cell" select="attribute::cell" />
						<td></td>
					</xsl:for-each>
				</tr>
			</xsl:for-each>

		</blockTable>
		<spacer length="1cm" />
		<blockTable>
			<xsl:attribute name="style">legend</xsl:attribute>
			<xsl:attribute name="colWidths"><xsl:value-of select="$cols_legend"/></xsl:attribute>
			<tr>
					<td>Color</td>
					<td>Holiday Type</td>

			</tr>
			<xsl:for-each select="report/legend">
			<tr>
					<td>
							<para>
							<xsl:attribute name="style">normal</xsl:attribute>
								<xsl:value-of select="attribute::row"/>
							</para>
					</td>
					<td>
							<para>
							<xsl:attribute name="style">normal</xsl:attribute>
								<xsl:value-of select="attribute::name"/>
							</para>
					</td>
            </tr>
            </xsl:for-each>
		</blockTable>
	</xsl:template>
</xsl:stylesheet>
