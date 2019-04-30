# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import _
from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class product_piece_delete_wizard(models.Model):
    
    _name = 'product.piece.delete.wizard'
    _description = 'Product piece delete Wizard'

    
    piece_id = fields.Many2one('product.piece','Pièce')
    
    def action_delete(self):
        piece=self.env['product.piece'].search([('id', '=', self.piece_id.id)])
        appareil_id=self.env['product.template'].search([('id', '=', self.piece_id.appareil_id.id)]).id
        if piece:
            piece.unlink()
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

