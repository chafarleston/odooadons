from odoo import (
    api,
    models,
    fields
)


class PosOrderSync(models.Model):
    _name = 'pos.order.sync'
    _rec_name = 'pos_reference'

    state = fields.Selection([
        ('not_synced', 'No sincronizado'),
        ('synced', 'Sincronizado')],
        default='not_synced',
        readonly=True
    )
    pos_reference = fields.Char(
        string='Número de pedido',
    )
    session_id = fields.Many2one(
        'pos.session',
    )
    api_external_id = fields.Char(
        string='External Id',
    )
    api_number_feapi = fields.Char(
        string='Número',
    )
    api_link_cdr = fields.Char(
        string='CDR',
    )
    api_link_pdf = fields.Char(
        string='PDF',
    )
    api_link_xml = fields.Char(
        string='XML',
    )

    @api.multi
    def sync_pos_orders(self):
        for order in self:
            PosOrder = self.env['pos.order'].sudo()
            if order.pos_reference and order.session_id and \
               order.state == 'not_synced':
                order_to_sync = PosOrder.search([
                    ('pos_reference', '=', order.pos_reference),
                    ('session_id', '=', order.session_id.id)
                ])
                if order_to_sync:
                    order_to_sync[0].write({
                        'api_external_id': order.api_external_id,
                        'api_number_feapi': order.api_number_feapi,
                        'api_link_cdr': order.api_link_cdr,
                        'api_link_xml': order.api_link_xml,
                        'api_link_pdf': order.api_link_pdf,
                    })
                    order.state = 'synced'
