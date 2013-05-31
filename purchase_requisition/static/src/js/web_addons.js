openerp.purchase_requisition = function(instance) {

    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    instance.web.ListView.include({
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.on('list_view_loaded', this, function() {
                if (!!self.fields_view.arch.attrs.options) {
                    _.extend(self.options, py.eval(self.fields_view.arch.attrs.options));
                }
                if (!!self.options.generate_po) {
                    if(self.__parentedParent.$el.find('.oe_generate_po').length == 0){
                        var button = $("<button type='button' class='oe_button oe_highlight oe_generate_po'>Generate PO</button>")
                            .click(this.proxy('generate_purchase_order'));
                        self.__parentedParent.$el.find('.oe_list_buttons').append(button);
                    }                   
                }
            });
        },
        generate_purchase_order: function () {
            var self = this;
            new instance.web.Model(self.dataset.model).call("generate_po",[self.dataset.context.active_id,self.dataset.context]);
        },
    });
}