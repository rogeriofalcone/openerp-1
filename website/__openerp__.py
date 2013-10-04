{
    'name': 'Website Builder',
    'category': 'Website',
    'summary': 'Build Your Enterprise Website',
    'version': '1.0',
    'description': """
OpenERP Website CMS
===================

        """,
    'author': 'OpenERP SA',
    'depends': ['web', 'share'],
    'installable': True,
    'data': [
        'views/views.xml',
        'views/snippets.xml',
        'views/themes.xml',
        'website_data.xml',
        'website_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'website_demo.xml',
    ]
}
