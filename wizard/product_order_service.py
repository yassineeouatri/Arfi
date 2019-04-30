# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_order_service_wizard(models.Model):
    
    _name = 'product.order.service.wizard'
    _description = 'Product Order Service Wizard'

    
    order_id = fields.Many2one('product.order','Commande')
    service_ids = fields.Many2many('product.mesure.service','rel_order_service',
                                                  'order_id','service_id','Service')
    
    def action_execute(self):
        for obj in self.service_ids:
            self.env['product.order.service'].create({'order_id' : self.order_id.id,
                                                       'service_id' : obj.id})
            
            

class product_order_service_delete_wizard(models.Model):
    
    _name = 'product.order.service.delete.wizard'
    _description = 'Product order service delete Wizard'

    
    order_service_id = fields.Many2one('product.order.service','Service')
    
    def action_delete(self):
        obj=self.env['product.order.service'].search([('id', '=', self.order_service_id.id)])
        if obj:
            obj.unlink()
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

