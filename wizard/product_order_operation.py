# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_appareil_order_operation_wizard(models.Model):
    
    _name = 'product.appareil.order.operation.wizard'
    _description = 'Product Appareil Order Operation Wizard'

    
    order_id = fields.Many2one('product.order','Commande')
    appareil_id = fields.Many2one('product.template','Appareil')
    operation_ids = fields.Many2many('product.operation','rel_appareil_order_operation',
                                                  'order_id','operation_id','Opérations')
    
    def action_execute(self):
        for obj in self.operation_ids:
            self.env['product.order.operation'].create({'order_id' : self.order_id.id,
                                                        'appareil_id' : self.appareil_id.id,
                                                        'operation_id' : obj.id,
                                                        'order_' : 1})
            
class product_piece_order_operation_wizard(models.Model):
    
    _name = 'product.piece.order.operation.wizard'
    _description = 'Product Piece Order Operation Wizard'

    
    order_id = fields.Many2one('product.order','Commande')
    appareil_id = fields.Many2one('product.template','Appareil')
    piece_id = fields.Many2one('product.piece','Appareil')
    operation_ids = fields.Many2many('product.operation','rel_piece_order_operation',
                                                  'order_id','operation_id','Opérations')
    
    def action_execute(self):
        for obj in self.operation_ids:
            self.env['product.order.operation'].create({'order_id' : self.order_id.id,
                                                        'appareil_id' : self.appareil_id.id,
                                                        'piece_id' : self.piece_id.id,
                                                        'operation_id' : obj.id,
                                                        'order_' : 1})

