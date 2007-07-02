<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="tinyerp/templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Login</title>
    
</head>

<body onload="hideElement('showbar')">
    <div class="view">
		<div class="box2 welcome">Create Database</div>    
		<form action="/dbadmin/create" method="post" name="create">        
            <div class="box2" id="create">
				<table align="center" border="0" width="100%">
					<tr>
		                <td align="right" class="label">
		                    Super admin password :
		                </td>
		                <td>
		                    <input type="password" name="password" style="width: 99%;"/>
		                </td>
		            </tr>
		            <tr>
		                <td></td>
		                <td>
		                    (use 'admin', if you did not changed it)
		                </td>
		            </tr>

			        <tr>
		                <td align="right" class="label">
		                    New database name :
		                </td>
		                <td>
		                    <input type="text" name="db_name" style="width: 99%;"/>
		                </td>
		            </tr>
		            <tr>
		                <td align='right' class="label">
		                    Load Demonstration data :
		                </td>
		                <td>
		                    <input type="checkbox" name="demo_data" value="True" checked="checked"/>
		                </td>
		            </tr>
		            <tr>
		                <td align='right' class="label">
		                    Default Language :
		                </td>
		                <td>
		                    <select name="language" style="width: 100%;">
	                            <option py:for="i, key in enumerate(langlist)" value="${langlist[i][0]}" py:content="langlist[i][1]" selected="${(i+1 == len(langlist) or None) and 1}">Language</option>
		                    </select>
		                </td>
		            </tr>
		        </table>
			</div>

			<div align="right" class="box2">
                <button type="button" onclick="window.location.href='/dbadmin'">Cancel</button>
                <button type="submit">OK</button>
    		</div>
    		
			<div class="box message" id="message" py:if="message" py:content="message"/>
        </form>
    </div>
</body>
</html>
