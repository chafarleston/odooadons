from odoo import api,models

class InvoiceReportSunat(models.AbstractModel):
    _name = "report.facturaloperu_api_invoice.invoice_mov_template"

    @api.model
    def get_report_values(self,docids,data=None):

        return {
            "doc_ids":docids,
            "docs":self,
        }