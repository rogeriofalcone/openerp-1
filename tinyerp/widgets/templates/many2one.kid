<table width="100%" cellpadding="0" cellspacing="0" xmlns:py="http://purl.org/kid/ns#">
    <tr>
        <td width="100%">
            <input type="hidden" name='${name}' value="${field_value}"/>
            <input style="width: 100%" type="text" id ='${field_id}' value="${text}" class="${field_class}"/>
            <br py:if="error"/><span class="fielderror" py:if="error" py:content="error"/>
        </td>
        <td>
            <div class="spacer" />
        </td>
        <td>
            <button type="button" onclick="wopen('/form/search_m2o?model=${relation}&amp;textid=${field_id}&amp;hiddenname=${name}', 'search', 800, 600)">Select</button>
        </td>
    </tr>
</table>
