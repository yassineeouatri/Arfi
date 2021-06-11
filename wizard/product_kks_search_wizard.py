# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _

_logger = logging.getLogger(__name__)


class product_kks_search_wizard(models.Model):

    _name = "product.kks.search.wizard"
    _description = "Product KKS Search Wizard"

    name = fields.Char("Recherche", default="Recherche")
    type = fields.Selection(
        [
            ("search_magasin", "Code magasin"),
            ("search_ref_fab", "Référence Fabricant"),
            ("search_ref_com", "Référence Commercial"),
            ("search_outillage", "Code outillage"),
        ],
        "Type de la recherche",
    )
    customer_id = fields.Many2one(
        "res.partner", "Client", domain=[("customer", "=", True)]
    )
    magasin_id = fields.Many2one("product.magasin", "Code Magasin")
    ref_fab_id = fields.Many2one("product.ref.fab", "Réf Fabricant")
    ref_com_id = fields.Many2one("product.ref.com", "Réf Commercial")
    outillage_id = fields.Many2one("product.outillage", "Désignation")
    code = fields.Char("Résultat", readonly=True)
    material_id = fields.Many2one("product.product.material", "Matière")
    piece_id = fields.Many2one("product.piece", "Pièce")

    @api.onchange("outillage_id")
    def _onchange_appareil(self):
        self.code = self.outillage_id.code

    def print_report_magasin(self):
        if self.magasin_id:
            name = "Recherche par code magasin"
            if self.customer_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_customer_id": self.customer_id.id,
                        "search_default_magasin_id": self.magasin_id.id,
                    },
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_magasin_id": self.magasin_id.id,
                    },
                }
        else:
            raise ValidationError(_("Veuillez sélectionner la valeur du magasin"))

    def print_report_fab(self):
        if self.ref_fab_id:
            name = "Recherche par fabriquant"
            if self.customer_id:

                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_customer_id": self.customer_id.id,
                        "search_default_ref_fab": self.ref_fab_id.name,
                    },
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_ref_fab": self.ref_fab_id.name,
                    },
                }
        else:
            raise ValidationError(_("Veuillez sélectionner le référence fabriquant"))

    def print_report_com(self):
        if self.ref_com_id:
            name = "Recherche par commercial"
            if self.customer_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_customer_id": self.customer_id.id,
                        "search_default_ref_com": self.ref_com_id.name,
                    },
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                    ],
                    "context": {
                        "search_default_ref_com": self.ref_com_id.name,
                    },
                }
        else:
            raise ValidationError(_("Veuillez sélectionner le réference commercial"))

    def print_report_outillage(self):
        if self.outillage_id:
            name = "Recherche par outillage"
            if self.customer_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.outillage.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (
                            self.env.ref(
                                "arfi.view_product_kks_outillage_report_tree"
                            ).id,
                            "tree",
                        )
                    ],
                    "context": {
                        "search_default_customer_id": self.customer_id.id,
                        "search_default_outillage_id": self.outillage_id.id,
                    },
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks.outillage.report",
                    "view_mode": "tree",
                    "view_type": "form",
                    "name": name,
                    "views": [
                        (
                            self.env.ref(
                                "arfi.view_product_kks_outillage_report_tree"
                            ).id,
                            "tree",
                        )
                    ],
                    "context": {
                        "search_default_outillage_id": self.outillage_id.id,
                    },
                }
        else:
            raise ValidationError(_("Veuillez sélectionner la valeur outillage"))

    def print_report_matiere(self):
        if self.material_id:
            name = "Recherche par matière"
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.kks.matiere.report",
                "view_mode": "tree",
                "view_type": "form",
                "name": name,
                "views": [
                    (
                        self.env.ref(
                            "arfi.view_product_kks_matiere_report_tree"
                        ).id,
                        "tree",
                    )
                ],
                "context": {
                    "search_default_material_id": self.material_id.id
                },
            }
        else:
            raise ValidationError(_("Veuillez sélectionner la valeur matière"))

    def print_report_piece(self):
        if self.piece_id:
            name = "Recherche par pièce"
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.kks.piece.report",
                "view_mode": "tree",
                "view_type": "form",
                "name": name,
                "views": [
                    (
                        self.env.ref(
                            "arfi.view_product_kks_piece_report_tree"
                        ).id,
                        "tree",
                    )
                ],
                "context": {
                    "search_default_piece_id": self.piece_id.id
                },
            }
        else:
            raise ValidationError(_("Veuillez sélectionner la valeur de la pièce"))

    def action_search(self):
        # raise ValidationError(_(self.type))
        if self.type == "search_magasin":
            name = "Recherche par code magasin"

        elif self.type == "search_ref_fab":
            name = "Recherche par Référence Fabricant"
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.kks.report",
                "view_mode": "tree",
                "view_type": "form",
                "name": name,
                "views": [
                    (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                ],
                "context": {
                    "search_default_customer_id": self.customer_id.id,
                    "search_default_ref_fab": self.ref_fab_id.name,
                },
            }
        elif self.type == "search_ref_com":
            name = "Recherche par Référence Commercial"
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.kks.report",
                "view_mode": "tree",
                "view_type": "form",
                "name": name,
                "views": [
                    (self.env.ref("arfi.view_product_kks_report_tree").id, "tree")
                ],
                "context": {
                    "search_default_customer_id": self.customer_id.id,
                    "search_default_ref_com": self.ref_com_id.name,
                },
            }
