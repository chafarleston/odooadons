# -*- encoding: utf-8 -*-
##############################################################################
#
#    Spellbound soft solutions.
#    Copyright (C) 2017-TODAY Spellbound soft solutions(<http://www.spellboundss.com>).
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
{
    'name': 'POS Z Report',
    "version": "1.0",
    'category': 'Point of Sale',
    'description': """
         The Z report is an overview of the entire shift, from beginning to end.
    """,
    'author': 'Spellbound Soft Solutions',
    'website': 'http://www.spellboundss.com',
    'images' : ['static/description/images/banner.jpg'],
    'depends':  ['base', 'point_of_sale'],
    'data': [
        'views/z_report_pdf_template.xml',
        'views/report.xml',
        'views/point_of_sale.xml',
        'data/mail_attachment.xml',
        'security/ir.model.access.csv'
        
    ],
    'qweb': [],
    'price':20,
    'license': "LGPL-3",

    'currency':'EUR',
    'auto_install': False,
    'installable': True,
}
