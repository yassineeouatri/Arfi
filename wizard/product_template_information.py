# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_template_information(models.Model):

    _name = "product.template.information"
    _description = "Product Template Information"

    appareil_id = fields.Many2one(
        "product.template", "Appareil", domain=[]
    )
    information_ids = fields.Many2many(
        "product.attribute",
        "rel_template_attribute",
        "information_id",
        "attribute",
        "Informations",
    )

    def action_execute(self):
        for obj in self.information_ids:
            self.env["product.attribute.line"].create(
                {"product_tmpl_id": self.appareil_id.id, "attribute_id": obj.id}
            )
