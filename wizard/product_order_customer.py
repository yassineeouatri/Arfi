# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class product_order_customer_wizard(models.TransientModel):
    _name = "product.order.customer.wizard"
    _description = "Product Order/Customer Wizard"

    customer_id = fields.Many2one(
        "res.partner", "Client", domain=[("customer", "=", True)]
    )
    year = fields.Char("Année", size=4)

    @api.multi
    def print_report(self):
        data = {}
        data["form"] = self.read(["customer_id", "year"])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data["form"].update(self.read(["customer_id", "year"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_productordercustomer", data=data
        )
