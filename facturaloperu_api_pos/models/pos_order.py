from odoo import (
    api,
    models,
    fields
)


class PosFacturaloApi(models.Model):
    _inherit = 'pos.order'

    api_external_id = fields.Char(
        string='External Id',
        readonly=True
    )
    api_number_feapi = fields.Char(
        string='Número',
        readonly=True
    )
    api_link_cdr = fields.Char(
        string='CDR',
        readonly=True
    )
    api_link_pdf = fields.Char(
        string='PDF',
        readonly=True
    )
    api_link_xml = fields.Char(
        string='XML',
        readonly=True
    )
    api_code_json = fields.Text(
        string='JSON',
        readonly=True
    )
