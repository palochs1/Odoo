{
    "name": "Website Delivery Orders",
    "version": "15.0.1.0.0",
    "summary": "Public website page to list Delivery Orders (stock.picking outgoing)",
    "author": "Tang",
    "license": "LGPL-3",
    "depends": ["website", "stock", "pkp_transport_management"],
    "data": [
        "views/delivery_orders_templates.xml",
        "views/liff_delivery_template.xml",
        "views/transpot_order_delivery.xml",
    ],
    "installable": True,
    "application": False,
}
