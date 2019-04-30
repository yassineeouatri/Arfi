# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_kks_pps_select(models.Model):
    
    _name = 'product.kks.pps.select'
    _description = 'Product KKS PPS Select'

    
    kks_id = fields.Many2one('product.kks','KKS')
    directory_id = fields.Many2one('muk_dms.directory', string="Directory", required=False)
    type_file = fields.Selection([('ins','Instruction de travail'),
                             ('ope','Mode Opératoire'),('man','Manuel de Maintenance'),
                             ('prev','Plan Prévention')] ,'Type du fichier' , required=False)
    pps_ids = fields.Many2many('muk_dms.file',
                                       'rel_kks_pps',
                                       'file_id','kks_id',
                                       'Procédures',)

  
    
    def action_execute(self):
        for obj in self.pps_ids:
            self.env['product.kks.pps'].create({'kks_id' : self.kks_id.id,
                                                  'directory_id' : self.directory_id.id,
                                                  'type_file' : self.type_file,
                                                  'file_id' : obj.id})