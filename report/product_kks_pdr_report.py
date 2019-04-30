# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ReportKKSPDR(models.AbstractModel):
    _name = 'report.arfi.action_report_productkkspdr'
    
    def _get_info(self, customer_id, arret_id):
        return {
            'customer': customer_id[1],
            'arret': arret_id[1]
        }
    
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        records = self.env['product.kks.pdr.full.report'].search([('customer_id', '=', docs.customer_id.id),
                                                        ('arret_id', '=', docs.arret_id.id)])
        unite=''
        if records:
            unite = records[0].unite_id.code
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'records': records,
            'unite': unite,
            'get_info': self._get_info(data['form']['customer_id'], data['form']['arret_id']),
        }
        return self.env['report'].render('arfi.action_report_productkkspdr', docargs)
class ReportKKSPDRSORTIR(models.AbstractModel):
    _name = 'report.arfi.action_report_productkkspdrsortir'
    
    def _get_info(self, customer_id, arret_id):
        return {
            'customer': customer_id[1],
            'arret': arret_id[1]
        }
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        records = self.env['product.kks.pdr.sortir.report'].search([('customer_id', '=', docs.customer_id.id),
                                                         ('arret_id', '=', docs.arret_id.id)])
        if records:
            unite = records[0].unite_id.code
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'records': records,
            'unite': unite,
            'get_info': self._get_info(data['form']['customer_id'], data['form']['arret_id']),
        }
        return self.env['report'].render('arfi.action_report_productkkspdrsortir', docargs)