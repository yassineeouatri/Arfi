# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import logging
import xlsxwriter
import sys
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import tools, _
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class product_report(models.Model):
    
    _name = 'product.report'
    _description = 'Reporting'
    
    def get_return(self,fichier):
        url = '/web/static/reporting/' + fichier
        if url:
            return { 'type': 'ir.actions.act_url','target': 'new', 'url': url, 'nodestroy': True }
        else:
            return True           
    def generer_stock(self):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env['product.image.directory'].search([('type','=','reporting')])
        for result in results:
            directory=result.name
        fichier="Stock _"+time.strftime('%H%M%S')+".xlsx"
        workbook = xlsxwriter.Workbook(directory + fichier)
        style_title = workbook.add_format({'bg_color' : '#003366','color' : 'white','text_wrap' : True, 'align' : 'center','valign' : 'vcenter',
                                                          'top' : 1, 'bottom' : 1,})
        style = workbook.add_format({'text_wrap' : True, 'align' : 'center','valign' : 'vcenter','top' : 1, 'bottom' : 1, })
        style_ = workbook.add_format({'text_wrap' : True, 'align' : 'center','valign' : 'vcenter','left' : 1, })

        feuille=workbook.add_worksheet('Stock')
        feuille.set_zoom(85)
        feuille.set_tab_color('yellow')
        feuille.set_column('A:A', 30)
        feuille.set_column('B:B', 20)
        x=1
        feuille.write('A'+str(x),'Code Mag',style_title)
        feuille.write('B'+str(x),'Stock',style_title)
        feuille.write('C'+str(x),'',style_)
        x=x+1
        self._cr.execute("""select a.code,b.value from product_magasin a
                            inner join product_kks_stock b on a.id=b.magasin_id
                            inner join product_info c on b.info_id=c.id
                            where c.name like 'Stock'
                            order by a.code""")

        for res in self.env.cr.fetchall():
            feuille.write('A'+str(x),res[0],style)
            feuille.write('B'+str(x),res[1],style)
            feuille.write('C'+str(x),'',style_)
            x=x+1

        workbook.close()
        return self.get_return(fichier)

