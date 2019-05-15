from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    doc_number = fields.Char(
        string='Document Number',
    )

    @api.model
    def create(self, vals):
        doc_number = vals.get('doc_number', False)
        vat = vals.get('vat', False)
        if doc_number:
            vals.update({'vat': doc_number})
        if vat:
            vals.update({'doc_number': vat})
        res_id = super(ResPartner, self).create(vals)
        return res_id

    @api.multi
    def write(self, vals):
        doc_number = vals.get('doc_number', False)
        vat = vals.get('vat', False)
        if doc_number:
            vals.update({'vat': doc_number})

        if vat:
            vals.update({'doc_number': vat})
        res_id = super(ResPartner, self).write(vals)
        return res_id

class einvoice_catalog_06(models.Model):
    _inherit = "einvoice.catalog.06"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for table in self:
            l_name =  table.name
            result.append((table.id, l_name ))
        return result