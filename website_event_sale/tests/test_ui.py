import openerp.addons.website.tests.test_ui as test_ui

def load_tests(loader, base, _):
    base.addTest(test_ui.WebsiteUiSuite(test_ui.full_path(__file__,'website_event_sale_test.js'),
        {'redirect': '/page/website.homepage'}))
    base.addTest(test_ui.WebsiteUiSuite(test_ui.full_path(__file__,'website_event_sale_test.js'),
        {'redirect': '/page/website.homepage', 'user': 'demo', 'password': 'demo'}))
    base.addTest(test_ui.WebsiteUiSuite(test_ui.full_path(__file__,'website_event_sale_test.js'),
        {'path': '/', 'user': None}))
    return base