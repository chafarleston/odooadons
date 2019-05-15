# -*- encoding: utf-8 -*-
##############################################################################
#
#    Spellbound soft solution.
#    Copyright (C) 2017-TODAY Spellbound soft solution(<http://www.spellboundss.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, api, _
from odoo import SUPERUSER_ID
from datetime import datetime, date, time, timedelta
from pytz import timezone
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError, ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    mail_ids = fields.One2many('pos.mail.mail','mail_id',string="Mail")
    print_z_report = fields.Boolean('Print Z Report')
    
class PosMail(models.Model):
    _name = 'pos.mail.mail'

    mail_id = fields.Many2one('pos.config',string="Mail")
    name = fields.Char("Email ID")

class pos_session(models.Model):
    _inherit = 'pos.session'
    
    def action_pos_session_close(self):
        
        res = super(pos_session, self).action_pos_session_close()
        pos_config_id = self.env['pos.config'].search([('id','=',self.config_id.id)])
        
        if pos_config_id.print_z_report == True:
           
            if pos_config_id.mail_ids:
                mail_list = ''
                for mail in pos_config_id.mail_ids:
#                     mail_list.append(mail.name)
                    mail_list += mail.name +','
            else:
                error_msg = _('Please Define a Racipient Mail ID')
                raise ValidationError(error_msg)
            email_to = mail_list
            email_template_obj = self.env['mail.template']
            template_ids = email_template_obj.search([('model', '=','pos.session')])
            for temp in template_ids:
                if temp.name  == "Z-report - Send by Email":
                    values = temp.generate_email(self.id)
                    att_obj = self.env['ir.attachment']
                    server_obj = self.env['ir.mail_server']
                    server_ids = server_obj.sudo().search([])
                    attachment_data = {
                    'name': "Emails :- " + self.name,
                    'datas_fname': self.name+".pdf", # your object File Name
                    'db_datas': values['attachments'][0][1],  # your object Data
                    }
                    att_id = att_obj.create(attachment_data)
                    values['subject'] = temp.subject
                    values['email_to'] = email_to
                    if server_ids:
                        values['email_from'] = server_ids[0].smtp_user or False
                    values['email_cc'] = self.env.user.company_id.email
                    values['body_html'] = """
                    &nbsp;<table border="0" width="100%" cellpadding="0" bgcolor="#ededed" style="padding: 20px; background-color: #ededed" summary="o_mail_notification">
                        <tbody>
       
                          <!-- HEADER -->
                          <tr>
                            <td align="center" style="min-width: 590px;">
                              <table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color: rgb(135,90,123); padding: 20px;">
                                <tbody><tr>
                                  <td valign="middle"><span style="font-size:20px; color:white; font-weight: bold;">POS z-report</span></td>
                                  <td valign="middle" align="right">
                                  </td>
                                </tr>
                              </tbody></table>
                            </td>
                          </tr>
       
                          <!-- CONTENT -->
                          <tr>
                            <td align="center" style="min-width: 590px;">
                              <table width="590" border="0" cellpadding="0" bgcolor="#ffffff" style="min-width: 590px; background-color: rgb(255, 255, 255); padding: 20px;">
                                <tbody>
                                  <tr><td valign="top" style="font-family:Arial,Helvetica,sans-serif; color: #555; font-size: 14px;">
                                    </td></tr></tbody></table></td></tr><tr><td align="center" style="min-width: 590px;"><table width="590" border="0" cellpadding="0" bgcolor="#875A7B" style="min-width: 590px; background-color: rgb(135,90,123); padding: 20px;"><tbody><tr><td valign="middle" align="left" style="color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;"><p>Hello Dear,<br></p><p> POS z-report is attached in the PDF.</p><p>Thanks,</p></td>
                                  <td valign="middle" align="right" style="color: #fff; padding-top: 10px; padding-bottom: 10px; font-size: 12px;"><br><br></td>
                                </tr>
                              </tbody></table>
                            </td>
                          </tr>
                          <tr>
                            <td align="center"> Powered by Spellbound Soft Solution. </td>
                          </tr>
                        </tbody>
                    </table>
                                                """
                    values['attachment_ids'] = [(6, 0, [att_id.id])]
                    mail_mail_obj = self.env['mail.mail']
    #                     mail_mail_obj = self.env['mail.message']
                         
                    msg_id = mail_mail_obj.sudo().create(values)
                    if msg_id:
                        msg_id.sudo().send()
    #                         mail_mail_obj.send( [msg_id.id])
        return res
         
        
    

    @api.multi
    def get_company_data(self):
        return self.user_id.company_id
    
    @api.multi
    def get_total_sales(self):
        total_price = 0.0
        if self:
            for order in self.order_ids:
                    for line in order.lines:
                            total_price += (line.qty * line.price_unit)
        return total_price
    
    @api.multi
    def get_total_returns(self):
        pos_order_obj = self.env['pos.order']
        total_return = 0.0
        if self:
            for order in pos_order_obj.search([('session_id', '=', self.id)]):
                if order.amount_total < 0:
                    total_return += abs(order.amount_total)
        return total_return

    @api.multi
    def get_total_tax(self):
        total_tax = 0.0
        if self:
            pos_order_obj = self.env['pos.order']
            total_tax += sum([order.amount_tax for order in pos_order_obj.search([('session_id', '=', self.id)])])
        return total_tax \

    @api.multi
    def get_total_discount(self):
        total_discount = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                total_discount += sum([((line.qty * line.price_unit) * line.discount) / 100 for line in order.lines])
        return total_discount
    
    @api.multi
    def get_total_first(self):
        global gross_total
        if self:
            gross_total = (self.get_total_sales() + self.get_total_tax()) \
                 + self.get_total_discount()
        return gross_total
    
    @api.multi
    def get_user(self):
        if self._uid == SUPERUSER_ID:
            return True

    @api.multi
    def get_gross_total(self):
        total_cost = 0.0
        gross_total = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    total_cost += line.qty * line.product_id.standard_price
        gross_total = self.get_total_sales() - \
                    + self.get_total_tax() - total_cost
        return gross_total

    @api.multi
    def get_net_gross_total(self):
        net_gross_profit = 0.0
        total_cost = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    total_cost += line.qty * line.product_id.standard_price
            net_gross_profit = self.get_total_sales() - self.get_total_tax() - total_cost
        return net_gross_profit  

    @api.multi
    def get_product_cate_total(self):
        balance_end_real = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    balance_end_real += (line.qty * line.price_unit)
        return balance_end_real

    @api.multi
    def get_product_name(self, category_id):
        if category_id:
            category_name = self.env['pos.category'].browse([category_id]).name
            return category_name

    @api.multi
    def get_product_category(self):
        product_list = []
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    flag = False
                    product_dict = {}
                    for lst in product_list:
                        if line.product_id.pos_categ_id:
                            if lst.get('pos_categ_id') == line.product_id.pos_categ_id.id:
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
#                                 if line.product_id.pos_categ_id.show_in_report:
                                lst['qty'] = lst.get('qty') or 0.0 + line.qty
                                flag = True
                        else:
                            if lst.get('pos_categ_id') == '':
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
                                lst['qty'] = lst.get('qty') or 0.0 + line.qty
                                flag = True
                    if not flag:
                        if line.product_id.pos_categ_id:
                            product_dict.update({
                                        'pos_categ_id': line.product_id.pos_categ_id and line.product_id.pos_categ_id.id or '',
                                        'price': (line.qty * line.price_unit),
                                        'qty': line.qty
                                    })
                        else:
                            product_dict.update({
                                        'pos_categ_id': line.product_id.pos_categ_id and line.product_id.pos_categ_id.id or '',
                                        'price': (line.qty * line.price_unit),
                                    })
                        product_list.append(product_dict)
        return product_list
    
    @api.multi
    def get_payments(self):
        if self:
            statement_line_obj = self.env["account.bank.statement.line"]
            pos_order_obj = self.env["pos.order"]
            company_id = self.env['res.users'].browse([self._uid]).company_id.id
            pos_ids = pos_order_obj.search([('session_id', '=', self.id),
                                            ('state', 'in', ['paid', 'invoiced', 'done']),
                                            ('user_id', '=', self.user_id.id), ('company_id', '=', company_id)])
            data = {}
            if pos_ids:
                pos_ids = [pos.id for pos in pos_ids]
                st_line_ids = statement_line_obj.search([('pos_statement_id', 'in', pos_ids)])
                if st_line_ids:
                    a_l = []
                    for r in st_line_ids:
                        a_l.append(r['id'])
                    self._cr.execute("select aj.name,sum(amount) from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                    "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                    "group by aj.name ", (tuple(a_l),))

                    data = self._cr.dictfetchall()
                    return data
            else:
                return {}
 

