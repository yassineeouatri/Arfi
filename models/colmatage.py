# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_colmatage(models.Model):

    _name = "product.colmatage"
    _description = "Colmatage"
    _order = "date_colmatage desc"

    date_colmatage = fields.Date("Date Colmatage", default=fields.Date.today)
    customer_id = fields.Many2one(
        "res.partner", "Client", domain=[("customer", "=", True)]
    )
    affaire_id = fields.Many2one(
        "product.affaire", "N° Affaire", domain=[("type", "=", "colmatage")]
    )
    localisation = fields.Char("Localisation")
    pression = fields.Char("Pression")
    temperature = fields.Char("Température")
    intervention = fields.Char("N° Intervention")
    date_from = fields.Date("Date début")
    date_to = fields.Date("Date Fin")
    appareil_id = fields.Many2one(
        "product.template", "Appareil", domain=[("type", "=", "colmatage")]
    )
    nature_id = fields.Many2one("product.colmatage.nature", "Nature Fuite")
    reparation_id = fields.Many2one("product.colmatage.reparation", "Réparation")


class product_colmatage_nature(models.Model):

    _name = "product.colmatage.nature"
    _description = "Nature Fuite"

    name = fields.Char("Nature Fuite")


class product_colmatage_reparation(models.Model):

    _name = "product.colmatage.reparation"
    _description = "Reparation"

    name = fields.Char("Reparation")
