(function () {
    'use strict';
    var website = openerp.website;

    website.snippet.BuildingBlock.include({
        _get_snippet_url: function () {
            return '/website_mail/snippets';
        }
    });

    // Copy the template to the body of the email
    $(document).ready(function () {
        $('.js_template_set').click(function(ev) {
            $('#email_designer').show();
            $('#email_template').hide();
            $(".js_content", $(this).parent()).children().clone().appendTo('#email_body');

            openerp.website.editor_bar.edit();
            event.preventDefault();
        });
    });

})();
