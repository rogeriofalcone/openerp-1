(function () {
    'use strict';

    var website = openerp.website;
    website.templates.push('/website/static/src/xml/website.seo.xml');

    website.EditorBar.include({
        events: _.extend({}, website.EditorBar.prototype.events, {
            'click a[data-action=promote-current-page]': 'launchSeo',
        }),
        launchSeo: function () {
            (new website.seo.Configurator()).appendTo($(document.body));
        },
    });

    website.seo = {};

    function analyzeKeyword(htmlPage, keyword) {
        return  htmlPage.isInTitle(keyword) ? {
                    title: 'keyword-in-title',
                    description: "This keyword is used in the page title",
                } : htmlPage.isInDescription(keyword) ? {
                    title: 'keyword-in-description',
                    description: "This keyword is used in the page description",
                } : htmlPage.isInBody(keyword) ? {
                    title: 'keyword-in-body',
                    description: "This keyword is used in the page content."
                } : { title: "", description: "" };
    }

    website.seo.Suggestion = openerp.Widget.extend({
        template: 'website.seo_suggestion',
        events: {
            'click .js_seo_suggestion': 'select',
        },
        init: function (parent, options) {
            this.root = options.root;
            this.keyword = options.keyword;
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            this.htmlPage.on('title-changed', this, this.renderElement);
            this.htmlPage.on('description-changed', this, this.renderElement);
        },
        analyze: function () {
            return analyzeKeyword(this.htmlPage, this.keyword);
        },
        highlight: function () {
            return this.analyze().title;
        },
        tooltip: function () {
            return this.analyze().description;
        },
        select: function () {
            this.trigger('selected', this.keyword);
        },
    });

    website.seo.SuggestionList = openerp.Widget.extend({
        template: 'website.seo_list',
        init: function (parent, options) {
            this.root = options.root;
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            this.refresh();
        },
        refresh: function () {
            var self = this;
            self.$el.append("Loading...");
            function addSuggestions (list) {
                self.$el.empty();
                // TODO Improve algorithm + Ajust based on custom user keywords
                var regex = new RegExp(self.root, "gi");
                var cleanList = _.map(list, function (word) {
                    return word.replace(regex, "").trim();
                });
                // TODO Order properly ?
                _.each(_.uniq(cleanList), function (keyword) {
                    if (keyword) {
                        var suggestion = new website.seo.Suggestion(self, {
                            root: self.root,
                            keyword: keyword,
                            page: self.htmlPage,
                        });
                        suggestion.on('selected', self, function (word) {
                            self.trigger('selected', word);
                        });
                        suggestion.appendTo(self.$el);
                    }
                });
            }
            $.getJSON("http://seo.eu01.aws.af.cm/suggest/"+encodeURIComponent(this.root + " "), addSuggestions);
        },
    });

    website.seo.Keyword = openerp.Widget.extend({
        template: 'website.seo_keyword',
        events: {
            'click a[data-action=remove-keyword]': 'destroy',
        },
        maxWordsPerKeyword: 4, // TODO Check
        init: function (parent, options) {
            this.keyword = options.word;
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            this.htmlPage.on('title-changed', this, this.updateLabel);
            this.htmlPage.on('description-changed', this, this.updateLabel);
            this.suggestionList = new website.seo.SuggestionList(this, {
                root: this.keyword,
                page: this.htmlPage,
            });
            this.suggestionList.on('selected', this, function (word) {
                this.trigger('selected', word);
            });
            this.suggestionList.appendTo(this.$('.js_seo_keyword_suggestion'));
        },
        analyze: function () {
            return analyzeKeyword(this.htmlPage, this.keyword);
        },
        highlight: function () {
            return this.analyze().title;
        },
        tooltip: function () {
            return this.analyze().description;
        },
        updateLabel: function () {
            var cssClass = "oe_seo_keyword js_seo_keyword " + this.highlight();
            this.$(".js_seo_keyword").attr('class', cssClass);
            this.$(".js_seo_keyword").attr('title', this.tooltip());
        },
        destroy: function () {
            this.trigger('removed');
            this._super();
        },
    });

    website.seo.KeywordList = openerp.Widget.extend({
        template: 'website.seo_list',
        maxKeywords: 10,
        init: function (parent, options) {
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            var self = this;
            var existingKeywords = self.htmlPage.keywords();
            if (existingKeywords.length > 0) {
                _.each(existingKeywords, function (word) {
                    self.add.call(self, word);
                });
            } else {
                var companyName = self.htmlPage.company().toLowerCase();
                self.add(companyName);
            }
        },
        keywords: function () {
            var result = [];
            this.$('.js_seo_keyword').each(function () {
                result.push($(this).data('keyword'));
            });
            return result;
        },
        isFull: function () {
            return this.keywords().length >= this.maxKeywords;
        },
        exists: function (word) {
            return _.contains(this.keywords(), word);
        },
        add: function (candidate) {
            var self = this;
            // TODO Refine
            var word = candidate ? candidate.replace(/[,;.:<>]+/g, " ").replace(/ +/g, " ").trim().toLowerCase() : "";
            if (word && !self.isFull() && !self.exists(word)) {
                var keyword = new website.seo.Keyword(self, {
                    word: word,
                    page: this.htmlPage,
                });
                keyword.on('removed', self, function () {
                   self.trigger('list-not-full');
                   self.trigger('removed', word);
                });
                keyword.on('selected', self, function (word) {
                    self.trigger('selected', word);
                });
                keyword.appendTo(self.$el);
            }
            if (self.isFull()) {
                self.trigger('list-full');
            }
        },
    });

    website.seo.Image = openerp.Widget.extend({
        template: 'website.seo_image',
        init: function (parent, options) {
            this.src = options.src;
            this.alt = options.alt;
            this._super(parent);
        },
    });


    website.seo.ImageList = openerp.Widget.extend({
        init: function (parent, options) {
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            var self = this;
            this.htmlPage.images().each(function (index, image) {
                new website.seo.Image(self, image).appendTo(self.$el);
            });
        },
        images: function () {
            var result = [];
            this.$('input').each(function () {
               var $input = $(this);
               result.push({
                   src: $input.attr('src'),
                   alt: $input.val(),
               });
            });
            return result;
        },
        add: function (image) {
            new website.seo.Image(this, image).appendTo(this.$el);
        },
    });

    website.seo.HtmlPage = openerp.Class.extend(openerp.PropertiesMixin, {
        url: function () {
            var url = window.location.href;
            var hashIndex = url.indexOf('#');
            return hashIndex >= 0 ? url.substring(0, hashIndex) : url;
        },
        title: function () {
            return $('title').text().trim();
        },
        changeTitle: function (title) {
            $('title').text(title);
            this.trigger('title-changed', title);
        },
        description: function () {
            return $('meta[name=description]').attr('value').trim();
        },
        changeDescription: function (description) {
            $('meta[name=description]').attr('value', description);
            this.trigger('description-changed', description);
        },
        keywords: function () {
            var parsed = $('meta[name=keywords]').attr('value').split(",");
            return parsed[0] ? parsed: [];
        },
        changeKeywords: function (keywords) {
            $('meta[name=keywords]').attr('value', keywords.join(","));
            this.trigger('keywords-changed', keywords);
        },
        headers: function (tag) {
            return $('#wrap '+tag).map(function () {
                return $(this).text();
            });
        },
        images: function () {
            return $('#wrap img').map(function () {
                var $img = $(this);
                return  {
                    src: $img.attr('src'),
                    alt: $img.attr('alt'),
                };
            });
        },
        company: function () {
            return $('meta[name="openerp.company"]').attr('value');
        },
        bodyText: function () {
            return $('body').children().not('.js_seo_configuration').text();
        },
        isInBody: function (text) {
            return new RegExp(text, "gi").test(this.bodyText());
        },
        isInTitle: function (text) {
            return new RegExp(text, "gi").test(this.title());
        },
        isInDescription: function (text) {
            return new RegExp(text, "gi").test(this.description());
        },
    });

    website.seo.Tip = openerp.Widget.extend({
        template: 'website.seo_tip',
        events: {
            'closed.bs.alert': 'destroy',
        },
        init: function (parent, options) {
            this.message = options.message;
            // cf. http://getbootstrap.com/components/#alerts
            // success, info, warning or danger
            this.type = options.type || 'info';
            this._super(parent);
        },
    });

    website.seo.Configurator = openerp.Widget.extend({
        template: 'website.seo_configuration',
        events: {
            'keyup input[name=seo_page_keywords]': 'confirmKeyword',
            'keyup input[name=seo_page_title]': 'titleChanged',
            'keyup textarea[name=seo_page_description]': 'descriptionChanged',
            'click button[data-action=add]': 'addKeyword',
            'click button[data-action=update]': 'update',
            'hidden.bs.modal': 'destroy',
        },
        maxTitleSize: 65,
        maxDescriptionSize: 155,
        start: function () {
            var self = this;
            var $modal = self.$el;
            var htmlPage = this.htmlPage = new website.seo.HtmlPage();
            $modal.find('.js_seo_page_url').text(htmlPage.url());
            $modal.find('input[name=seo_page_title]').val(htmlPage.title());
            $modal.find('textarea[name=seo_page_description]').val(htmlPage.description());
            self.suggestImprovements();
            self.imageList = new website.seo.ImageList(self, { page: htmlPage });
            if (htmlPage.images().length === 0) {
                $modal.find('.js_image_section').remove()
            } else {
                self.imageList.appendTo($modal.find('.js_seo_image_list'));
            }
            self.keywordList = new website.seo.KeywordList(self, { page: htmlPage });
            self.keywordList.on('list-full', self, function () {
                $modal.find('input[name=seo_page_keywords]')
                    .attr('readonly', "readonly")
                    .attr('placeholder', "Remove a keyword first");
                $modal.find('button[data-action=add]')
                    .prop('disabled', true).addClass('disabled');
            });
            self.keywordList.on('list-not-full', self, function () {
                $modal.find('input[name=seo_page_keywords]')
                    .removeAttr('readonly').attr('placeholder', "");
                $modal.find('button[data-action=add]')
                    .prop('disabled', false).removeClass('disabled');
            });
            self.keywordList.on('selected', self, function (word) {
                self.keywordList.add(word);
            });
            self.keywordList.appendTo($modal.find('.js_seo_keywords_list'));
            $modal.modal();
        },
        suggestImprovements: function () {
            var tips = [];
            var self = this;
            function displayTip(message, type) {
                new website.seo.Tip(self, {
                   message: message,
                   type: type,
                }).appendTo(self.$('.js_seo_tips'));
            }
            var htmlPage = this.htmlPage;
            if (htmlPage.headers('h1').length === 0) {
                tips.push({
                    type: 'warning',
                    message: "This page seems to be missing an &lt;h1&gt; tag.",
                });
            }
            if (htmlPage.headers('h1').length > 1) {
                tips.push({
                    type: 'warning',
                    message: "The page contains more than one &lt;h1&gt; tag.",
                });
            }
            if (tips.length > 0) {
                _.each(tips, function (tip) {
                    displayTip(tip.message, tip.type);
                });
            } else {
                displayTip("The markup on this page is appropriate for search engines.", 'success');
            }
        },
        confirmKeyword: function (e) {
            if (e.keyCode == 13) {
                this.addKeyword();
            }
        },
        addKeyword: function (word) {
            var $input = this.$('input[name=seo_page_keywords]');
            var keyword = _.isString(word) ? word : $input.val();
            this.keywordList.add(keyword);
            $input.val("");
        },
        update: function () {
            var data = {
                title: this.htmlPage.title(),
                description: this.htmlPage.description(),
                keywords: this.keywordList.keywords(),
                images: this.imageList.images(),
            };
            console.log(data);
            // TODO Persist changes
            this.$el.modal('hide');
        },
        titleChanged: function () {
            var self = this;
            setTimeout(function () {
                var title = self.$('input[name=seo_page_title]').val();
                self.htmlPage.changeTitle(title);
            }, 0);
        },
        descriptionChanged: function () {
            var self = this;
            setTimeout(function () {
                var description = self.$('textarea[name=seo_page_description]').attr('value');
                self.htmlPage.changeDescription(description);
            }, 1);
        },
        destroy: function () {
            this.htmlPage.changeKeywords(this.keywordList.keywords());
            this._super();
        },
    });
})();
