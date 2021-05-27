# -*- coding: utf-8 -*-
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_contract_appareil(models.Model):

    _name = "product.contract.appareil"
    _description = "Contrats des appareils"

    kks_id = fields.Many2one("product.kks", "Code KKS")
    customer_id = fields.Many2one(
        "res.partner",
        "Client",
        related="kks_id.customer_id",
        store=True,
        readonly=False,
    )
    appareil_id = fields.Many2one(
        "product.template",
        "Appareil",
        related="kks_id.appareil_id",
        store=True,
        readonly=False,
    )
    item = fields.Integer(
        related="kks_id.item", string="Item", store=True, readonly=False
    )
    maker_id = fields.Many2one(
        "product.template.maker",
        "Marque",
        related="kks_id.maker_id",
        store=True,
        readonly=False,
    )
    nature_id = fields.Many2one("product.nature", "Action")
    montant = fields.Float("Montant (Dhs)")
    magasin_id = fields.Many2one("product.magasin", "Magasin")
    fact = fields.Selection([("Forfait", "Forfait")], "Fact")


class product_contract_piece(models.Model):

    _name = "product.contract.piece"
    _description = "Contrats des pieces"

    kks_id = fields.Many2one("product.kks", "Code KKS")
    customer_id = fields.Many2one(
        "res.partner",
        "Client",
        related="kks_id.customer_id",
        store=True,
        readonly=False,
    )
    piece_id = fields.Many2one("product.piece", "Pièce", readonly=False)
    item = fields.Integer(string="Item", readonly=False)
    nature_id = fields.Many2one("product.nature", "Nature Travaux")
    montant = fields.Float("Montant (Dhs)")
    magasin_id = fields.Many2one("product.magasin", "Magasin")
    fact = fields.Selection([("Piece", "Pièce")], "Fact")
