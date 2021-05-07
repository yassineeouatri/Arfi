# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_purchase_etat_wizard(models.Model):

    _name = "product.purchase.etat.wizard"
    _description = "Product Purchase Etat Wizard"

    date_from = fields.Date("Date Début")
    date_to = fields.Date("Date Fin")
    no_order = fields.Integer("Nb de Commandes")
    no_order_nc = fields.Integer("Nb de NC")
    tx_nc = fields.Float("Tx de Non Conformité")
