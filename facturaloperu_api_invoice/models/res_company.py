# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    api_url = fields.Char('URL', help="https://odoo.facturaloperuonline.com/api/documents", default="https://odoo.facturaloonline.com/api/documents")
    api_token = fields.Char('API Token', help="Bh6B6eFFeNbKAGtSd1hZwcrbQ244j1cfEyG5IC45WPMkyHnkqe", default="Bh6B6eFFeNbKAGtSd1hZwcrbQ244j1cfEyG5IC45WPMkyHnkqe")