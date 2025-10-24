{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Author Name",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/real_estate_views.xml',
        'views/sales_person_views.xml',
        'views/buyers_views.xml',
        'views/offers_views.xml',


    ],
    # data files containing optionally loaded demonstration data
    'demo': [

    ],
}