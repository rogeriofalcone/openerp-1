/*---------------------------------------------------------
 * OpenERP Web Mobile Form View
 *---------------------------------------------------------*/

openerp.web_mobile.form_mobile = function (openerp) {

openerp.web_mobile.FormView = openerp.web.Widget.extend({
    init: function(session, element_id, list_id, action) {
        this._super(session, element_id);
        this.list_id = list_id;
        this.action = action;
        this.content_expanded_class = "ui-collapsible-content ui-collapsible-content-expanded";
        this.content_collapsed_class = "ui-collapsible-content ui-collapsible-content-collapsed";
        this.expanded_class = "ui-collapsible-content-expanded";
        this.collapsed_class = "ui-collapsible-content-collapsed";
        this.plus_class = "ui-icon-plus";
        this.minus_class = "ui-icon-minus";
    },
    start: function() {
        var self = this;
        var id = this.list_id;
        var model = this.action.res_model;
        var view_id = this.action.views[1][0];
        this.dataset = new openerp.web.DataSetSearch(this, this.action.res_model, null, null);
        var context = new openerp.web.CompoundContext(this.dataset.get_context());
        this.dataset.read_slice([],{}, function (result) {
            for (var i = 0; i < result.length; i++) {
                if (result[i].id == id) {
                    var data = result[i];
                }
            }
            self.rpc("/web/view/load", {"model": model, "view_id": view_id, "view_type": "form", context: context}, function (result) {
                var fields = result.fields;
                var view_fields = result.arch.children;
                var get_fields = self.get_fields(view_fields);
                var selection = new openerp.web_mobile.Selection();
                for (var j = 0; j < view_fields.length; j++) {
                    if (view_fields[j].tag == 'notebook') {
                        var notebooks = view_fields[j];
                    }
                }
                self.$element.html(QWeb.render("FormView", {'get_fields': get_fields, 'notebooks': notebooks || false, 'fields' : fields, 'values' : data ,'temp_flag':'1'}));

                    self.$element.find("[data-role=header]").find('h1').html(self.action.name);
                    self.$element.find("[data-role=header]").find('#home').click(function(){
                        $.mobile.changePage($("#oe_menu"), "slide", true, true);
                    });
                    self.$element.find("[data-role=footer]").find('#shrotcuts').click(function(){
                        if(!$('#oe_shortcuts').html().length){
                            this.shortcuts = new openerp.web_mobile.Shortcuts(self, "oe_shortcuts");
                            this.shortcuts.start();
                        }
                        else{
                            $.mobile.changePage($("#oe_shortcuts"), "slide", true, true);
                        }
                    });
                    self.$element.find("[data-role=footer]").find('#preference').click(function(){
                        if(!$('#oe_options').html().length){
                            this.options = new openerp.web_mobile.Options(self, "oe_options");
                            this.options.start();
                        }
                        else{
                            $.mobile.changePage($("#oe_options"), "slide", true, true);
                        }
                    });
                    self.$element.find('select').change(function(ev){
                        selection.on_select_option(ev);
                    });

                    self.$element.find('[data-role=collapsible-set]').find('[data-role=collapsible]').each(function(i){

                        for (var k = 0; k < notebooks.children.length; k++) {
                            if (notebooks.children[k].attrs.string == $(this).attr('id')) {
                                get_fields = self.get_fields(notebooks.children[k].children);
                                for (var i = 0; i < get_fields.length; i++) {
                                    if (fields[get_fields[i].attrs.name].type == 'one2many'){
                                        if(fields[get_fields[i].attrs.name].views.form){
                                            var get_fields_test = self.get_fields(fields[get_fields[i].attrs.name].views.form.arch.children);
                                            var fields_test = fields[get_fields[i].attrs.name]['views'].form.fields;
                                            var notebook=fields[get_fields[i].attrs.name].views.form.arch;
                                        }
                                    }
                                }
                            }
                            if(notebook){
                                $(this).find('p').html(QWeb.render("FormView", {'get_fields': get_fields,'fields' : result.fields, 'values' : data,'til': notebook.attrs.string }));
                            }else{
                                $(this).find('p').html(QWeb.render("FormView", {'get_fields': get_fields,'fields' : result.fields, 'values' : data }));
                            }
                        }
                    });

                    self.$element.find('[data-role=collapsible-set]').find('[data-role=collapsible]').find('p').find('[data-role=content]').find('ul').find('li').click(function(){

                    });
                    $.mobile.changePage($("#oe_form"), "slide", true, true);
                });
        });
    },
    get_fields: function(view_fields, fields) {
        this.fields = fields || [];
        for (var i=0; i < view_fields.length; i++){
            if (view_fields[i].tag == 'field') {
                this.fields.push(view_fields[i]);
            }
            if (view_fields[i].tag == 'group') {
                this.get_fields(view_fields[i].children, this.fields);
            }
        }
        return this.fields;
    }
});
};
