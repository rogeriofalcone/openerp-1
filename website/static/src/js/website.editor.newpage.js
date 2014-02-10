(function() {
    "use strict";

    var website = openerp.website;
    var _t = openerp._t;
    website.is_editable = true;
    website.is_editable_button = true;
    
    website.EditorBar.include({
        start: function() {
            var res = this._super();
            this.$("a[data-action=new_page]").parents("li").removeClass("hidden");
            this.$(".oe_content_menu li.divider").removeClass("hidden");
            return res;
        },
        events: _.extend({}, website.EditorBar.prototype.events, {
            'click a[data-action=new_page]': function (ev) {
                ev.preventDefault();
                website.prompt({
                    id: "editor_new_page",
                    window_title: _t("New Page"),
                    input: "Page Title",
                }).then(function (val) {
                    if (val) {
                        document.location = '/website/add/' + encodeURI(val);
                    }
                });
            }
        }),
    });
})();