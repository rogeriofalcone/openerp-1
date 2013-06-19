openerp.hr_recruitment = function (openerp) {

  openerp.hr_recruitment.GaugeWidget = openerp.web_kanban.AbstractField.extend({
    start: function() {
        var self = this;
        var parent = self.getParent();
        var unique_id = _.uniqueId("JustGage");
        var label = this.options.label_field ? parent.record[this.options.label_field].string : "";
        var value = parent.values.no_of_hired_employee.value;
        var flag_open = false;
        this.$el.empty()
            .attr('id', unique_id)
            .attr('class','oe_justgage');
        this.gage = new JustGage({
            id: unique_id,
            node: this.$el[0],
            value: value,
            min: 0,
            max: self.field.raw_value,
            relativeGaugeSize: true,
            humanFriendly: true,
            titleFontColor: '#333333',
            valueFontColor: '#333333',
            labelFontColor: '#808080',
            showInnerShadow:true,
            label: label,
            levelColors: [
                "#ff0000",
                "#f9c802",
                "#a9d70b"
            ],
        });
        if (self.options.action_change) {
            self.$el.click(function (event) {
                event.stopPropagation();
                flag_open = false;
                if (!parent.view.is_action_enabled('edit')) {
                    return;
                }
                if (!self.$el.find(".oe_justgage_edit").size()) {
                    var $svg = self.$el.find('svg');
                    $div = $('<div class="oe_justgage_edit" style="text-align: center; z-index: 1; position: absolute; width: ' + $svg.outerWidth() + 'px; top: ' + ($svg.outerHeight()/2+20) + 'px;"/>');
                    $input = $('<input style="text-align: center; width: ' + ($svg.outerWidth()/2) + 'px; margin: auto;"/>').val(value);
                    $div.append($input);
                    self.$el.prepend($div)
                    $input.focus()
                        .keydown(function (event) {
                            event.stopPropagation();
                            if (event.keyCode == 13 || event.keyCode == 9) {
                                if ($input.val() != value) {
                                    parent.view.dataset.call(self.options.action_change, [parent.id, $input.val()]).then(function () {
                                        parent.do_reload();
                                    });
                                } else { $div.remove();}
                            }
                        })
                        .click(function (event) {
                            event.stopPropagation();
                            flag_open = false;
                        })
                        .blur(function (event) {
                            if(!flag_open) {
                                self.$el.find(".oe_justgage_edit").remove();
                            } else {
                                flag_open = false;
                                setTimeout(function () {$input.focus();}, 0);
                            }
                        });
                }
            }).mousedown(function () {
                flag_open = true;
            });
        }
    },
  });

  openerp.web_kanban.KanbanRecord.include({
      on_card_clicked: function() {
          if (this.view.dataset.model === 'hr.job') {
              this.$('.oe_applications a').first().click();
          } else {
              this._super.apply(this, arguments);
          }
      },
  });

  openerp.web_kanban.fields_registry.add("justgage", "openerp.hr_recruitment.GaugeWidget");
}
