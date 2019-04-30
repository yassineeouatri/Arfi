# -*- coding: utf-8 -*-

import time
from odoo import api, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ReportTEMPLATECARTOUCHE(models.AbstractModel):
    _name = 'report.arfi.action_report_producttemplatecartouche'
    
  
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('id'))
        pieces = self.env['product.piece'].search([('appareil_id', '=', docs.id),
                                                   ('material_id','!=',None)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'pieces' : pieces
        }
        return self.env['report'].render('arfi.action_report_producttemplatecartouche', docargs)
    