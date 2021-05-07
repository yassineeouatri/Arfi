# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_order_test_wizard(models.Model):

    _name = "product.order.test.wizard"
    _description = "Product Order Test Wizard"

    order_id = fields.Many2one("product.order", "Commande")
    test_ids = fields.Many2many(
        "product.mesure.test", "rel_order_test", "order_id", "test_id", "test"
    )

    def action_execute(self):
        for obj in self.test_ids:
            self.env["product.order.test"].create(
                {"order_id": self.order_id.id, "test_id": obj.id}
            )


class product_order_test_delete_wizard(models.Model):

    _name = "product.order.test.delete.wizard"
    _description = "Product order test delete Wizard"

    order_test_id = fields.Many2one("product.order.test", "Test")

    def action_delete(self):
        obj = self.env["product.order.test"].search(
            [("id", "=", self.order_test_id.id)]
        )
        if obj:
            obj.unlink()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
