<?xml version="1.0" encoding="utf-8"?>


<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
<xsl:template match="/">
			<xsl:apply-templates select="artists"/>
</xsl:template>


<xsl:template match="artists">

	<document>
		<template leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Bids report" author="Generated by Open ERP, Fabien Pinckaers">


			<pageTemplate id="all">
				<pageGraphics/>
					<frame id="principal" x1="1.0cm" y1="2.0cm" width="19.0cm" height="26.0cm" alignment="center"/>
			</pageTemplate>
		</template>

		<stylesheet>
		<paraStyle name="spacebefore" alignment="center" fontName="Courier" fontSize="12" spaceBefore="0" spaceAfter="0"/>
		<paraStyle name="spaceafter" fontName="Courier" fontSize="12" spaceBefore="0" spaceAfter="0"/>

		<blockTableStyle id="artist">
			<blockLeftPadding  start="0,0" stop="-1,-1" length="5mm"/>
			<blockRightPadding start="0,0" stop="-1,-1" length="5mm"/>
			<blockTopPadding start="0,0" stop="-1,0" length="5mm"/>
			<blockBottomPadding start="0,0" stop="-1,0" length="2mm"/>
			<blockBottomPadding start="0,-1" stop="-1,-1" length="5mm"/>

			<blockValign value="TOP"/>
			<blockAlignment value="LEFT"/>
			<lineStyle kind="LINEABOVE" colorName="black" start="0,0" stop="-1,0"/>
			<lineStyle kind="LINEBELOW" colorName="black" start="0,-1" stop="-1,-1"/>
			<lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="-1,-1"/>
			<lineStyle kind="LINEBEFORE" colorName="black" start="0,0" stop="0,-1"/>
			<lineStyle kind="LINEAFTER" colorName="black" start="-1,0" stop="-1,-1"/>
		</blockTableStyle>
		</stylesheet>
		<story>

	<xsl:apply-templates select="artist"/>
	</story>
	</document>
</xsl:template>


<xsl:template match="artist">

			<blockTable repeatRows="1" style="artist" colWidths="18.0cm">
				<tr>
					<td>
						<para style="spacebefore"><b><xsl:value-of select="name"/><xsl:text> (</xsl:text><xsl:value-of select="birth_death_dates"/><xsl:text>)</xsl:text></b></para>
					</td>
				</tr>

				<tr>
					<td>
						<para style="spaceafter"><xsl:value-of select="biography"/></para>
					</td>
				</tr>
			</blockTable>

			<blockTable rowHeights="2cm" colWidths="18.0cm">
				<tr>
					<td>
					</td>
				</tr>
			</blockTable>
</xsl:template>

</xsl:stylesheet>
