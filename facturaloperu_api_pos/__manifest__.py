{
    'name': "FacturaloPeru API POS",
    'category': "web",
    'version': "11.0.1.0.0",
    "author": "FacturaloPeru",
    'website': "www.facturaloperu.com",
    'summary': "Módulo que se integra con POS",

    'depends': [
        'base',
        'point_of_sale',
        'odoope_ruc_validation'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/api_url.xml',
        'data/pos_order_document_type.xml',
        'views/assets.xml',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'views/pos_order_sync_view.xml',
        'views/pos_order_document_type_view.xml',
        'views/pos_order_serial_number_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': False,
    'installable': True,
    'web_preload': True,
}
