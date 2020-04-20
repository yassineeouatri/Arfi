# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_template_procedure(models.Model):
    
    _name = 'product.template.procedure'
    _description = 'Product Template Procedure'

    
    appareil_id = fields.Many2one('product.template','Appareil',domain=[('type','=','appareil')])
    directory_id = fields.Many2one('muk_dms.directory', string="Directory", required=False)
    type_file = fields.Selection([('ins','Instruction de travail'),
                             ('ope','Mode Opératoire'),('man','Manuel de Maintenance')
                             ,('codif','Codification')] ,'Type du fichier' , required=False)
    procedure_ids = fields.Many2many('muk_dms.file',
                                       'rel_template_procedure',
                                       'file_id','appareil_id',
                                       'Procédures',)

  
    
    def action_procedure_it_execute(self):
        for obj in self.procedure_ids:
            self.env['product.procedure'].create({'product_tmpl_id' : self.appareil_id.id,
                                                  'directory_id' : self.directory_id.id,
                                                  'type_file' : self.type_file,
                                                  'file_id' : obj.id})
            
    def action_procedure_mm_execute(self):
        for obj in self.procedure_ids:
            self.env['product.procedure'].create({'product_tmpl_id' : self.appareil_id.id,
                                                  'directory_id' : self.directory_id.id,
                                                  'type_file' : self.type_file,
                                                  'file_id' : obj.id})
    def action_procedure_ope_execute(self):
        for obj in self.procedure_ids:
            self.env['product.procedure'].create({'product_tmpl_id' : self.appareil_id.id,
                                                  'directory_id' : self.directory_id.id,
                                                  'type_file' : self.type_file,
                                                  'file_id' : obj.id})
    def action_procedure_codif_execute(self):
        for obj in self.procedure_ids:
            self.env['product.procedure'].create({'product_tmpl_id' : self.appareil_id.id,
                                                  'directory_id' : self.directory_id.id,
                                                  'type_file' : self.type_file,
                                                  'file_id' : obj.id})
