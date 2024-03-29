# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class product_template_procedure(models.Model):

    _name = "product.template.procedure"
    _description = "Product Template Procedure"

    appareil_id = fields.Many2one(
        "product.template", "Appareil", domain=[]
    )
    directory_id = fields.Many2one(
        "muk_dms.directory", string="Directory", required=False
    )
    type_file = fields.Selection(
        [
            ("ins", "Instruction de travail"),
            ("ope", "Mode Opératoire"),
            ("man", "Manuel de Maintenance"),
            ("codif", "Codification"),
            ("spec", "Spécification de Qualité"),
            ("mos", "Mode Opératoire de Soudage"),
        ],
        "Type du fichier",
        required=False,
    )
    procedure_ids = fields.Many2many(
        "muk_dms.file",
        "rel_template_procedure",
        "file_id",
        "appareil_id",
        "Procédures",
    )

    def action_procedure_it_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )

    def action_procedure_mm_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )

    def action_procedure_ope_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )

    def action_procedure_codif_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )

    def action_procedure_spec_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )

    def action_procedure_mos_execute(self):
        for obj in self.procedure_ids:
            self.env["product.procedure"].create(
                {
                    "product_tmpl_id": self.appareil_id.id,
                    "directory_id": self.directory_id.id,
                    "type_file": self.type_file,
                    "file_id": obj.id,
                }
            )
