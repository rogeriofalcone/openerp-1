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

var ListView = function(id, terp){
    this.id = id;
    this.terp = terp;
}

ListView.prototype.checkAll = function(clear){

    clear = clear == null ? true: clear;

    boxes = $(this.id).getElementsByTagName('input');
    forEach(boxes, function(box){
        box.checked = clear;
    });
}

ListView.prototype.getSelected = function() {

    boxes = getElementsByTagAndClassName('input', 'grid-record-selector', this.id);
    result = [];

    forEach(boxes, function(box){
        if (box.name && box.checked) result.push(box);
    });

    return result;
}

ListView.prototype.create = function(){
	this.edit(-1);
}

ListView.prototype.edit = function(id){
	this.reload(id);
}

ListView.prototype.getEditors = function(named, dom){

	var editors = [];
	var dom = dom ? dom : this.id;

	editors = editors.concat(getElementsByTagAndClassName('input', null, dom));
	editors = editors.concat(getElementsByTagAndClassName('select', null, dom));

	if (named)
		return filter(function(e){return e.name &&  e.name.indexOf('_terp_listfields') == 0;}, editors);
	else
		return filter(function(e){return e.id &&  e.id.indexOf('_terp_listfields') == 0;}, editors);
}

ListView.prototype.adjustEditors = function(newlist){

	var myself = this;
    var widths = {};

    if (items(myself.getEditors(true)).length == 0) {

        var header = getElementsByTagAndClassName('tr', 'grid-header', myself.id)[0];
        var columns = filter(function(c){return c.id;}, getElementsByTagAndClassName('td', 'grid-cell', header));
                
        forEach(columns, function(c){
            var k = c.id.split('/');
            k.shift(); 
            k = '_terp_listfields/' + k.join('/');
            
            var w = parseInt(c.offsetWidth);
            
            if (hasElementClass(c, 'datetime') || hasElementClass(c, 'date') || hasElementClass(c, 'time')) {
                w -= 18;
            }
            
            if (hasElementClass(c, 'many2one')) {
                w -= 34;
                k += '_text';
            }
                                            
            widths[k] = w - 4;
        });
    } else {
        forEach(myself.getEditors(), function(e){            
            widths[e.id] = parseInt(e.offsetWidth);
        });
    }

    forEach(myself.getEditors(false, newlist), function(e){
        var k = e.id;

        if (k in widths) {
            e.style.width = widths[k] + 'px';
            e.style.maxWidth = widths[k] + 'px';
        }
    });
}

ListView.prototype.save = function(id, model){

    var args = {};
    var parent_field = this.id.split('/');
    
    args['_terp_id'] = id;
    args['_terp_model'] = model;
    
    if (parent_field.length > 0){
		parent_field.pop();
	}
	
    parent_field = parent_field.join('/');
    parent_field = parent_field ? parent_field + '/' : '';
    
    args['_terp_parent/id'] = $(parent_field + '_terp_id').value;
    args['_terp_parent/model'] = $(parent_field + '_terp_model').value;
    args['_terp_parent/context'] = $(parent_field + '_terp_context').value;
    
    var myself = this;
    var editors = this.getEditors(true);
    
    forEach(editors, function(e){
   		// remove '_terp_listfields/' prefix
   		var n = e.name.split('/');
        n.shift();

        var f = '_terp_form/' + n.join('/');
        var k = '_terp_kind/' + n.join('/');
        var r = '_terp_required/' + n.join('/');

        args[f] = e.value;
        args[k] = e.attributes['kind'].value;        
        if (hasElementClass(e, 'requiredfield'))
        	args[k] += ' required';
    });

    var req= Ajax.JSON.post('/listgrid/save', args);

    req.addCallback(function(obj){
        if (obj.error){
           alert(obj.error);
        }else{
            myself.reload(id ? null : -1);
        }
    });    
}

ListView.prototype.remove = function(record_id){
}

ListView.prototype.reload = function(edit_inline){

	var myself = this;
    var args = {};
    
    args['_terp_source'] = this.id;
    args['_terp_edit_inline'] = edit_inline;

    args['_terp_model'] = $('_terp_model').value;
    args['_terp_id'] = $('_terp_id').value;
    args['_terp_view_ids'] = $('_terp_view_ids').value;
    args['_terp_context'] = $('_terp_context').value;

    var req = Ajax.JSON.post('/listgrid/get', args);
    
    req.addCallback(function(obj){
    	
    	var ids = $(myself.id + '/_terp_ids');
    	ids = ids ? ids : $('_terp_ids');
    	
    	ids.value = obj.ids;

        var d = DIV();
        d.innerHTML = obj.view;

        var newlist = d.getElementsByTagName('table')[0];
        
		myself.adjustEditors(newlist);		

        swapDOM(myself.id, newlist);
    });
    
    req.addErrback(function(err){
        logError(err);
    });
}
