# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FeapiSerie(models.Model):
    _name = 'feapi.serie'

    name = fields.Char('Serie', size=4, required=True)
    description = fields.Char('Descripcion')

    invoice_id = fields.One2many("account.invoice", "serie_id")

    document_type_id = fields.Many2one("einvoice.catalog.01", string="Tipo de Documento")

class FeapiDocumentType(models.Model):
    _inherit = 'einvoice.catalog.01'

    serie_id = fields.One2many("feapi.serie", "document_type_id")