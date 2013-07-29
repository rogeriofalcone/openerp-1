openerp.website = function(instance) {
var _lt = instance.web._lt;
instance.website.EditorBar = instance.web.Widget.extend({
    template: 'Website.EditorBar',
    events: {
        'click button[data-action=edit]': 'edit',
        'click button[data-action=save]': 'save',
        'click button[data-action=cancel]': 'cancel',
        'click button[data-action=snippet]': 'snippet',
    },
    container: 'body',
    init: function () {
        this._super.apply(this, arguments);
        this.saving_mutex = new $.Mutex();
    },
    start: function() {
        var self = this;

        this.$('button[data-action]').prop('disabled', true);
        this.$buttons = {
            edit: this.$('button[data-action=edit]'),
            save: this.$('button[data-action=save]'),
            cancel: this.$('button[data-action=cancel]'),
            snippet: this.$('button[data-action=snippet]'),
        };
        this.$buttons.edit.add(this.$buttons.snippet).prop('disabled', false);

        self.snippet_start();

        this.rte = new instance.website.RTE(this);
        this.rte.on('change', this, this.proxy('rte_changed'));

        return $.when(
            this._super.apply(this, arguments),
            this.rte.appendTo(this.$el)
        );
    },
    edit: function () {
        this.$buttons.edit.prop('disabled', true);
        this.$buttons.cancel.prop('disabled', false);
        // TODO: span edition changing edition state (save button)
        this.rte.start_edition(
                $('[data-oe-model]')
                    .not('link, script')
                    .prop('contentEditable', true)
                    .addClass('oe_editable'));
    },
    rte_changed: function () {
        this.$buttons.save.prop('disabled', false);
    },
    save: function () {
        var self = this;
        var defs = [];
        $('.oe_dirty').each(function (i, v) {
            var $el = $(this);
            // TODO: Add a queue with concurrency limit in webclient
            // https://github.com/medikoo/deferred/blob/master/lib/ext/function/gate.js
            var def = self.saving_mutex.exec(function () {
                return self.saveElement($el).then(function () {
                    $el.removeClass('oe_dirty');
                }).fail(function () {
                    var data = $el.data();
                    console.error(_.str.sprintf('Could not save %s#%d#%s', data.oeModel, data.oeId, data.oeField));
                });
            });
            defs.push(def);
        });
        return $.when.apply(null, defs).then(function () {
            window.location.reload();
        });
    },
    saveElement: function ($el) {
        var data = $el.data();
        var html = $el.html();
        var xpath = data.oeXpath;
        if (xpath) {
            var $w = $el.clone();
            $w.removeClass('oe_dirty');
            _.each(['model', 'id', 'field', 'xpath'], function(d) {$w.removeAttr('data-oe-' + d);});
            $w
                .removeClass('oe_editable')
                .prop('contentEditable', false);
            html = $w.wrap('<div>').parent().html();
        }
        return (new instance.web.DataSet(this, 'ir.ui.view')).call('save', [data.oeModel, data.oeId, data.oeField, html, xpath]);
    },
    cancel: function () {
        window.location.reload();
    },
    snippet_start: function () {
        var self = this;
        $('.oe_snippet').click(function(ev) {
            $('.oe_selected').removeClass('oe_selected');
            var $snippet = $(ev.currentTarget);
            $snippet.addClass('oe_selected');
            $snippet.draggable();
            var selector = $snippet.data("selector");
            var $zone = $(".oe_website_body " + selector);
            var droppable = '<div class="oe_snippet_drop" style="border:1px solid red;">.<br/>.<br/>.<br/>.<br/>.<br/></div>';
            $zone.before(droppable);
            $zone.after(droppable);
            $(".oe_snippet_drop").droppable({
                drop: function( event, ui ) {
                    console.log(event, ui, "DROP");
                    var $target = $(event.target);
                    $target.before($snippet.html());
                    $('.oe_selected').remove();
                    $('.oe_snippet_drop').remove();
                }
            });
        });

    },
    snippet: function (ev) {
        $('.oe_snippet_editor').toggle();
    },
});

instance.website.Action = instance.web.Widget.extend({
    tagName: 'button',
    attributes: {
        type: 'button',
    },
    events: { click: 'perform' },
    init: function (parent, name) {
        this._super(parent);
        this.name = name;
    },
    start: function () {
        this.$el.text(this.name);
        return this._super();
    },
    /**
     * Executes action
     */
    perform: null
});
var Style = instance.website.Style = instance.website.Action.extend({
    init: function (parent, name, style) {
        this._super(parent, name);
        this.style = style;
    },
    perform: function () {
        this.getParent().with_editor(function (editor) {
            editor.applyStyle(new CKEDITOR.style(this.style))
        }.bind(this));
    },
});
var Command = instance.website.Command = instance.website.Action.extend({
    init: function (parent, name, command) {
        this._super(parent, name);
        this.command = command;
    },
    perform: function () {
        this.getParent().with_editor(function (editor) {
            switch (typeof this.command) {
            case 'string': editor.execCommand(this.command); break;
            case 'function': this.command(editor); break;
            }
        }.bind(this));
    },
});
var Group = instance.website.ActionGroup = instance.website.Action.extend({
    template: 'Website.ActionGroup',
    events: { 'click > button': 'perform' },
    instances: [],
    init: function (parent, name, actions) {
        this._super(parent, name);
        this.actions = _(actions).map(this.getParent().proxy('init_command'));
    },
    start: function () {
        this.instances.push(this);
        var $ul = this.$('ul');
        return $.when.apply(null, _(this.actions).map(function (action) {
            var $li = $('<li>').appendTo($ul);
            return action.appendTo($li);
        }));
    },
    destroy: function () {
        this.instances = _(this.instances).without(this);
        return this._super();
    },
    perform: function () {
        this.getParent().with_editor(function () {
            _(this.instances).chain()
                .without(this)
                .pluck('$el')
                .invoke('removeClass', 'open');
            // JS part of bootstrap dropdown does really weird stuff which
            // interacts quite badly with the RTE thing, so bypass it
            this.$el.toggleClass('open');
        }.bind(this), false);
        return false;
    },
});

instance.website.RTE = instance.web.Widget.extend({
    tagName: 'li',
    className: 'oe_right oe_rte_toolbar',
    commands: [
        [Command, "\uf032", 'bold'],
        [Command, "\uf033", 'italic'],
        [Command, "\uf0cd", 'underline'],
        [Command, "\uf0cc", 'strike'],
        [Command, "\uf12b", 'superscript'],
        [Command, "\uf12c", 'subscript'],
        [Group, "\uf0ca", [
            [Command, "\uf0ca", 'bulletedlist'],
            [Command, "\uf0cb", 'numberedlist']
        ]],
        [Group, _lt("Heading"), [
            [Style, _lt('H1'), { element: 'h1' }],
            [Style, _lt('H2'), { element: 'h2', }],
            [Style, _lt('H3'), { element: 'h3', }],
            [Style, _lt('H4'), { element: 'h4', }],
            [Style, _lt('H5'), { element: 'h5', }],
            [Style, _lt('H6'), { element: 'h6', }]
        ]]
    ],
    // editor.ui.items -> possible commands &al
    // editor.applyStyle(new CKEDITOR.style({element: "span",styles: {color: "#(color)"},overrides: [{element: "font",attributes: {color: null}}]}, {color: '#ff0000'}));
    start: function () {
        this.$el.hide();

        return $.when.apply(
            null, _(this.commands).map(this.proxy('start_command')));
    },
    init_command: function (command) {
        var type = command[0], args = command.slice(1);
        args.unshift(this);
        var F = function (args) {
            return type.apply(this, args);
        };
        F.prototype = type.prototype;

        return new F(args);
    },
    start_command: function (command) {
        return this.init_command(command).appendTo(this.$el);
    },
    start_edition: function ($elements) {
        var self = this;
        CKEDITOR.on('currentInstance', this.proxy('_change_focused_editor'));
        $elements
            .not('span, [data-oe-type]')
            .each(function () {
                var $this = $(this);
                CKEDITOR.inline(this, self._config()).on('change', function () {
                    $this.addClass('oe_dirty');
                    self.trigger('change', this, null);
                });
            });
    },

    /**
     * @param {Function} fn
     * @param {Boolean} [snapshot=true]
     * @returns {$.Deferred}
     */
    with_editor: function (fn, snapshot) {
        var editor = this._current_editor();
        if (snapshot !== false) { editor.fire('saveSnapshot'); }
        return $.when(fn(editor)).then(function () {
            if (snapshot !== false) { editor.fire('saveSnapshot'); }
            editor.focus();
        });
    },

    _current_editor: function () {
        return CKEDITOR.currentInstance;
    },
    _change_focused_editor: function () {
        this.$el.toggle(!!CKEDITOR.currentInstance);
    },
    _config: function () {
        return {
            // Don't load ckeditor's style rules
            stylesSet: [],
            // Remove toolbar entirely
            removePlugins: 'toolbar,elementspath,resize',
            uiColor: '',
            // Ensure no config file is loaded
            customConfig: '',
            // Disable ACF
            allowedContent: true,
        };
    },
});

$(function(){

    function make_static(){
        $('.oe_snippet_demo').removeClass('oe_new');
        $('.oe_page *').off('mouseover mouseleave');
        $('.oe_page .oe_selected').removeClass('oe_selected');
    }

    var selected_snippet = null;
    function snippet_click(event){
        if(selected_snippet){
            selected_snippet.removeClass('oe_selected');
            if(selected_snippet[0] === $(this)[0]){
                selected_snippet = null;
                event.preventDefault();
                make_static();
                return;
            }
        }
        $(this).addClass('oe_selected');
        selected_snippet = $(this);
        make_editable();
        event.preventDefault();
    }
    //$('.oe_snippet').click(snippet_click);

    var hover_element = null;

    function make_editable( constraint_after, constraint_inside ){
        if(selected_snippet && selected_snippet.hasClass('oe_new')){
            $('.oe_snippet_demo').addClass('oe_new');
        }else{
            $('.oe_snippet_demo').removeClass('oe_new');
        }
    
        $('.oe_page *').off('mouseover');
        $('.oe_page *').off('mouseleave');
        $('.oe_page *').mouseover(function(event){
            console.log('hover:',this);
            if(hover_element){
                hover_element.removeClass('oe_selected');
                hover_element.off('click');
            }
            $(this).addClass('oe_selected');
            $(this).click(append_snippet);
            hover_element = $(this);
            event.stopPropagation();
        });
        $('.oe_page *').mouseleave(function(){
            if(hover_element && $(this) === hover_element){
                hover_element = null;
                $(this).removeClass('oe_selected');
            }
        });
    }

        

    function append_snippet(event){
        console.log('click',this,event.button);
        if(event.button === 0){
            if(selected_snippet){
                if(selected_snippet.hasClass('oe_new')){
                    var new_snippet = $("<div class='oe_snippet'></div>");
                    new_snippet.append($(this).clone());
                    new_snippet.click(snippet_click);
                    $('.oe_snippet.oe_selected').before(new_snippet);
                }else{
                    $(this).after($('.oe_snippet.oe_selected').contents().clone());
                }
                selected_snippet.removeClass('oe_selected');
                selected_snippet = null;
                make_static();
            }
        }else if(event.button === 1){
            $(this).remove();
        }
        event.preventDefault();
    }

});


/**
 * Client action to go back in global history.
 * If can't go back in history stack, will go back to home.
 */
instance.web.ActionGoBack = function(parent, action) {
    window.location.href = document.referrer;
};
instance.web.client_actions.add("goback", "instance.web.ActionGoBack");

};
