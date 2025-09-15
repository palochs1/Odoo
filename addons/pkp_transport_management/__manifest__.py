{
    'name': 'Pikulthong Plastic - Transport Management Extension',
    'version': '1.0',
    'category': 'Inventory',
    'license': 'OPL-1',
    'author': '',
    'company': '',
    'website': '',
    'summary': 'Transport Management Extension',
    'description': """
Description
-----------
Extends the functionality of Transport Management

Changelog
---------

**Version 1.0**
    - Initial

    """,
    'depends' : ['account', 'sale', 'stock', 'stock_account', 'fleet'],
    'data': [
        'security/transport_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_transport.xml',
        'data/paper_format.xml',
        'views/menuitem.xml',

        'wizard/allowance_delivery_wizard.xml',
        # 'wizard/allowance_person_wizard.xml',

        'views/delivery_place_view.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',


        'views/extra_cost_view.xml',
        'views/transport_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/stock_picking_view.xml',

        'report/allowance_delivery_report.xml',
        'report/allowance_person_report.xml',
        'report/transport_report.xml',

        'views/transport_remark_views.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
