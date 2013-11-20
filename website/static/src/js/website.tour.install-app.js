(function () {
    'use strict';

    var website = openerp.website;

    var render = website.tour.render;

    website.EditorBar.include({
        start: function () {
            this.registerTour(new website.InstallAppTour(this));
            return this._super();
        },
    });

    website.InstallAppTour = website.Tour.extend({
        id: 'install-app',
        name: "Install a new App",
        init: function (editor) {
            var self = this;
            self.steps = [
                {
                    stepId: 'welcome-install-app',
                    orphan: true,
                    backdrop: true,
                    title: "Install an App",
                    content: "You can intall some apps to manage your website content.",
                    template: render('website.tour_popover', { next: "Start Tutorial", end: "Skip It" }),
                },
                {
                    stepId: 'customize',
                    element: '#customize-menu-button',
                    placement: 'left',
                    title: "Install an app",
                    content: "Add new apps by customizing your website.",
                    template: render('website.tour_popover'),
                    onShow: function () {
                        editor.on('rte:customize_menu_ready', editor, function () {
                            self.movetoStep('install-app');
                        });
                    },
                },
                {
                    stepId: 'install-app',
                    element: '#customize-menu li:last a',
                    placement: 'left',
                    orphan: true,
                    title: "Install an app",
                    content: "Click 'Install Apps' to select and install the application you would like to manage from your website.",
                    template: render('website.tour_popover'),
                },
            ];
            return this._super();
        },
    });

}());
