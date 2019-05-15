from odoo import (
    api,
    models,
    fields
)


class PosOrderDocumentType(models.Model):
    _name = "pos.order.document.type"
    _description = "Tipo de Documento"

    name = fields.Char(
        string='Tipo de documento'
    )
    number = fields.Char(
        string='Número de tipo de documento'
    )


class PosOrderSerialNumber(models.Model):
    _name = "pos.order.serial.number"
    _description = "Número de Serie de Factura"

    name = fields.Char(
        string='Tipo de Documento'
    )
    document_type_id = fields.Many2one(
        'pos.order.document.type',
        string="Tipo de documento"
    )
    document_type_name = fields.Char(
        related="document_type_id.name"
    )
    document_type_number = fields.Char(
        related="document_type_id.number"
    )
