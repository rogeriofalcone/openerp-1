///////////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
//
// $Id$
//
// WARNING: This program as such is intended to be used by professional
// programmers who take the whole responsability of assessing all potential
// consequences resulting from its eventual inadequacies and bugs
// End users who are looking for a ready-to-use solution with commercial
// garantees and support are strongly adviced to contract a Free Software
// Service Company
//
// This program is Free Software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
//
///////////////////////////////////////////////////////////////////////////////

function get_form_action(action, params){
	var act = typeof(form_controller) == 'undefined' ? '/form' : form_controller;
	act = action && action.indexOf('/') == 0 ? action : act + '/' + action;

	return getURL(act, params);
}

var newO2M = function(src, mode, editors){

	var prefix = src + '/';
	var parent_prefix = src.indexOf('/') > -1 ? src.slice(0, src.lastIndexOf('/')+1) : '';

	var parent_id = $(parent_prefix + '_terp_id').value;

	if (!parent_id || parent_id == 'False' || mode == 'form'){
		return submit_form('save', src);
	}

	if (mode == 'tree' && editors > 0){
		return new ListView(src).create();
	}

	return editO2M(null, src);
}

var editO2M = function(id, src){

	var prefix = src + '/';
	var parent_prefix = src.indexOf('/') > -1 ? src.slice(0, src.lastIndexOf('/')+1) : '';

	var model = $(prefix + '_terp_model').value;

	var parent_model = $(parent_prefix + '_terp_model').value;
	var parent_id = $(parent_prefix + '_terp_id').value;

	var args = {_terp_parent_model: parent_model,
				_terp_parent_id: parent_id,
				_terp_o2m: src,
				_terp_o2m_model: model,
				_terp_o2m_id: id};

	openWindow(getURL('/openo2m/edit', args));
}

var editRecord = function(id, src){

	if (src && src != '_terp_list' && $('_terp_count').value != '0') {
		return editO2M(id, src);
	}

	var prefix = src && src != '_terp_list' ? src + '/' : '';

	var model = $(prefix + '_terp_model').value;
	var view_ids = $(prefix + '_terp_view_ids').value;
	var view_mode = $(prefix + '_terp_view_mode').value;

	var ids = $(prefix + '_terp_ids').value;

	var offset = $(prefix + '_terp_offset').value;
	var limit = $(prefix + '_terp_limit').value;
	var count = $(prefix + '_terp_count').value;

	var domain = $(prefix + '_terp_domain').value;
	var context = $(prefix + '_terp_context').value;

	var search_domain = $('_terp_search_domain');
	search_domain = search_domain ? search_domain.value : null;

	var args = {'model': model,
				'id': id ? id : 'False',
				'ids': ids,
				'view_ids': view_ids,
				'view_mode': view_mode,
				'domain': domain,
				'context': context,
				'offset': offset,
				'limit': limit,
				'count': count,
				'search_domain': search_domain};

	window.location.href = get_form_action('edit', args);
}

var viewRecord = function(id, src){

	var prefix = src && src != '_terp_list' ? src + '/' : '';
	var model = $(prefix + '_terp_model').value;
	var view_ids = $(prefix + '_terp_view_ids').value;
	var view_mode = $(prefix + '_terp_view_mode').value;

	var ids = $(prefix + '_terp_ids').value;

	var offset = $(prefix + '_terp_offset').value;
	var limit = $(prefix + '_terp_limit').value;
	var count = $(prefix + '_terp_count').value;

	var domain = $(prefix + '_terp_domain').value;
	var context = $(prefix + '_terp_context').value;

	var search_domain = $('_terp_search_domain');
	search_domain = search_domain ? search_domain.value : null;

	var args = {'model': model,
				'id': id ? id : 'False',
				'ids': ids,
				'view_ids': view_ids,
				'view_mode': view_mode,
				'domain': domain,
				'context': context,
				'offset': offset,
				'limit': limit,
				'count': count,
				'search_domain': search_domain};

	window.location.href = get_form_action('view', args);
}

var switchView = function(view_type, src){

    var prefix = src ? src + '/' : '';
    var form = $("view_form");

    var params = {
        '_terp_source': src,
        '_terp_source_view_type': view_type
    }

    if (getElement('_terp_list')){
        var ids = new ListView('_terp_list').getSelectedRecords();
        if (ids.length > 0) {
            $('_terp_id').value = ids[0];
        }
    }

    submit_form(get_form_action('switch', params));
}

var submit_form = function(action, src, data){
    
    if (Ajax.COUNT > 0) {
        return callLater(1, submit_form, action, src, data);
    }

    if (action == 'delete' &&  !confirm('Do you realy want to delete this record?')) {
        return false;
    }

    form = $("view_form");
    setNodeAttribute(form, 'target', '');

    source = src ? (typeof(src) == "string" ? src : src.name) : null;

    args = {
        _terp_source: source,
        _terp_data: data ? data : null
    };

    if (action == 'action' && $('_terp_list')){
    	var list = new ListView('_terp_list');
    	var ids = list.getSelectedRecords();

    	if (ids.length == 0) {
    	   return alert('You must select at least one record.');
    	}

    	args['_terp_selection'] = '[' + ids.join(',') + ']';
    }

    if (action == 'report' || (action == 'action' && data)){
        setNodeAttribute(form, 'target', '_blank');
    }

    if ((action == 'report') || (data && action == 'action' && data.indexOf('ir.actions.report') > -1)) {
        action =  action + '/report.pdf'
    }

    setNodeAttribute(form, 'action', get_form_action(action, args));
    form.submit();
}

var submit_search_form = function(action) {

	if ($('search_view_notebook')) {

	    // disable fields of hidden tab

	    var hidden_tab = getElementsByTagAndClassName('div', 'tabbertabhide', 'search_view_notebook')[0];
	    var disabled = [];

	    disabled = disabled.concat(getElementsByTagAndClassName('input', null, hidden_tab));
	    disabled = disabled.concat(getElementsByTagAndClassName('textarea', null, hidden_tab));
	    disabled = disabled.concat(getElementsByTagAndClassName('select', null, hidden_tab));

	    forEach(disabled, function(fld){
	        fld.disabled = true;
	    });
	}

	submit_form(action ? action : 'find');
}

var clear_search_form = function() {

    if ($('search_view_notebook')) {

        var fields = [];

        fields = fields.concat(getElementsByTagAndClassName('input', null, 'search_view_notebook'));
        fields = fields.concat(getElementsByTagAndClassName('textarea', null, 'search_view_notebook'));
        fields = fields.concat(getElementsByTagAndClassName('select', null, 'search_view_notebook'));

        forEach(fields, function(fld){
            fld.value = '';
        });
    }
}

var pager_action = function(action, src) {
    if (src)
        new ListView(src).go(action);
    else
        submit_search_form(action);
}

var save_binary_data = function(src) {
    var name = $(src) ? $(src).name : src;
    var fname = $(name + 'name');

    var act = '/form/save_binary_data';

    act = fname ? act + '/' + fname.value : act;

    act = act + '?_terp_field=' + name;

    submit_form(act);
}

var buttonClicked = function(name, btype, model, id, sure){

    if (sure && !confirm(sure)){
        return;
    }

    params = {};

    params['_terp_button/name'] = name;
    params['_terp_button/btype'] = btype;
    params['_terp_button/model'] = model;
    params['_terp_button/id'] = id;

    submit_form(get_form_action('save', params));
}

/**
 * get key-pair object of the form data
 * 
 * if extended is
 *    1 then give form data with type info
 *    2 then give form data with type info + required flag
 * else gives simple key-value pairs 
 */
var getFormData = function(extended) {
    
    var parentNode = $('_terp_list') || $('view_form');

    var frm = {};
    var fields = [];

    fields = fields.concat(getElementsByTagAndClassName('input', null, parentNode));
    fields = fields.concat(getElementsByTagAndClassName('select', null, parentNode));
    fields = fields.concat(getElementsByTagAndClassName('textarea', null, parentNode));

    forEach(fields, function(e){

        if (!e.name)
            return;

        var n = e.name.replace('_terp_listfields/', '');

        if (n.indexOf('_terp_') > -1 || n.indexOf('/__id') > -1)
            return;

        if (extended) {
        
            var attrs = {};
            
            var value = e.value;
            var kind = null;
            
            value = e.value;            
            kind = getNodeAttribute(e, 'kind');
            
            attrs['value'] = value;
            
            if (kind)
                attrs['type'] = kind;
                
            if (extended > 1 && hasElementClass(e, 'requiredfield'))
                attrs['required'] =  1;

            if (value && (kind == "text" || kind == "char"))
                attrs['value'] = '""' + value + '""';

            // pythonize the attr object
            attrs = map(function(x){return '"' + x[0] + '"' + ':' + '"' + x[1] + '"'}, items(attrs));            
            frm[n] = "{" + attrs.join(", ") + "}";
            
        } else {
            frm[n] = value;
        }
    });

    return frm;
}

/*
 * get key-value pair of form params (_terp_)
 *
 */
var getFormParams = function(){
        
    var parentNode = $('view_form');
        
    var frm = {};
    var fields = [];
        
    fields = fields.concat(getElementsByTagAndClassName('input', null, parentNode));

    forEach(fields, function(e){

        if (!e.name || e.name.indexOf('_terp_listfields/') > -1 || e.name.indexOf('_terp_') == -1)
            return

        frm[e.name] = e.value;
    });

    return frm;
}

/**
 * This function will be used by widgets that has `onchange` trigger is defined.
 */
var onChange = function(name) {

    var caller = $(name);
    var callback = getNodeAttribute(caller, 'callback');

   	var is_list = caller.id.indexOf('_terp_listfields') == 0;

    var prefix = caller.name.split("/");
    prefix.pop();
    prefix = prefix.join("/");
    prefix = prefix ? prefix + '/' : '';

    var vals = getFormData(1);
    var model = is_list ? $(prefix.slice(17) + '_terp_model').value : $(prefix + '_terp_model').value;

    if (!callback)
        return;

    vals['_terp_caller'] = is_list ? caller.id.slice(17) : caller.id;
    vals['_terp_callback'] = callback;
    vals['_terp_model'] = model;

    req = Ajax.JSON.post('/form/on_change', vals);

    req.addCallback(function(obj){

    	if (obj.error) {
    		return alert(obj.error);
    	}

        values = obj['value'];
        domains = obj['domain'];

        domains = domains ? domains : {};

        for(var k in domains){
        	fld = $(prefix + k);
        	if (fld){
        		setNodeAttribute(fld, 'domain', domains[k]);
        	}
        }

		for(var k in values){
			flag = false;
            fld = $(prefix + k);
            if (fld) {
                value = values[k];
                value = value === false || value === null ? '' : value

				if ($(prefix + k + '_id')){
                	fld = $(prefix + k + '_id');
                	flag = true;
                }

                if ((fld.value != value) || flag) {
                	fld.value = value;

                	var kind = getNodeAttribute(fld, 'kind');

                	if (kind == 'many2one' || kind == 'reference'){
                	   getName(fld);
                	}

                	if (kind == 'many2many'){
                	   fld.onchange();
                	}
               	}
            }
        }
    });
}

/**
 * This function will be used by many2one field to get display name.
 *
 * @param name: name/instance of the widget
 * @param relation: the TinyERP model
 *
 * @return string
 */
function getName(name, relation){

    var value_field = $(name);
    var text_field = $(value_field.name + '_text');

    relation = relation ? relation : getNodeAttribute(value_field, 'relation');

    if (value_field.value == ''){
        text_field.value = ''
    }

    if (value_field.value){
        var req = Ajax.JSON.get('/search/get_name', {model: relation, id : value_field.value});
        req.addCallback(function(obj){
            text_field.value = obj.name;
        });
    }
}

function eval_domain_context_request(options){

	var prefix = options.source.split("/");
    prefix.pop();

    // editable listview fields
    if (prefix[0] == '_terp_listfields'){
    	prefix.shift();
    }
	
	var params = getFormData(1);
	
	params['_terp_domain'] = options.domain;
	params['_terp_context'] = options.context;
	params['_terp_prefix'] = prefix;
	
    return Ajax.JSON.post('/search/eval_domain_and_context', params);
}

function open_search_window(relation, domain, context, source, kind, text) {

	if (text || (domain == '' || domain == '[]') && (context == '' || context == '{}')){
		return openWindow(getURL('/search/new', {model: relation, domain: '[]', context: '{}', source: source, kind: kind, text: text}));
	}

	var req = eval_domain_context_request({source: source, domain: domain, context: context});

	req.addCallback(function(obj){
		openWindow(getURL('/search/new', {model: relation, domain: obj.domain, context: obj.context, source: source, kind: kind, text: text}));
    });
}

function makeContextMenu(id, kind, relation, val) {

    var form = $('view_form');
    var act = get_form_action('get_context_menu');

    var prefix = id.indexOf('/') > -1 ? id.slice(0, id.lastIndexOf('/')) + '/' : '';

	var model = prefix ? $(prefix + '_terp_model').value : $('_terp_model').value;

    var params = {'model': model, 'field': id, 'kind': kind, 'relation': relation, 'value': val};

    var req = Ajax.JSON.post(act, params);

    req.addCallback(function(obj) {

        var rows = [];

        for(var r in obj.defaults) {
            var o = obj.defaults[r];
            var a = A({href: "javascript: void(0)", onclick: 'hideElement("contextmenu"); return ' + o.action}, o.text);
            rows = rows.concat(a);
        }

        if(obj.actions.length > 0) {
            rows = rows.concat(HR());

	        for(var r in obj.actions) {
	            var o = obj.actions[r];

	            var a = A({href: "javascript: void(0)", onclick: o.action ? 'hideElement("contextmenu"); return ' + o.action : '', 'class': o.action ? '' : 'disabled'}, o.text);

	            rows = rows.concat(a);
	        }
	    }

        if(obj.relates.length > 0) {
            rows = rows.concat(HR())

	        for(var r in obj.relates) {
                var o = obj.relates[r];

	            var a = A({href: "javascript: void(0)", data: o.data, onclick: o.action ? 'hideElement(\'contextmenu\'); return ' + o.action : '', 'class': o.action ? '' : 'disabled'}, o.text);
	            rows = rows.concat(a);
	        }
        }

        $('contextmenu').innerHTML = '';

        var tbl = TABLE({'cellpadding': 0, 'cellspacing' : 1}, TBODY(null, map(function(r){return TR(null, TD(null, r));}, rows)));
        appendChildNodes('contextmenu', tbl);

        var vd = getViewportDimensions();
        var md = elementDimensions('contextmenu');

        var x = $('contextmenu').style.left.slice(0, -2);
        x = parseInt(x);

        if ((x + md.w) > vd.w) {
        	x -= x + md.w - vd.w;
        	$('contextmenu').style.left = x + 'px';
        }

        showContextMenu();
	});
}

var showContextMenu = function(){

	var menu = $('contextmenu');
	var ifrm = $('contextmenu_frm');

	showElement(menu);

	if (ifrm){
	
		ifrm.style.left = menu.offsetLeft + "px";
		ifrm.style.top = menu.offsetTop + "px";
		ifrm.style.width = menu.offsetWidth + "px";
		ifrm.style.height = menu.offsetHeight + "px";
		ifrm.style.zIndex = 6;

        showElement(ifrm);
	}
}

var hideContextMenu = function(){
	var menu = $('contextmenu');
	var ifrm = $('contextmenu_frm');

	if (ifrm){
		hideElement(ifrm);
	}

	hideElement(menu);
}

var m2oContextMenu = function(src){

	var btn = $(src);
    var menu = $('contextmenu');
    
    if (!menu) {
        menu = DIV({id:"contextmenu", 'class' : 'contextmenu', 'onmouseout':'hideContextMenu()', 'onmouseover':'showContextMenu()', 'style':'position: absolute; display: none;'});
        appendChildNodes(document.body, menu);       

        if (/msie/.test(navigator.userAgent.toLowerCase())) {
            var ifrm = createDOM('IFRAME', {'id':'contextmenu_frm', 'src' : '#', 'frameborder': '0', 'scrolling':'no', 'style':'position: absolute; display: none;'});
            appendChildNodes(document.body, frm);
        }
    }
    
    var src = $(src).id.slice(0, -5);
    src = $(src);

    var val = $(src.id).value;
    var kind = getNodeAttribute(src, 'kind');
    var relation = getNodeAttribute(src, 'relation');

    hideElement(menu);

    var p = elementPosition(btn);
    var d = elementDimensions(btn);

    if (typeof(opera) != 'undefined') {
        p = findPosition(btn);
    }

    p.y += d.h;
    setElementPosition(menu, p);

    makeContextMenu(src.id, kind, relation, val);
}

function set_to_default(field, model){

	var kind = getNodeAttribute($(field), 'kind');

    var act = get_form_action('get_default_value');
    var params = {'model': model, 'field': field};

    var req = Ajax.JSON.post(act, params);
    req.addCallback(function(obj) {

        $(field).value = obj.value;
        signal(field, "onchange");
    });
}

function set_as_default(field, model){

	var kind = getNodeAttribute($(field), 'kind');

	var args = getFormData(1);
	args['_terp_model'] = model;
	args['_terp_field'] = field;

	var req = Ajax.JSON.post('/fieldpref/get', args);

	req.addCallback(function(obj){
		var text = obj.text;
		var params = {'_terp_model': model, '_terp_field/name': field, '_terp_field/string': text, '_terp_field/value': $(field).value, '_terp_deps': obj.deps};
		openWindow(getURL('/fieldpref', params), {width: 500, height: 350});
	});
}

function do_action(id, relation) {

    id = $(id).value;

    var act = get_form_action('action');
    var params = {'_terp_model': relation, '_terp_id': id};

    window.open(getURL(act, params));
}

function do_print(id, relation) {

    id = $(id).value;

    var act = get_form_action('report/report.pdf');
    var params = {'_terp_model': relation, '_terp_id': id};

    window.open(getURL(act, params));
}

function do_relate(action_id, field, relation, src) {

    var id = $(field).value;
    var data = getNodeAttribute(src, 'data');

    var act = get_form_action('action');
    var params = {'_terp_data': data, '_terp_id': id, '_terp_model': relation};

    window.open(getURL(act, params));
}

