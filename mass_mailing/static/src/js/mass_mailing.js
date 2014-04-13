openerp.mass_mailing = function (instance) {
    var _t = instance.web._t;
	debugger;

    openerp.mass_mailing = function(openerp) {
        openerp.web_kanban.KanbanRecord.include({
            on_card_clicked: function (event) {
                if (this.view.dataset.model === 'mail.mass_mailing.campaign') {
                    this.$('.oe_mailings').click();
                } else {
                    this._super.apply(this, arguments);
                }
            },
        });
    };

    instance.web.form.CharDomainButton = instance.web.form.AbstractField.extend({
        template: 'CharDomainButton',
        init: function(field_manager, node) {
            this._super.apply(this, arguments);
        },
        start: function() {
            var self=this;
            this._super.apply(this, arguments);
            $('button', this.$el).on('click', self.on_click);
            this.set_button();
        },
        set_button: function() {
            if (this.get('value')) {
                // TODO: rpc to copute X
                $('.oe_domain_count', this.$el).text('X records selected');
                $('button span', this.$el).text(' Change selection');
            } else {
                $('.oe_domain_count', this.$el).text('0 record selected');
                $('button span', this.$el).text(' Select records');
            };
        },
        on_click: function(ev) {
            var self = this;
            var model = this.options.model || this.field_manager.get_field_value(this.options.model_field);
            this.pop = new instance.web.form.SelectCreatePopup(this);
            this.pop.select_element(
                model, {title: 'Select records...'},
                [], this.build_context());
            this.pop.on("elements_selected", self, function() {
                var self2 = this;
                var search_data = this.pop.searchview.build_search_data()
                instance.web.pyeval.eval_domains_and_contexts({
                    domains: search_data.domains,
                    contexts: search_data.contexts,
                    group_by_seq: search_data.groupbys || []
                }).then(function (results) {
                    var domain = self2.pop.dataset.domain.concat(results.domain || []);
                    self.set_value(JSON.stringify(domain))
                });
            });
            event.preventDefault();
        },
        set_value: function(value_) {
            var self = this;
            this.set('value', value_ || false);
            this.set_button();
         },
    });

    instance.web.form.widgets = instance.web.form.widgets.extend(
        {'char_domain': 'instance.web.form.CharDomainButton'}
    );

};
