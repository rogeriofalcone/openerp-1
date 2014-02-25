(function () {
    'use strict';

    var website = openerp.website;
    var _t = openerp._t;

    website.EditorBar.include({
        start: function () {
            this.registerTour(new website.EventTour(this));
            return this._super();
        },
    });

    website.EventTour = website.Tour.extend({
        id: 'event',
        name: "Create an event",
        testPath: '/event(/[0-9]+/register)?',
        init: function (editor) {
            var self = this;
            self.steps = [
                {
                    title:     _t("Create an Event"),
                    content:   _t("Let's go through the first steps to publish a new event."),
                    popover:   { next: _("Start Tutorial"), end: _("Skip It") },
                },
                {
                    element:   '#content-menu-button',
                    placement: 'left',
                    title:     _t("Add Content"),
                    content:   _t("The <em>Content</em> menu allows you to create new pages, events, menus, etc."),
                    popover:   { fixed: true },
                },
                {
                    element:   'a[data-action=new_event]',
                    placement: 'left',
                    title:     _t("New Event"),
                    content:   _t("Click here to create a new event."),
                    popover:   { fixed: true },
                },
                {
                    element:   '.modal #editor_new_event input[type=text]',
                    sampleText: 'Advanced Technical Training',
                    placement: 'right',
                    title:     _t("Create an Event Name"),
                    content:   _t("Create a name for your new event and click <em>'Continue'</em>. e.g: Technical Training"),
                },
                {
                    waitNot:   '.modal input[type=text]:not([value!=""])',
                    element:   '.modal button.btn-primary',
                    placement: 'right',
                    title:     _t("Create Event"),
                    content:   _t("Click <em>Continue</em> to create the event."),
                },
                {
                    waitFor:   'body:has(button[data-action=save]:visible):has(.js_event)',
                    title:     _t("New Event Created"),
                    content:   _t("This is your new event page. We will edit the event presentation page."),
                    popover:   { next: _t("Continue") },
                },
                {
                    element:   'button[data-action=snippet]',
                    placement: 'bottom',
                    title:     _t("Layout your event"),
                    content:   _t("Insert blocks to layout the body of your event."),
                    popover:   { fixed: true },
                },
                {
                    snippet:   'image-text',
                    placement: 'bottom',
                    title:     _t("Drag & Drop a block"),
                    content:   _t("Drag the 'Image-Text' block and drop it in your page."),
                    popover:   { fixed: true },
                },
                {
                    
                    element:   'button[data-action=snippet]',
                    placement: 'bottom',
                    title:     _t("Layout your event"),
                    content:   _t("Insert another block to your event."),
                    popover:   { fixed: true },
                },
                {
                    snippet:   'text-block',
                    placement: 'bottom',
                    title:     _t("Drag & Drop a block"),
                    content:   _t("Drag the 'Text Block' in your event page."),
                    popover:   { fixed: true },
                },
                {
                    element:   'button[data-action=save]',
                    placement: 'right',
                    title:     _t("Save your modifications"),
                    content:   _t("Once you click on save, your event is updated."),
                    popover:   { fixed: true },
                },
                {
                    waitFor:   'button[data-action=edit]:visible',
                    element:   'button.btn-danger.js_publish_btn',
                    placement: 'top',
                    title:     _t("Publish your event"),
                    content:   _t("Click to publish your event."),
                },
                {
                    waitFor:   '.js_publish_management button.js_publish_btn.btn-success:visible',
                    element:   '.js_publish_management button[data-toggle="dropdown"]',
                    placement: 'left',
                    title:     _t("Customize your event"),
                    content:   _t("Click here to customize your event further."),
                },
                {
                    element:   '.js_publish_management ul>li>a:last:visible',
                },
            ];
            return this._super();
        }
    });

}());
