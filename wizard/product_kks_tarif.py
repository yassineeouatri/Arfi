# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class product_kks_tarif_wizard(models.Model):

    _name = "product.kks.tarif.wizard"
    _description = "Product KKS tarif Wizard"

    kks_id = fields.Many2one("product.kks", "KKS")
    nature_ids = fields.Many2many(
        "product.nature", "rel_kks_nature", "kks_id", "nature_id", "Natures"
    )

    @api.multi
    def action_execute(self):
        for obj in self.nature_ids:
            montant = montant2 = 0
            if self.kks_id.appareil_id:
                contract_obj = self.env["product.appareil.price"].search(
                    [
                        ("appareil_id", "=", self.kks_id.appareil_id.id),
                        ("nature_id", "=", obj.id),
                    ],
                    limit=1,
                )
                if contract_obj:
                    montant2 = contract_obj.purchase_price
                    montant = contract_obj.sale_price
            self.env["product.kks.tarif"].create(
                {
                    "kks_id": self.kks_id.id,
                    "nature_id": obj.id,
                    "fact": "Contrat",
                    "montant": montant,
                    "montant2": montant2,
                }
            )
