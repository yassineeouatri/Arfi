# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_template_nature(models.Model):
    
    _name = 'product.template.nature'
    _description = 'Product Template Nature'

    
    appareil_id = fields.Many2one('product.template','Appareil',domain=[('type','=','appareil')])
    nature_ids = fields.Many2many('product.nature',
                                       'rel_template_nature',
                                       'nature_id','appreil_id',
                                       'Informations',)

  
    
    def action_execute(self):
        for obj in self.nature_ids:
            self.env['product.appareil.price'].create({'appareil_id' : self.appareil_id.id,
                                                       'nature_id' : obj.id})

