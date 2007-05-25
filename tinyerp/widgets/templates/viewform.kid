<form xmlns:py="http://purl.org/kid/ns#" method="post" id="${name}" name="${name}" action="${action}" enctype="multipart/form-data">
    <span py:for="field in hidden_fields" py:replace="field.display(value_for(field), **params_for(field))"/>
 
    <script type="text/javascript">    
        function toggle_sidebar(element_id) {
        	var elem = $(element_id);
                       
            if (elem){
                elem.style.display = elem.style.display == "none" ? "" : "none";
                set_cookie("terp_sidebar", elem.style.display);
           	}
        }
    </script>

    <table border="0" cellpadding="0" cellspacing="0" width="100%" py:if="screen">
        <tr>
            <td valign="top" py:content="screen.display(value_for(screen), **params_for(screen))" width="100%"></td>
            <td py:if="screen.hastoolbar and screen.toolbar" width="163" valign="top" style="padding-left: 4px">
		
				<table border="0" cellpadding="0" cellspacing="0" width="160" id="sidebar" style="display:none">
	                <tr py:if="'print' in screen.toolbar">
	                    <td>
				    		<table border="0" cellpadding="0" cellspacing="0" width="100%">
								<tr>
									<td width="8" bgcolor="#ac0000"></td>
									<td width="7" bgcolor="#363636"></td>
									<td bgcolor="#363636" style="font:verdana; color:white; font-weight:bold; font-size:12px">
										REPORTS
									</td>
									<td width="25" bgcolor="#666666" valign="top">
										<img src="/static/images/head_diagonal.png"/>
									</td>
									<td bgcolor="#666666" width="50"></td>
								</tr>
							
	    						<tr py:for="item in screen.toolbar['print']" data="${str(item)}" onclick="submit_form('action', null, getNodeAttribute(this, 'data'))">
	    						    <td colspan="5">
									    <a href="#">${item['string']}</a>								    
									</td>
						        </tr>
						    </table>
                        </td>
                    </tr>
					<tr py:if="'action' in screen.toolbar">
                        <td>											
							<table border="0" cellpadding="0" cellspacing="0" width="100%">
								<tr>
									<td width="8" bgcolor="#ac0000"></td>
									<td width="7" bgcolor="#363636"></td>
									<td bgcolor="#363636" style="font:verdana; color:white; font-weight:bold; font-size:12px">
										ACTIONS
									</td>
									<td width="25" bgcolor="#666666" valign="top">
										<img src="/static/images/head_diagonal.png"/>
									</td>
									<td bgcolor="#666666" width="50"></td>
								</tr>
	    						<tr py:for="item in screen.toolbar['action']" data="${str(item)}" onclick="submit_form('action', null, getNodeAttribute(this, 'data'))">
	    						    <td colspan="5">			    
							    	    <a href="#">${item['string']}</a>										       			   	
	            				    </td>
	        				    </tr>
			    		    </table>
			    		</td>
			    	</tr>
			    </table>	          
		    </td>	  		    
            
            <td id="sidebar_hide" valign="top">
                <a href="#" onclick="toggle_sidebar('sidebar');">
                    <img src="/static/images/sidebar_hide.png" alt="|" border="0"/>
                </a>
            </td>
        </tr>
    </table>
</form>
