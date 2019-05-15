# -*- coding: utf-8 -*-
# encoding: latin1

from odoo import models, fields, api, exceptions
from odoo.tools import float_is_zero, float_compare, pycompat
from requests.exceptions import ConnectionError, HTTPError, Timeout
import requests
import json

class feapi(models.Model):
    _inherit = 'account.invoice'

    # campo para consultar estatus de documento
    external_id = fields.Char(string='External Id', readonly=True)
    number_feapi = fields.Char(string='Número', readonly=True)
    link_cdr = fields.Char(string='CDR', readonly=True)
    link_pdf = fields.Char(string='PDF', readonly=True)
    link_xml = fields.Char(string='XML', readonly=True)
    api_json = fields.Text(string='JSON', readonly=True)
    api_qr = fields.Char(string='QR', readonly=True)
    api_number_to_letter = fields.Char(string='number_to_letter', readonly=True)

    serie_id = fields.Many2one("feapi.serie", string="Número de Serie", required=True)


    # botones para mostrar el estado actual del documento
    state_api = fields.Selection([
            ('register','Registrado'),
            ('send', 'Enviado'),
            ('success', 'Aceptado'),
            ('observed', 'Observado'),
            ('reject', 'Rechazado'),
            ('null', 'Anulado'),
            ('nullable', 'Por anular'),
        ], string='Status API', index=True, readonly=True, default='register')

    # enviar json
    @api.multi
    def action_invoice_send_sunat(self,values):

        token = self.company_id.api_token
        url = self.company_id.api_url
        serie = self.serie_id.name + '-#'
        document_type = self.serie_id.document_type_id.code

        products = self.invoice_line_ids
        items = []

        for product in products:

            if product.invoice_line_tax_ids.amount != 0:
                amountIgv = (int(product.price_subtotal) * int(product.invoice_line_tax_ids.amount)) / 100
                affectIgv = 10
                percentIgv = int(product.invoice_line_tax_ids.amount)
            else:
                amountIgv = 0
                affectIgv = 20
                percentIgv = 18

            json_string = product.name.replace('\n', ' ')
            item = {
                        "codigo_interno_del_producto": "P0121",
                        "descripcion_detallada": json_string,
                        "codigo_producto_de_sunat": "51121703",
                        "unidad_de_medida": product.uom_id.name,
                        "cantidad_de_unidades": product.quantity,
                        "valor_unitario": product.price_unit,
                        "codigo_de_tipo_de_precio":"01",
                        "precio_de_venta_unitario_valor_referencial": product.price_unit,
                        "afectacion_al_igv": affectIgv,
                        "porcentaje_de_igv": percentIgv,
                        "monto_de_igv": float(amountIgv),
                        "valor_de_venta_por_item": product.price_subtotal,
                        "total_por_item": product.price_total
                    }
            items.append(item)

        # end items

        # create json
        data = {
                    "version_del_ubl": "v21",
                    "serie_y_numero_correlativo": serie,
                    "fecha_de_emision": self.date_invoice,
                    "hora_de_emision": "10:11:11",
                    "tipo_de_documento": document_type,
                    "tipo_de_moneda": self.company_currency_id.name,
                    "fecha_de_vencimiento": self.date_due,
                    "datos_del_emisor": {
                        "codigo_del_domicilio_fiscal": "0001"
                    },
                    "datos_del_cliente_o_receptor":{
                        "numero_de_documento": self.partner_id.vat,
                        "tipo_de_documento": self.partner_id.catalog_06_id.code,
                        "apellidos_y_nombres_o_razon_social": self.partner_id.name,
                        "direccion": self.partner_id.street,
                        "ubigeo": self.partner_id.zip
                    },
                    "totales": {
                        "total_operaciones_gravadas": self.amount_untaxed,
                        "sumatoria_igv": self.amount_tax,
                        "total_de_la_venta": self.amount_total
                    },
                    "items": items,
                    "informacion_adicional":{
                        "tipo_de_operacion": "0101",
                        "leyendas":[]
                    },
                    "extras":{
                        "forma_de_pago": "Efectivo"
                    }
                }

        # edito el api_json
        html_json = json.dumps(data,sort_keys=True, indent=4, separators=(',', ': '))
        self.write({'api_json':html_json})

        # return {
        #     'data': data,
        #     'url': url,
        #     'token': token
        # }

        apiToken = 'Bearer ' + token

        try:
            r = requests.post(url, data=html_json, headers={'Content-Type': 'application/json','Authorization': apiToken}, timeout=10)
            response = r.json()
        except (ConnectionError, HTTPError) as e:
            raise exceptions.Warning('Error Http')
            return
        except (ConnectionError, Timeout) as e:
            raise exceptions.Warning('El tiempo de envío se ha agotado, el servidor de la Sunat puede encontrarse no disponible temporalemente')
            return

        # edito el external_id
        self.write({'external_id':response['data']['external_id']})
        # edito el estado
        if response['data']['link_cdr']:
            self.write({'state_api': 'success'})
        else:
            self.write({'state_api': 'send'})
        # edito el numero
        self.write({'number_feapi':response['data']['number']})
        # edito el cdr
        self.write({'link_cdr':response['data']['link_cdr']})
        # edito el pdf
        self.write({'link_pdf':response['data']['link_pdf']})
        # edito el xml
        self.write({'link_xml':response['data']['link_xml']})
        # edito el qr
        self.write({'api_qr':response['data']['qr']})
        # edito el api_number_to_letter
        self.write({'api_number_to_letter':response['data']['number_to_letter']})


        return {
            "response": response,
        }

    # generar json
    @api.multi
    def action_invoice_json_generate(self,values):

        token = self.company_id.api_token
        url = self.company_id.api_url
        serie = self.serie_id.name + '-#'
        document_type = self.serie_id.document_type_id.code

        products = self.invoice_line_ids
        items = []

        for product in products:

            if product.invoice_line_tax_ids.amount != 0:
                amountIgv = (int(product.price_subtotal) * int(product.invoice_line_tax_ids.amount)) / 100
                affectIgv = 10
                percentIgv = int(product.invoice_line_tax_ids.amount)
            else:
                amountIgv = 0
                affectIgv = 20
                percentIgv = 18

            json_string = product.name.replace('\n', ' ')
            item = {
                        "codigo_interno_del_producto": "P0121",
                        "descripcion_detallada": json_string,
                        "codigo_producto_de_sunat": "51121703",
                        "unidad_de_medida": product.uom_id.name,
                        "cantidad_de_unidades": product.quantity,
                        "valor_unitario": product.price_unit,
                        "codigo_de_tipo_de_precio":"01",
                        "precio_de_venta_unitario_valor_referencial": product.price_unit,
                        "afectacion_al_igv": affectIgv,
                        "porcentaje_de_igv": percentIgv,
                        "monto_de_igv": float(amountIgv),
                        "valor_de_venta_por_item": product.price_subtotal,
                        "total_por_item": product.price_total
                    }
            items.append(item)

        # end items

        # create json
        data = {
                    "version_del_ubl": "v21",
                    "serie_y_numero_correlativo": serie,
                    "fecha_de_emision": self.date_invoice,
                    "hora_de_emision": "10:11:11",
                    "tipo_de_documento": document_type,
                    "tipo_de_moneda": self.company_currency_id.name,
                    "fecha_de_vencimiento": self.date_due,
                    "datos_del_emisor": {
                        "codigo_del_domicilio_fiscal": "0001"
                    },
                    "datos_del_cliente_o_receptor":{
                        "numero_de_documento": self.partner_id.vat,
                        "tipo_de_documento": "6",
                        "apellidos_y_nombres_o_razon_social": self.partner_id.name,
                        "direccion": self.partner_id.street,
                        "ubigeo": self.partner_id.zip
                    },
                    "totales": {
                        "total_operaciones_gravadas": self.amount_untaxed,
                        "sumatoria_igv": self.amount_tax,
                        "total_de_la_venta": self.amount_total
                    },
                    "items": items,
                    "informacion_adicional":{
                        "tipo_de_operacion": "0101",
                        "leyendas":[]
                    },
                    "extras":{
                        "forma_de_pago": "Efectivo"
                    }
                }

        # edito el api_json
        html_json = json.dumps(data,sort_keys=True, indent=4, separators=(',', ': '))
        self.write({'api_json':html_json})

        return {
            "json": html_json
        }

    # validar y guardar json
    @api.multi
    def action_invoice_open(self,values):
        token = self.company_id.api_token
        url = self.company_id.api_url
        serie = self.serie_id.name + '-#'
        document_type = self.serie_id.document_type_id.code

        products = self.invoice_line_ids
        items = []

        for product in products:

            if product.invoice_line_tax_ids.amount != 0:
                amountIgv = (int(product.price_subtotal) * int(product.invoice_line_tax_ids.amount)) / 100
                affectIgv = 10
                percentIgv = int(product.invoice_line_tax_ids.amount)
            else:
                amountIgv = 0
                affectIgv = 20
                percentIgv = 18

            json_string = product.name.replace('\n', ' ')
            item = {
                        "codigo_interno_del_producto": "P0121",
                        "descripcion_detallada": json_string,
                        "codigo_producto_de_sunat": "51121703",
                        "unidad_de_medida": product.uom_id.name,
                        "cantidad_de_unidades": product.quantity,
                        "valor_unitario": product.price_unit,
                        "codigo_de_tipo_de_precio":"01",
                        "precio_de_venta_unitario_valor_referencial": product.price_unit,
                        "afectacion_al_igv": affectIgv,
                        "porcentaje_de_igv": percentIgv,
                        "monto_de_igv": float(amountIgv),
                        "valor_de_venta_por_item": product.price_subtotal,
                        "total_por_item": product.price_total
                    }
            items.append(item)

        # end items

        # create json
        data = {
                    "version_del_ubl": "v21",
                    "serie_y_numero_correlativo": serie,
                    "fecha_de_emision": self.date_invoice,
                    "hora_de_emision": "10:11:11",
                    "tipo_de_documento": document_type,
                    "tipo_de_moneda": self.company_currency_id.name,
                    "fecha_de_vencimiento": self.date_due,
                    "datos_del_emisor": {
                        "codigo_del_domicilio_fiscal": "0001"
                    },
                    "datos_del_cliente_o_receptor":{
                        "numero_de_documento": self.partner_id.vat,
                        "tipo_de_documento": "6",
                        "apellidos_y_nombres_o_razon_social": self.partner_id.name,
                        "direccion": self.partner_id.street,
                        "ubigeo": self.partner_id.zip
                    },
                    "totales": {
                        "total_operaciones_gravadas": self.amount_untaxed,
                        "sumatoria_igv": self.amount_tax,
                        "total_de_la_venta": self.amount_total
                    },
                    "items": items,
                    "informacion_adicional":{
                        "tipo_de_operacion": "0101",
                        "leyendas":[]
                    },
                    "extras":{
                        "forma_de_pago": "Efectivo"
                    }
                }

        # edito el api_json
        html_json = json.dumps(data,sort_keys=True, indent=4, separators=(',', ': '))
        self.write({'api_json':html_json})

        # COPIA addons/account/models/account_invoice.py
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

class ApiConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    api_token = fields.Char(string='API Token')
    api_url = fields.Char(string='API URL', help="Example sub.domain.com/api/documents")


    # get_ y set_ se cargan automatico en odoo

    def get_values(self):
        res = super(ApiConfig, self).get_values()
        res.update(
            api_token=self.env['ir.config_parameter'].sudo().get_param('res.config.settings.api_token'),
            api_url=self.env['ir.config_parameter'].sudo().get_param('res.config.settings.api_url')
        )
        return res

    def set_values(self):
        super(ApiConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('res.config.settings.api_token', self.api_token)
        self.env['ir.config_parameter'].sudo().set_param('res.config.settings.api_url', self.api_url)
