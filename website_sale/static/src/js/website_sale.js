$(document).ready(function () {
    var $shippingDifferent = $(".oe_website_sale input[name='shipping_different']");
    if ($shippingDifferent.is(':checked')) {
       $(".oe_website_sale .js_shipping").show();
    }
    $shippingDifferent.change(function () {
        $(".oe_website_sale .js_shipping").toggle();
    });

    // change for css
    $(document).on('mouseup', '.js_publish', function (ev) {
        $(ev.currentTarget).parents(".thumbnail").toggleClass("disabled");
    });

    function set_my_cart_quantity(qty) {
        var $q = $(".my_cart_quantity");
        $q.parent().parent().removeClass("hidden", !qty);
        $q.html(qty)
            .hide()
            .fadeIn(600);
    }

    $(".oe_website_sale .oe_cart input.js_quantity").change(function () {
        var $input = $(this);
        var value = parseInt($input.val(), 10);
        if (isNaN(value)) value = 0;
        openerp.jsonRpc("/shop/set_cart_json/", 'call', {'order_line_id': $input.data('id'), 'set_number': value})
            .then(function (data) {
                set_my_cart_quantity(data[1]);
                $input.val(data[0]);
                if (!data[0]) {
                    location.reload();
                }
            });
    });

    // hack to add and rome from cart with json
    $('.oe_website_sale a.js_add_cart_json').on('click', function (ev) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var href = $link.attr("href");

        var add_cart = href.match(/add_cart\/([0-9]+)/);
        var product_id = add_cart && +add_cart[1] || false;

        var change_cart = href.match(/change_cart\/([0-9]+)/);
        var order_line_id = change_cart && +change_cart[1] || false;
        openerp.jsonRpc("/shop/add_cart_json/", 'call', {
                'product_id': product_id,
                'order_line_id': order_line_id,
                'remove': $link.is('[href*="remove"]')})
            .then(function (data) {
                if (!data[0]) {
                    location.reload();
                }
                set_my_cart_quantity(data[1]);
                $link.parents(".input-group:first").find(".js_quantity").val(data[0]);
                $('#cart_total').replaceWith(data[3]);
            });
        return false;
    });

    // change price when they are variants
    $('form.js_add_cart_json label').on('mouseup', function (ev) {
        ev.preventDefault();
        var $label = $(ev.currentTarget);
        var $price = $label.parent("form").find(".oe_price .oe_currency_value");
        if (!$price.data("price")) {
            $price.data("price", parseFloat($price.text()));
        }
        $price.html($price.data("price")+parseFloat($label.find(".badge span").text() || 0));
    });

    // attributes

    var js_slider_time = null;
    var $form = $("form.attributes");
    $form.on("change", "label input", function () {
        $form.submit();
    });
});
