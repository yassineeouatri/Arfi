# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_purchase_evaluation_wizard(models.Model):

    _name = "product.purchase.evaluation.wizard"
    _description = "Product Purchase Evaluation Wizard"

    purchase_id = fields.Many2one("product.purchase", "Commande")
    evaluation_ids = fields.Many2many(
        "product.purchase.type.evaluation",
        "rel_purchase_evaluation",
        "purchase_id",
        "evaluation_id",
        "Evaluations",
    )

    def action_execute(self):
        for obj in self.evaluation_ids:
            self.env["product.purchase.evaluation"].create(
                {"purchase_id": self.purchase_id.id, "type_evaluation_id": obj.id}
            )
