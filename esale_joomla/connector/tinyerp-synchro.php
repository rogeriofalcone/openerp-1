<?php

	define( '_VALID_MOS', 1);

	include("xmlrpc.inc");
	include("xmlrpcs.inc");

	require_once( 'configuration.php' );
	require_once( 'includes/joomla.php' );
	require_once( 'administrator/components/com_virtuemart/virtuemart.cfg.php' );

	$con = mysql_pconnect($mosConfig_host, $mosConfig_user,$mosConfig_password );
	mysql_select_db($mosConfig_db);

	function get_taxes() {
		global $mosConfig_dbprefix;
		$taxes=array();

		$result=mysql_query("select tax_rate_id, tax_rate*100 from ".$mosConfig_dbprefix."vm_tax_rate;");
		if ($result) while ($row=mysql_fetch_row($result)) {
			$taxes[]=new xmlrpcval(array(new xmlrpcval($row[0], "int"), new xmlrpcval("Tax ".$row[1]."%", "string")), "array");
		}
		return new xmlrpcresp( new xmlrpcval($taxes, "array"));
	}


	function delete_products() {
		global $mosConfig_dbprefix;

		mysql_query("truncate  table ".$mosConfig_dbprefix."vm_product_attribute;");
		mysql_query("truncate  table ".$mosConfig_dbprefix."vm_product_price;");
		mysql_query("truncate  table ".$mosConfig_dbprefix."vm_product_tax;");
		mysql_query("truncate  table ".$mosConfig_dbprefix."vm_product_category_xref;");
		mysql_query("delete from ".$mosConfig_dbprefix."jf_content where reference_table='vm_product' and reference_field in ('product_s_desc','product_desc') ;");
		$result=mysql_query("truncate  table ".$mosConfig_dbprefix."vm_product;");
		//$result=mysql_query("update ".$mosConfig_dbprefix."vm_product set `product_publish` = 'N';");
		//$result=mysql_query("update ".$mosConfig_dbprefix."vm_product set ".
		//	"product_publish='N' ".
		//	";");

		return new xmlrpcresp( new xmlrpcval($result, "int"));
	}

	function unlink_products($product_id) {
		global $mosConfig_dbprefix;
		//self.debug("Products Ids for Unlink: ".implode(",",$product_ids));
		mysql_query("update ".$mosConfig_dbprefix."vm_product set product_publish='N' where product_id in (".implode(",",$product_id).");");
		return new xmlrpcresp(new xmlrpcval(1,"int"));
	}

	function delete_product_categories() {
		global $mosConfig_dbprefix;

		mysql_query("truncate  table ".$mosConfig_dbprefix."vm_category_xref;");
		$result=mysql_query("truncate  table ".$mosConfig_dbprefix."vm_category;");


		return new xmlrpcresp( new xmlrpcval($result, "int"));
	}

	function get_languages() {
		$languages=array();

		$languages[]=new xmlrpcval(array(new xmlrpcval(1, "int"), new xmlrpcval("Unique", "string")), "array");
		return new xmlrpcresp( new xmlrpcval($languages, "array"));
	}

	function get_categories() {
		global $mosConfig_dbprefix;
		$categories=array();

		$result=mysql_query("select category_id, category_name from ".$mosConfig_dbprefix."vm_category;");
		if ($result) while ($row=mysql_fetch_row($result)) {
			$categories[]=new xmlrpcval(array(new xmlrpcval($row[0], "int"), new xmlrpcval(parent_category($row[0],$row[1]), "string")), "array");
		}
		return new xmlrpcresp( new xmlrpcval($categories, "array"));
	}

	function parent_category($id, $name) {
		global $mosConfig_dbprefix;
		$result=mysql_query("select category_parent_id from ".$mosConfig_dbprefix."vm_category_xref where category_child_id=".$id.";");
		if ($result && $row=mysql_fetch_row($result)) {
			if ($row[0]==0) {
				return $name;
			} else {
				$resultb=mysql_query("select category_name from ".$mosConfig_dbprefix."vm_category where category_id=".$row[0].";");
				if ($resultb && $rowb=mysql_fetch_row($resultb)) {
					$name=parent_category($row[0], $rowb[0] . " \\ ". $name);
					return $name;
				}
			}
		}
		return $name;
	}

	function set_product_stock($tiny_product) {
		global $mosConfig_dbprefix;
		mysql_query("update ".$mosConfig_dbprefix."vm_product set product_in_stock=".$tiny_product['quantity']." where
		product_id=".$tiny_product['esale_joomla_id'].";");
		//mysql_query("update products set products_status=".(($tiny_product['quantity']>0)?1:0)." where
		//products_id=".$tiny_product['esale_joomla_id'].";");
		return new xmlrpcresp(new xmlrpcval(1,"int"));
	}

	function debug($s) {
		$fp = fopen("/tmp/debug.xmlrpc2.txt","a");
		fwrite($fp, $s."\n");
		fclose($fp);
	}



	function set_category($tiny_category){
		global $mosConfig_dbprefix;

		if($tiny_category['esale_joomla_id'] != 0)
		{

			$result=mysql_query("update ".$mosConfig_dbprefix."vm_category set ".
				"category_name='". ($tiny_category['name'])."', ".
				"category_description='". ($tiny_category['name'])."'".
				"where category_id=".$tiny_category['esale_joomla_id'].";");
			$osc_id=$tiny_category['esale_joomla_id'];

		}
		else{

			mysql_query("insert into  ".$mosConfig_dbprefix."vm_category  (category_name,category_description,category_publish,vendor_id) values (\"". ($tiny_category['name'])."\",\"". ($tiny_category['name'])."\",\"Y\",'1');");
			$category_child_id=mysql_insert_id();
			mysql_query("update ".$mosConfig_dbprefix."vm_category set list_order=".$category_child_id." where category_id=".$category_child_id.";");
			$category_parent_id=$tiny_category['parent_id'];
			mysql_query("insert into  ".$mosConfig_dbprefix."vm_category_xref  (category_parent_id,category_child_id) values (".$category_parent_id.",".$category_child_id.");");
			$osc_id=$category_child_id;

		}
		$result=mysql_query("select id from ".$mosConfig_dbprefix."languages where iso='fr';");
		$lang_id=-1;
		if ($result && $row=mysql_fetch_row($result)) {
			$lang_id=$row[0];

		}
		$orinal= ($tiny_category['name']);
		$value= ($tiny_category['name:fr_FR']);

		if($value=='' and $orinal!=''){
			$value=$orinal;
		}
		elseif($orinal=='' and $value!=''){
			$orinal=$value;
		}
		if($orinal!=''){
			$value=str_replace('"','\"',$value);
			$result=mysql_query("select id from ".$mosConfig_dbprefix."jf_content where reference_id=".$osc_id." and reference_table='vm_category' and reference_field='category_name';");
			$temp=-1;
			if ($result && $row=mysql_fetch_row($result)) {
				$temp=mysql_query("update ".$mosConfig_dbprefix."jf_content set reference_id=".$osc_id." ,language_id='".$lang_id."',published=1,value=\"".$value."\",modified='".date( "Y-m-d H:i:s" )."',original_value='".md5($orinal)."' where id=".$row[0].";");


			}
			else{
				$temp=mysql_query("insert into  ".$mosConfig_dbprefix."jf_content(language_id,reference_id,reference_table,reference_field,value,original_value,modified_by,modified,published)
values (".$lang_id.",".$osc_id.",'vm_category','category_name',\"".$value."\",'".md5($orinal)."',70,'".date( "Y-m-d H:i:s" )."',1);");


			}

		}



		return new xmlrpcresp(new xmlrpcval($osc_id, "int"));
	}

	function set_tax($tiny_tax){
		global $mosConfig_dbprefix;
		$country_id='-';
		$state_id='-';
		$type='fixamount';
		if ($tiny_tax['type']=='percent')
			$type='percentage';

		if ($tiny_tax['country'])
		{
			$result=mysql_query("select country_3_code from ".$mosConfig_dbprefix."vm_country where country_name='".$tiny_tax['country']."';");
			if ($result && $row=mysql_fetch_row($result)) {
				$country_id=$row[0];
			}
		}

		if($tiny_tax['esale_joomla_id'] != 0)
		{

			$result=mysql_query("update ".$mosConfig_dbprefix."vm_tax_rate set ".
				"tax_name='".$tiny_tax['name']."', ".
				"tax_type='".$type."', ".
				"tax_rate=".$tiny_tax['rate'].", ".
				"inc_base_price=".$tiny_tax['include_base_amount'].", ".
				"tax_country='".$country_id."', ".
				"tax_state='".$state_id."', ".
				"priority=".$tiny_tax['sequence'].
				" where tax_rate_id=".$tiny_tax['esale_joomla_id'].";");

			$osc_id=$tiny_tax['esale_joomla_id'];

		}
		else{

			mysql_query("insert into  ".$mosConfig_dbprefix."vm_tax_rate  (tax_name,tax_type,tax_rate,inc_base_price,priority,tax_country,tax_state,vendor_id) values (\"".$tiny_tax['name']."\",\"".$type."\",".$tiny_tax['rate'].",".$tiny_tax['include_base_amount'].",".$tiny_tax['sequence'].",'".$country_id."','".$state_id."','1');");
			$osc_id=mysql_insert_id();

		}

		return new xmlrpcresp(new xmlrpcval($osc_id, "int"));
	}
	function set_product($tiny_product){
		global $mosConfig_dbprefix;
		$prod = Array(
			'vendor_id'=>0
		);

		$result=mysql_query("select vendor_id, vendor_currency from ".$mosConfig_dbprefix."vm_vendor;");
		if ($result && $row=mysql_fetch_row($result)) {
			$prod['vendor_id']=$row[0];
			$prod['vendor_currency']=$row[1];
		}
		$result=mysql_query("select shopper_group_id from ".$mosConfig_dbprefix."vm_shopper_group where vendor_id=".$vendor_id." and shopper_group_name='-default-';");
		if ($result && $row=mysql_fetch_row($result))
			$prod['shopper_group']=$row[0];
		if ( $tiny_product['esale_joomla_id']) {
			$result = mysql_query("select count(*) from ".$mosConfig_dbprefix."vm_product where product_id=". $tiny_product['esale_joomla_id']);
			$row = mysql_fetch_row($result);
			if (! $row[0] )
				$tiny_product['esale_joomla_id'] = 0;
		}

		if (! $tiny_product['esale_joomla_id']) {
			$res = mysql_query("select shopper_group_id,vendor_id from ".$mosConfig_dbprefix."vm_shopper_group where `default` = 1");
			$shoperid = mysql_fetch_array($res);
			$shopper_group = $shoperid['shopper_group_id'];
			$vendorid = $shoperid['vendor_id'];

			$res = mysql_query("select vendor_currency from ".$mosConfig_dbprefix."vm_vendor where vendor_id = ".$vendorid);
			$vcurrency = mysql_fetch_array($res);
			$vendor_currency = $vcurrency['vendor_currency'];

			mysql_query("insert into ".$mosConfig_dbprefix."vm_product () values ()");
			$osc_id=mysql_insert_id();
			mysql_query("insert into ".$mosConfig_dbprefix."vm_product_price (product_id, product_price, product_currency, product_price_vdate, product_price_edate, shopper_group_id) values (".$osc_id.", ".$tiny_product['price'].", '".$vendor_currency."', 0, 0, ".$shopper_group.");");
			mysql_query("insert into ".$mosConfig_dbprefix."vm_product_category_xref (product_id, category_id) values (".$osc_id.", ".$tiny_product['category_id'].");");

			foreach ($tiny_product['tax_rate_id'] as $taxes=>$values) {
				mysql_query("insert into ".$mosConfig_dbprefix."vm_product_tax (product_id, tax_rate_id) values (".$osc_id.", ".$values["id"].");");
			}
		} else {
			$osc_id=$tiny_product['esale_joomla_id'];
		}



		mysql_query("update ".$mosConfig_dbprefix."vm_product set ".
			"product_in_stock=".$tiny_product['quantity'].",".
			"product_weight=".$tiny_product['weight'].",".
			"product_sku='".mysql_escape_string($tiny_product['model'])."',".
			"product_name='".mysql_escape_string( ($tiny_product['name']))."',".
			"vendor_id='".$prod['vendor_id']."',".
			"product_desc='".mysql_escape_string( ($tiny_product['description']))."', ".
			"product_unit='".mysql_escape_string( ($tiny_product['product_unit']))."', ".
			"product_publish='Y',".
			"product_packaging=".$tiny_product['product_packaging'].",".
			"product_s_desc='".mysql_escape_string( (substr($tiny_product['short_description'],0,200)))."' ".
			"where product_id=".$osc_id.";");

			// Replace or
			// Delete old values

		mysql_query("update ".$mosConfig_dbprefix."vm_product_price set product_price='".$tiny_product['price']."' where product_id=".$osc_id.";");

		mysql_query("update ".$mosConfig_dbprefix."vm_product_category_xref set category_id='".$tiny_product['category_id']."' where product_id=".$osc_id.";");
		mysql_query("delete from ".$mosConfig_dbprefix."vm_product_tax where product_id=".$osc_id.";");
		foreach ($tiny_product['tax_rate_id'] as $taxes=>$values) {
				mysql_query("insert into ".$mosConfig_dbprefix."vm_product_tax (product_id, tax_rate_id) values (".$osc_id.", ".$values["id"].");");
			}

		$result=mysql_query("select id from ".$mosConfig_dbprefix."languages where iso='fr';");
		$lang_id=-1;
		if ($result && $row=mysql_fetch_row($result)) {
			$lang_id=$row[0];

		}
		$orinal= ($tiny_product['name']);
		$value= ($tiny_product['name:fr_FR']);

		if($value=='' and $orinal!=''){
			$value=$orinal;
		}
		elseif($orinal=='' and $value!=''){
			$orinal=$value;
		}
		if($orinal!=''){
			$value=str_replace('"','\"',$value);
			$result=mysql_query("select id from ".$mosConfig_dbprefix."jf_content where reference_id=".$osc_id." and reference_table='vm_product' and reference_field='product_name';");
			$temp=-1;
			if ($result && $row=mysql_fetch_row($result)) {
				$temp=mysql_query("update ".$mosConfig_dbprefix."jf_content set reference_id=".$osc_id." ,language_id='".$lang_id."',published=1,value=\"".$value."\",modified='".date( "Y-m-d H:i:s" )."',original_value='".md5($orinal)."' where id=".$row[0].";");


			}
			else{
				$temp=mysql_query("insert into  ".$mosConfig_dbprefix."jf_content(language_id,reference_id,reference_table,reference_field,value,original_value,modified_by,modified,published)
values (".$lang_id.",".$osc_id.",'vm_product','product_name',\"".$value."\",'".md5($orinal)."',70,'".date( "Y-m-d H:i:s" )."',1);");


			}

		}

		$orinal= ($tiny_product['description']);
		$value= ($tiny_product['description:fr_FR']);

		if($value=='' and $orinal!=''){
			$value=$orinal;
		}
		elseif($orinal=='' and $value!=''){
			$orinal=$value;
		}
		if($orinal!=''){
			$value=str_replace('"','\"',$value);
			$result=mysql_query("select id from ".$mosConfig_dbprefix."jf_content where reference_id=".$osc_id." and reference_table='vm_product' and reference_field='product_desc';");
			$temp=-1;
			if ($result && $row=mysql_fetch_row($result)) {
				$temp=mysql_query("update ".$mosConfig_dbprefix."jf_content set reference_id=".$osc_id." ,language_id='".$lang_id."',published=1,value=\"".$value."\",modified='".date( "Y-m-d H:i:s" )."',original_value='".md5($orinal)."' where id=".$row[0].";");


			}
			else{
				$temp=mysql_query("insert into  ".$mosConfig_dbprefix."jf_content(language_id,reference_id,reference_table,reference_field,value,original_value,modified_by,modified,published)
values (".$lang_id.",".$osc_id.",'vm_product','product_desc',\"".$value."\",'".md5($orinal)."',70,'".date( "Y-m-d H:i:s" )."',1);");


			}

		}

		$s_orinal= ($tiny_product['short_description']);
		$s_value= ($tiny_product['short_description:fr_FR']);


		if($s_value=='' and $s_orinal!=''){
			$s_value=$s_orinal;
		}
		elseif($s_orinal=='' and $s_value!=''){
			$s_orinal=$s_value;
		}
		if($s_orinal!=''){
			$value=str_replace('"','\"',$value);
			$result=mysql_query("select id from ".$mosConfig_dbprefix."jf_content where reference_id=".$osc_id." and reference_table='vm_product' and reference_field='product_s_desc';");
			$temp=-1;
			if ($result && $row=mysql_fetch_row($result)) {
				$temp=mysql_query("update ".$mosConfig_dbprefix."jf_content set reference_id=".$osc_id.",language_id='".$lang_id."',published=1,value=\"".$value."\",modified='".date( "Y-m-d H:i:s" )."',original_value='".md5($s_orinal)."' where id=".$row[0].";");

			}
			else{
				$temp=mysql_query("insert into  ".$mosConfig_dbprefix."jf_content(language_id,reference_id,reference_table,reference_field,value,original_value,modified_by,modified,published)
values (".$lang_id.",".$osc_id.",'vm_product','product_s_desc',\"".$value."\",'".md5($s_orinal)."',70,'".date( "Y-m-d H:i:s" )."',1);");



			}

		}




		if ($tiny_product['haspic']==1) {

			$filename=tempnam('components/com_virtuemart/shop_image/product/', 'tiny_');
			$extension=strrchr($tiny_product['code'].'.jpg','.');
			$filename.=$extension;
			//$filename='components/com_virtuemart/shop_image/product/tiny_'.$tiny_product['code'].'.jpg';
			$hd=fopen($filename, "w");
			fwrite($hd, base64_decode($tiny_product['picture']));
			fclose($hd);
			$short=strrchr($filename,'/');
			$short=substr($short, 1, strlen($short));
			mysql_query("update ".$mosConfig_dbprefix."vm_product set product_full_image='".$short."' where product_id=".$osc_id.";");
			mysql_query("update ".$mosConfig_dbprefix."vm_product set product_thumb_image='".$short."' where product_id=".$osc_id.";");
			unlink(substr($filename,0,strlen($filename)-4));
			/*$newxsize = PSHOP_IMG_WIDTH;
			if (!$newxsize) {
				$newxsize=90;
			}
			$newysize = PSHOP_IMG_HEIGHT;
			if (!$newysize) {
				$newysize=60;
			}
			$extension=strtolower($extension);
			if (in_array($extension, array('.jpeg', '.jpe', '.jpg', '.gif', '.png'))) {
				if (in_array($extension, array('.jpeg', '.jpe', '.jpg'))) {
					$extension='.jpeg';
				}
				$thumb=tempnam('components/com_virtuemart/shop_image/product/', 'tiny_').$extension;
				$load='imagecreatefrom'.substr($extension,1,strlen($extension)-1);
				$save='image'.substr($extension,1,strlen($extension)-1);
				$tmp_img=$load($filename);
				$imgsize = getimagesize($filename);
				if ($imgsize[0] > $newxsize || $imgsize[1] > $newysize) {
					if ($imgsize[0]*$newysize > $imgsize[1]*$newxsize) {
						$ratio=$imgsize[0]/$newxsize;
					} else {
						$ratio=$imgsize[1]/$newysize;
					}
				} else {
					$ratio=1;
				}
				$tn=imagecreatetruecolor (floor($imgsize[0]/$ratio),floor($imgsize[1]/$ratio));
				imagecopyresized($tn,$tmp_img,0,0,0,0,floor($imgsize[0]/$ratio),floor($imgsize[1]/$ratio),$imgsize[0],$imgsize[1]);
				$short=strrchr($thumb,'/');
				$short=substr($short,1,strlen($short));
				$save($tn, $thumb);
				mysql_query("update ".$mosConfig_dbprefix."vm_product set product_thumb_image='".$short."' where product_id=".$osc_id.";");
			}*/
		}
		return new xmlrpcresp(new xmlrpcval($osc_id, "int"));
	}

	function get_saleorders($last_so) {
		global $mosConfig_dbprefix;
		$saleorders=array();

		/*$result=mysql_query(
			"SELECT
				o.`order_id`, c.`last_name`, c.`address_1`, c.`city`, c.`zip`, c.`state`,
				c.`country`, c.`phone_1`, c.`user_email`, d.`last_name` , d.`address_1` ,
				d.`city`, d.`zip`, d.`state`, d.`country`, o.`cdate`,
				c.title, c.first_name, d.title, d.first_name,
				d.user_id, c.user_id, o.customer_note
			FROM ".
				$mosConfig_dbprefix."vm_orders as o,".
				$mosConfig_dbprefix."vm_user_info as c, ".
				$mosConfig_dbprefix."vm_user_info as d
			where
				o.order_id>".$last_so." and
				o.user_id=c.user_id and
				(c.address_type_name is NULL or c.address_type_name='-default-') and
				o.user_info_id=d.user_info_id;
		");*/

		$result=mysql_query(
			"SELECT
				o.`order_id`, c.`last_name`, c.`address_1`, c.`city`, c.`zip`, c.`state`,
				cn.`country_2_code` as `country`, c.`phone_1`, c.`user_email`, d.`last_name` , d.`address_1` ,
				d.`city`, d.`zip`, d.`state`, d.`country`, o.`cdate`,
				c.title, c.first_name, d.title, d.first_name,
				d.user_id, c.user_id, o.customer_note,
				o.order_discount,o.order_shipping,o.order_shipping_tax FROM ".
				$mosConfig_dbprefix."vm_orders as o,".
				$mosConfig_dbprefix."vm_user_info as c, ".
				$mosConfig_dbprefix."vm_country as cn, ".
				$mosConfig_dbprefix."vm_user_info as d
			where
				o.order_id>".$last_so." and
				o.user_id=c.user_id and
				(c.address_type_name is NULL or c.address_type_name='-default-') and
				( cn.country_3_code = c.country) and
				o.user_info_id=d.user_info_id;
		");


		if ($result) while ($row=mysql_fetch_row($result)) {
			$orderlines=array();
			$resultb=mysql_query("select product_id, product_quantity, product_item_price from ".$mosConfig_dbprefix."vm_order_item where order_id=".$row[0].";");
			if ($resultb) while ($rowb=mysql_fetch_row($resultb)) {
				$orderlines[]=new xmlrpcval( array(
					"product_id" => new xmlrpcval($rowb[0], "int"),
					"product_qty" =>	new xmlrpcval($rowb[1], "int"),
					"price" =>	new xmlrpcval($rowb[2], "string")
				), "struct");
			}

			$fee=$row[23];
			$shipping_fee=$row[24];
			$other_fee=(-1 * $fee)+$shipping_fee;
			$orderlines[]=new xmlrpcval( array(
					"product_name" => new xmlrpcval("Other fees", "string"),
					"product_qty" =>	new xmlrpcval(0, "int"),
					"price" =>	new xmlrpcval($other_fee, "string")
				), "struct");
			//$orderlines[]=new xmlrpcval( array(
			//		"product_name" => new xmlrpcval("Shipping tax", "string"),
			//		"product_qty" =>	new xmlrpcval(0, "int"),
			//		"price" =>	new xmlrpcval($row[25], "string")
			//	), "struct");
			$saleorders[] = new xmlrpcval( array(
				"id" => new xmlrpcval( $row[0], "int"),
				"note" => new xmlrpcval( $row[22], "string"),
				"lines" =>		new xmlrpcval( $orderlines, "array"),
				"address" =>	new xmlrpcval( array(
					"name"		=> new xmlrpcval($row[16]." ".$row[1]." ".$row[17], "string"),
					"address"	=> new xmlrpcval($row[2], "string"),
					"city"		=> new xmlrpcval($row[3], "string"),
					"zip"		=> new xmlrpcval($row[4], "string"),
					"state"		=> new xmlrpcval($row[5], "string"),
					"country"	=> new xmlrpcval($row[6], "string"),
					"phone"		=> new xmlrpcval($row[7], "string"),
					"email"		=> new xmlrpcval($row[8], "string"),
					"esale_id"	=> new xmlrpcval($row[20], "string")
				), "struct"),
				"delivery" =>	new xmlrpcval( array(
					"name"		=> new xmlrpcval($row[18]." ".$row[9]." ".$row[19], "string"),
					"address"	=> new xmlrpcval($row[10], "string"),
					"city"		=> new xmlrpcval($row[11], "string"),
					"zip"		=> new xmlrpcval($row[12], "string"),
					"state"		=> new xmlrpcval($row[13], "string"),
					"country"	=> new xmlrpcval($row[14], "string"),
					"email"		=> new xmlrpcval($row[8], "string"),
					"esale_id"	=> new xmlrpcval($row[21], "string")
				), "struct"),
				"billing" =>new xmlrpcval( array(
					"name"		=> new xmlrpcval($row[16]." ".$row[1]." ".$row[17], "string"),
					"address"	=> new xmlrpcval($row[2], "string"),
					"city"		=> new xmlrpcval($row[3], "string"),
					"zip"		=> new xmlrpcval($row[4], "string"),
					"state"		=> new xmlrpcval($row[5], "string"),
					"country"	=> new xmlrpcval($row[6], "string"),
					"email"		=> new xmlrpcval($row[8], "string"),
					"esale_id"	=> new xmlrpcval($row[20], "string")
				), "struct"),
				"date" =>		new xmlrpcval( date('YmdHis',$row[15]), "date")
			), "struct");
		}
		return new xmlrpcresp(new xmlrpcval($saleorders, "array"));
	}

	function process_order($order_id) {
		global $mosConfig_dbprefix;
		mysql_query("update ".$mosConfig_dbprefix."vm_orders set order_status='C' where order_id=".$order_id.";");
		mysql_query("update ".$mosConfig_dbprefix."vm_order_item set oerder_status='C' where order_id=".$order_id.";");
		return new xmlrpcresp(new xmlrpcval(0, "int"));
	}

	function close_order($order_id) {
		global $mosConfig_dbprefix;
		mysql_query("update ".$mosConfig_dbprefix."vm_orders set order_status='S' where order_id=".$order_id.";");
		mysql_query("update ".$mosConfig_dbprefix."vm_order_item set oerder_status='S' where order_id=".$order_id.";");
		return new xmlrpcresp(new xmlrpcval(0, "int"));
	}

	$server = new xmlrpc_server( array(
		"get_taxes" => array(
			"function" => "get_taxes",
			"signature" => array(array($xmlrpcArray))
		),
		"get_languages" => array(
			"function" => "get_languages",
			"signature" => array(array($xmlrpcArray))
		),
		"get_categories" => array(
			"function" => "get_categories",
			"signature" => array(array($xmlrpcArray))
		),
		"get_saleorders" => array(
			"function" => "get_saleorders",
			"signature" => array(array($xmlrpcArray, $xmlrpcInt))
		),
		"set_product" => array(
			"function" => "set_product",
			"signature" => array(array($xmlrpcInt, $xmlrpcStruct))
		),
		"set_category" => array(
			"function" => "set_category",
			"signature" => array(array($xmlrpcInt, $xmlrpcStruct))
		),
		"set_tax" => array(
			"function" => "set_tax",
			"signature" => array(array($xmlrpcInt, $xmlrpcStruct))
		),

		"set_product_stock" => array(
			"function" => "set_product_stock",
			"signature" => array(array($xmlrpcInt, $xmlrpcStruct))
		),
		"process_order" => array(
			"function" => "process_order",
			"signature" => array(array($xmlrpcInt, $xmlrpcInt))
		),
		"delete_products" => array(
			"function" => "delete_products",
			"signature" => array(array($xmlrpcArray))
		),
		"delete_product_categories" => array(
			"function" => "delete_product_categories",
			"signature" => array(array($xmlrpcArray))
		),
		"close_order" => array(
			"function" => "close_order",
			"signature" => array(array($xmlrpcInt, $xmlrpcInt))
		),
		"unlink_products"=>array(
			"function" => "unlink_products",
			"signature" => array(array($xmlrpcInt, $xmlrpcArray))
		)
	), false);
	$server->functions_parameters_type= 'phpvals';
	$server->service();
?>