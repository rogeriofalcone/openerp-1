<div xmlns:py="http://purl.org/kid/ns#" py:strip="">
    <textarea py:if="editable and not inline"
        rows="10" id ="${field_id}" name="${name}" 
        class="${field_class}" kind="${kind}"
        callback="${callback}" onchange="${onchange}"
        py:attrs='attrs' py:content="value or None">
    </textarea>
    <script type="text/javascript" py:if="editable and not inline">
        if (!window.browser.isWebkit) {
            new ResizableTextarea('$field_id');
        }
    </script>

    <input py:if="editable and inline"
        id ="${field_id}" name="${name}"
        type="text" class="${field_class}" kind="${kind}"  
        callback="${callback}" onchange="${onchange}"
        value="${value or None}"
        py:attrs='attrs'/>
    
    <span py:if="editable and error" class="fielderror" py:content="error"/>
    <div py:if="not editable and value" kind="${kind}" id="${name}" class="${field_class}" py:content="XML(data)"/>
</div>
