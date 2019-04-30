# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)



class product_observation(models.Model):
    _name='product.observation'
    
    order_id = fields.Many2one('product.order' , 'Commande',required=True)
    obs_devis = fields.Text('Observation Devis',required=False)
    obs_recap = fields.Text('Observation Récap',required=False)
    obs_atelier = fields.Text('Observation Atelier',required=False)
    
    _defaults = {
    }

    def case_execute(self):
        self._cr.execute("update product_order set obs_devis='"+self.obs_devis+"',obs_recap='"+self.obs_devis+"',obs_atelier='"+self.obs_atelier+"'")
        return True
                        