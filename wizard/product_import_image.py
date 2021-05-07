# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os.path

from odoo import _
from odoo import fields, models
from odoo import tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class product_template(models.Model):
    """
    A wizard to import product.
    """

    _name = "product.template"
    _inherit = "product.template"
    _description = "Product Template"

    wizard_id = fields.Many2one("product.wizard", "Wizard")


class product_wizard(models.Model):
    """
    A wizard to manage the creation/removal of portal users.
    """

    _name = "product.wizard"
    _description = "Product Import Image"

    product_ids = fields.One2many("product.template", "wizard_id", string="Users")
    # file_name = fields.Char('Nom du fichier',size=256)
    # file =  fields.Binary('Select *.csv', required=False,help="Select csv file.")

    def download_image(self, image_path):
        return tools.image_resize_image_big(
            open(image_path, "rb").read().encode("base64")
        )

    def write_file(self, data, filename):
        with open(filename, "wb") as f:
            f.write(data)

    def action_apply(self):
        self.import_image_appareil()
        self.import_image_piece()
        return {"type": "ir.actions.act_window_close"}

    def import_operation(self):
        product_obj = self.env["product.order.operation"]
        i = 0
        _logger.info(i)
        self._cr.execute(
            """select code_order,code_operation,code_piece,poids_matiere,coef_matiere,allotted_time,estimated_cost,
                        spent_time,real_cost,price,intervenant, mat_sal,id
                        from operation where download='f'"""
        )
        for res in self.env.cr.fetchall():
            i = i + 1
            _logger.info(i)
            code_order = res[0]
            code_operation = res[1]
            code_piece = res[2]
            poids_matiere = res[3]
            coef_matiere = res[4]
            allotted_time = res[5]
            estimated_cost = res[6]
            spent_time = res[7]
            real_cost = res[8]
            price = res[9]
            mat_sal = res[10]
            intervenant = res[11]
            operation_id = res[12]
            ################################################################################################
            product_obj.create(
                {
                    "code_order": code_order,
                    "code_operation": code_operation,
                    "code_piece": code_piece,
                    "poids_matiere": poids_matiere,
                    "coef_matiere": coef_matiere,
                    "allotted_time": allotted_time,
                    "estimated_cost": estimated_cost,
                    "spent_time": spent_time,
                    "real_cost": real_cost,
                    "price": price,
                    "intervenant": intervenant,
                    "mat_sal": mat_sal,
                }
            )
            self._cr.commit()
            self._cr.execute(
                "update operation set download='t' where id=" + str(operation_id)
            )
            self._cr.commit()
        return True

    def import_operation_(self):
        product_obj = self.env["product.order.operation"]
        for data in self.browse():
            lines = (data.file.decode("base64")).split("\n")
            extension = data.file_name.split(".")[1]
            if extension != "csv":
                raise ValidationError(
                    _("Seuls les fichiers CSV sont autorisés à être importés")
                )
            # ################################## import data ##################################################
            rownum = 0
            for line in lines[:-1]:
                if rownum == 0:
                    header = line.split(";")
                else:
                    code_order = (
                        code_operation
                    ) = code_piece = intervenant = mat_sal = ""
                    poids_matiere = (
                        coef_matiere
                    ) = (
                        allotted_time
                    ) = estimated_cost = spent_time = real_cost = price = 0
                    data = line.split(";")
                    i = 0
                    _logger.info(i)
                    while i < len(header):
                        if header[i] == "code_order":
                            code_order = data[i]
                        if header[i] == "code_operation":
                            code_operation = data[i]
                        if header[i] == "code_piece":
                            code_piece = data[i]
                        if header[i] == "allotted_time":
                            allotted_time = data[i]
                        if header[i] == "spent_time":
                            spent_time = data[i]
                        if header[i] == "poids_matiere":
                            poids_matiere = data[i]
                        if header[i] == "coef_matiere":
                            coef_matiere = data[i]
                        if header[i] == "estimated_cost":
                            estimated_cost = data[i]
                        if header[i] == "real_cost":
                            real_cost = data[i]
                        if header[i] == "price":
                            price = data[i]
                        if header[i] == "mat_sal":
                            mat_sal = data[i]
                        if header[i] == "mat_sal":
                            intervenant = data[i]
                        i += 1
                    ################################################################################################
                    product_obj.create(
                        {
                            "code_order": code_order,
                            "code_operation": code_operation,
                            "code_piece": code_piece,
                            "poids_matiere": poids_matiere,
                            "coef_matiere": coef_matiere,
                            "allotted_time": allotted_time,
                            "estimated_cost": estimated_cost,
                            "spent_time": spent_time,
                            "real_cost": real_cost,
                            "price": price,
                            "intervenant": intervenant,
                            "mat_sal": mat_sal,
                        }
                    )
                rownum += 1
        return True

    def import_image_appareil(self):
        self.env["product.piece"].update_order()
        return True

    def import_image_appareil__(self):
        results = self.env["product.image.directory"].search(
            [("type", "=", "appareil")]
        )
        for result in results:
            directory_appareil = result.name
        self._cr.execute(
            "select no_app from product_template where param1 is not null order by no_app"
        )
        for res in self.env.cr.fetchall():
            image_path = directory_appareil + str(res[0]) + ".png"
            _logger.info(image_path)
            if os.path.exists(image_path):
                template_ids = self.env["product.template"].search(
                    [("no_app", "=", res[0])]
                )
                if template_ids:
                    template_ids.write(
                        {"default_code": 1, "image": self.download_image(image_path)}
                    )
        return {"type": "ir.actions.act_window_close"}

    def import_image_piece(self):
        results = self.env["product.image.directory"].search([("type", "=", "piece")])
        for result in results:
            directory_piece = result.name
        self._cr.execute(
            "select code_piece from product_piece where param1 is not null order by code_piece"
        )
        for res in self.env.cr.fetchall():
            image_path = directory_piece + str(res[0]) + ".png"
            _logger.info(image_path)
            if os.path.exists(image_path):
                template_ids = self.env["product.piece"].search(
                    [("code_piece", "=", res[0])]
                )
                if template_ids:
                    template_ids.write(
                        {"default_code": 1, "image": self.download_image(image_path)}
                    )
        return {"type": "ir.actions.act_window_close"}


class product_image_directory(models.Model):
    _name = "product.image.directory"
    _description = "Product Image Directory"

    type = fields.Selection(
        [("appareil", "Appareil"), ("piece", "Pièce"), ("reporting", "Reporting")],
        string="Dossier",
    )
    name = fields.Char("URL")
