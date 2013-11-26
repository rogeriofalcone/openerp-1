(function () {
    'use strict';

    var website = openerp.website;

    website.EditorBar.include({
        start: function () {
            this.registerTour(new website.BannerTour(this));
            return this._super();
        },
    });

    website.BannerTour = website.Tour.extend({
        id: 'banner-tutorial',
        name: "Insert a banner",
        startPath: '/page/website.homepage',
        init: function (editor) {
            var self = this;
            self.steps = [
                {
                    stepId: 'welcome',
                    orphan: true,
                    backdrop: true,
                    title: "Welcome to your website!",
                    content: "This tutorial will guide you to build your home page. We will start by adding a banner.",
                    template: self.popover({ next: "Start Tutorial", end: "Skip It" }),
                },
                {
                    stepId: 'edit-page',
                    element: 'button[data-action=edit]',
                    placement: 'bottom',
                    title: "Edit this page",
                    content: "Every page of your website can be modified through the <i>Edit</i> button.",
                    triggers: function () {
                        editor.on('tour:editor_bar_loaded', self, self.moveToNextStep);
                    },
                },
                {
                    stepId: 'add-block',
                    element: 'button[data-action=snippet]',
                    placement: 'bottom',
                    title: "Insert building blocks",
                    content: "To add content in a page, you can insert building blocks.",
                    triggers: function () {
                        $('button[data-action=snippet]').one('click', function () {
                            self.moveToNextStep();
                        });
                    }
                },
                {
                    stepId: 'drag-banner',
                    element: '#website-top-navbar [data-snippet-id=carousel].ui-draggable',
                    placement: 'bottom',
                    title: "Drag & Drop a Banner",
                    content: "Drag the Banner block and drop it in your page.",
                    triggers: function () {
                        self.onSnippetDraggedAdvance('carousel');
                    },
                },
                {
                    stepId: 'edit-title',
                    element: '#wrap [data-snippet-id=carousel]:first .carousel-caption',
                    placement: 'top',
                    title: "Customize banner's text",
                    content: "Click in the text and start editing it. Click continue once it's done.",
                    template: self.popover({ next: "Continue" }),
                    triggers: function () {
                        var $banner = $("#wrap [data-snippet-id=carousel]:first");
                        if ($banner.length) {
                            $banner.click();
                        }
                    },
                },
                {
                    stepId: 'customize-banner',
                    element: '.oe_overlay_options .oe_options',
                    placement: 'left',
                    title: "Customize the banner",
                    content: "You can customize characteristic of any blocks through the Customize menu. For instance, change the background of the banner.",
                    template: self.popover({ next: "Continue" }),
                },
                {
                    stepId: 'add-three-cols',
                    element: 'button[data-action=snippet]',
                    placement: 'bottom',
                    title: "Add Another Block",
                    content: "Let's add another building block to your page.",
                    triggers: function () {
                        $('button[data-action=snippet]').one('click', function () {
                            self.moveToNextStep();
                        });
                    }
                },
                {
                    stepId: 'drag-three-columns',
                    element: '#website-top-navbar [data-snippet-id=three-columns].ui-draggable',
                    placement: 'bottom',
                    title: "Drag & Drop a Block",
                    content: "Drag the <em>'3 Columns'</em> block and drop it below the banner.",
                    triggers: function () {
                        self.onSnippetDraggedAdvance('three-columns');
                    },
                },
                {
                    stepId: 'activate-text-block-title',
                    element: '#wrap [data-snippet-id=three-columns] .text-center[data-snippet-id=colmd]',
                    placement: 'top',
                    title: "Edit an Area",
                    content: "Select any area of the page to modify it. Click on this subtitle.",
                    triggers: function () {
                        $('#wrap [data-snippet-id=three-columns] .text-center[data-snippet-id=colmd]').one('click', function () {
                            self.moveToNextStep();
                        });
                    },
                },
                {
                    stepId: 'remove-text-block-title',
                    element: '.oe_snippet_remove:last',
                    placement: 'top',
                    reflex: true,
                    title: "Delete the Title",
                    content: "From this toolbar you can move, duplicate or delete the selected zone. Click on the cross to delete the title.",
                },
                {
                    stepId: 'save-changes',
                    element: 'button[data-action=save]',
                    placement: 'right',
                    reflex: true,
                    title: "Save your modifications",
                    content: "Publish your page by clicking on the <em>'Save'</em> button.",
                },
                {
                    stepId: 'part-2',
                    orphan: true,
                    title: "Congratulation!",
                    content: "Your homepage has been updated.",
                    template: self.popover({ next: "Continue" }),
                },
                {
                    stepId: 'show-mobile',
                    element: 'a[data-action=show-mobile-preview]',
                    placement: 'bottom',
                    title: "Test Your Mobile Version",
                    content: "Let's check how your homepage looks like on mobile devices.",
                    triggers: function () {
                        $(document).one('shown.bs.modal', function () {
                            self.moveToNextStep();
                        });
                    }
                },
                {
                    stepId: 'show-mobile-close',
                    element: 'button[data-dismiss=modal]',
                    placement: 'right',
                    reflex: true,
                    title: "Close Mobile Preview",
                    content: "Scroll in the mobile preview to test the rendering. Once it's ok, close this dialog.",
                },
                {
                    stepId: 'show-tutorials',
                    element: '#help-menu-button',
                    placement: 'left',
                    reflex: true,
                    title: "More Tutorials",
                    content: "Get more tutorials through this <em>'Help'</em> menu or click on the left <em>'Edit'</em> button to continue modifying this page.",
                    template: self.popover({ end: "Close Tutorial" }),
                }
            ];
            return this._super();
        },
        resume: function () {
            return this.isCurrentStep('part-2') && this._super();
        },
    });

}());
