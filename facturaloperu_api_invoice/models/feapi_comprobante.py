# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FeapiComprobante(models.Model):
    _name = "feapi.comprobante"
    _description = "Facturalo Peru"


    @api.model
    def _get_api_url(self):
        frame = '<iframe src="{}" \
            marginwidth="0" marginheight="0" frameborder="no" \
            style="height: 100%; width: 100%; \
            border-width:0px;"></iframe>'

        not_found_msg = """
        <div style="font-size:12pt;" class="alert alert-warning">
            <strong style="font-size:14pt">Parametro no encontrado.</strong>
            <br></br>
            El parametro <i>«facturaloperu_api_invoice.api_url»</i> no se \
            encuentra creado en esta instancia, consulte con el \
            <i>Administrador.</i>
        </div>"""

        not_found_div = """
        <div id="api_frame" style="position:absolute; left:0; top:0; \
            width:100%; height:100%;">
            {}
        </div>""".format(not_found_msg)

        api_url = self.env['ir.config_parameter'].sudo().get_param(
            'facturaloperu_api_invoice.api_url'
        )

        if not api_url:
            return not_found_div

        api_frame = frame.format(api_url)
        return api_frame

    api_frame = fields.Html(
        default=lambda self: self._get_api_url()
    )