# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_kks_piece_wizard(models.Model):

    _name = "product.kks.piece.wizard"
    _description = "Product KKS piece Wizard"

    kks_id = fields.Many2one("product.kks", "KKS")
    appareil_id = fields.Many2one("product.template", "Appareil")
    piece_ids = fields.Many2many(
        "product.piece", "rel_kks_piece", "kks_id", "piece_id", "Pièces"
    )

    def action_execute(self):
        for obj in self.piece_ids:
            self.env["product.kks.piece"].create(
                {
                    "kks_id": self.kks_id.id,
                    "appareil_id": self.appareil_id.id,
                    "piece_id": obj.id,
                }
            )
