# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class hr_employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    document_ids = fields.One2many(
        "hr.employee.document", "employee_id", string="Documents", copy=True
    )


class hr_employee_document(models.Model):
    _name = "hr.employee.document"
    _description = "Documents"

    employee_id = fields.Many2one("hr.employee", "Employé")
    filename = fields.Char("Nom du fichier", size=256)
    file = fields.Binary("Fichier")
