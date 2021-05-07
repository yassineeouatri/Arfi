# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_attribute_delete_wizard(models.Model):

    _name = "product.attribute.delete.wizard"
    _description = "Product attribute delete Wizard"

    attribute_line_id = fields.Many2one("product.attribute.line", "Line")

    def action_delete(self):
        obj = self.env["product.attribute.line"].search(
            [("id", "=", self.attribute_line_id.id)]
        )
        if obj:
            obj.unlink()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
