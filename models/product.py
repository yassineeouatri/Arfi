# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    def _compute_piece_count(self):
        read_group_res = self.env["product.piece"].read_group(
            [("appareil_id", "in", self.ids)], ["appareil_id"], ["appareil_id"]
        )
        group_data = dict(
            (data["appareil_id"][0], data["appareil_id_count"])
            for data in read_group_res
        )
        for obj in self:
            obj.piece_count = group_data.get(obj.id, 0)

    def _compute_procedure_count(self):
        read_group_res = self.env["product.procedure"].read_group(
            [("appareil_id", "in", self.ids)], ["appareil_id"], ["appareil_id"]
        )
        group_data = dict(
            (data["appareil_id"][0], data["appareil_id_count"])
            for data in read_group_res
        )
        for obj in self:
            obj.procedure_count = group_data.get(obj.id, 0)

    def _compute_outillage_count(self):
        read_group_res = self.env["product.appareil.outillage"].read_group(
            [("appareil_id", "in", self.ids)], ["appareil_id"], ["appareil_id"]
        )
        group_data = dict(
            (data["appareil_id"][0], data["appareil_id_count"])
            for data in read_group_res
        )
        for obj in self:
            obj.outillage_count = group_data.get(obj.id, 0)

    no_app = fields.Char("N° Appareil")
    type = fields.Selection(
        [("appareil", "Appareil"), ("piece", "Pièce"), ("colmatage", "Colmatage")],
        "Type de produit",
        help="",
    )
    categ_id = fields.Many2one(
        "product.category",
        "Type Appareil",
        required=False,
        change_default=True,
        domain="[('type','=','type')]",
        help="",
    )
    ss_categ_id = fields.Many2one(
        "product.category",
        "Sous Type Appareil",
        required=False,
        domain="[('parent_id','=',categ_id),('type','=','ss_type')]",
        change_default=True,
        help="",
    )
    maker_id = fields.Many2one(
        "product.template.maker",
        "Fabriquant",
        required=False,
        change_default=True,
        help="",
    )
    param1 = fields.Char("Param1")
    #### Var Pieces
    no_piece = fields.Char("N° Pièce")
    reference_appareil = fields.Char("Référence Appareil")
    code_matiere = fields.Char("Code Matière")
    code_piece = fields.Char("Code Pièce")
    diam1 = fields.Char("Diam1")
    diam2 = fields.Char("Diam2")
    longueur = fields.Char("Longueur")
    largeur = fields.Char("Largeur")
    profond = fields.Char("Profond")
    poids = fields.Char("Poids")
    order_id = fields.Many2one("product.order", "Commande")
    parent_id = fields.Many2one(
        "product.template", "Appareil", select=True, ondelete="cascade"
    )
    material_id = fields.Many2one("product.product.material", "Matière")
    piece_ids = fields.One2many(
        "product.piece", "appareil_id", string="Pièces", copy=True
    )
    procedure_ids = fields.One2many(
        "product.procedure", "appareil_id", string="Procédures"
    )
    instruction_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Instructions de Maintenance",
        domain=[("type_file", "=", "ins")],
    )
    maitenance_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Manuel de Maintenance",
        domain=[("type_file", "=", "man")],
    )
    operatoire_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Mode Opératoire",
        domain=[("type_file", "=", "ope")],
    )
    original_ids = fields.One2many(
        "product.plan.original", "appareil_id", string="Plans Original"
    )
    codification_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Codification Appareil",
        domain=[("type_file", "=", "codif")],
    )
    specification_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Spécification Appareil",
        domain=[("type_file", "=", "spec")],
    )
    soudage_ids = fields.One2many(
        "product.procedure",
        "appareil_id",
        string="Mode Opératoire de Soudage",
        domain=[("type_file", "=", "mos")],
    )
    operation_ids = fields.One2many(
        "product.order.operation",
        "appareil_id",
        string="Opérations",
        domain=[("piece_id", "=", None), ("order_", "=", 1)],
    )
    outillage_ids = fields.One2many(
        "product.appareil.outillage", "appareil_id", string="Outillages"
    )
    outillage_tarage_ids = fields.One2many(
        "product.appareil.outillage.tarage", "appareil_id", string="Outillages Tarages"
    )
    price_ids = fields.One2many("product.appareil.price", "appareil_id", string="Prix")
    piece_count = fields.Integer(
        compute="_compute_piece_count",
        type="integer",
        string="# of Pieces",
        method=True,
    )
    procedure_count = fields.Integer(
        compute="_compute_procedure_count",
        type="integer",
        string="# of Procedures",
        method=True,
    )
    outillage_count = fields.Integer(
        compute="_compute_outillage_count",
        type="integer",
        string="# of Outillages",
        method=True,
    )
    ###########Calcul SMP
    clapet_ext = fields.Float("Clapet Exterieur")
    clapet_int = fields.Float("Clapet Interieur")
    buse_ext = fields.Float("Buse Exterieur")
    buse_int = fields.Float("Buse Interieur")
    ########### File colmatage
    colmatage_name = fields.Char("Nom du fichier", size=256)
    colmatage_file = fields.Binary("Fichier")

    _sql_constraints = [
        # ('name_uniq', 'unique (name)', "La référence de l'appareil est unique !"),
    ]

    @api.onchange(
        "clapet_ext", "clapet_int", "buse_ext", "buse_int"
    )  # if these fields are changed, call method
    def _onchange_diametre(self):
        if self.clapet_ext and self.clapet_int and self.buse_ext and self.buse_int:
            print(self.clapet_ext)
            print(self.buse_ext)
            min_ = min(self.clapet_ext, self.buse_ext)
            max_ = max(self.clapet_int, self.buse_int)
            section = round(
                (((min_ + max_) / 2) * (min_ + max_) / 2) * 3.14159 / 400, 2
            )
            self._cr.execute(
                """ UPDATE product_attribute_line a SET value='{0}'
                                  WHERE product_tmpl_id={1} AND attribute='{2}'""".format(
                    str(section) + " cm3", self._origin.id, "Section Moyenne Portées"
                )
            )

    def action_select_attribute(self):
        self._cr.execute("update product_attribute set create_variant='t'")
        self._cr.commit()
        for obj in self.attribute_line_ids:
            self._cr.execute(
                "update product_attribute set create_variant='f' where id="
                + str(obj.attribute_id.id)
            )
            self._cr.commit()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_template_information"
        )
        res["context"] = {"default_appareil_id": self.id}
        return res

    def action_select_operation(self):
        self._cr.execute("update product_operation set variant='t'")
        self._cr.commit()
        for obj in self.operation_ids:
            self._cr.execute(
                "update product_operation set variant='f' where id="
                + str(obj.operation_id.id)
            )
            self._cr.commit()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_appareil_order_operation_wizard"
        )
        res["context"] = {
            "default_appareil_id": self.id,
            "default_order_id": self.order_id.id,
        }

        return res

    def action_select_nature(self):
        self._cr.execute("update product_nature set variant='t'")
        self._cr.commit()
        for obj in self.price_ids:
            self._cr.execute(
                "update product_nature set variant='f' where id="
                + str(obj.nature_id.id)
            )
            self._cr.commit()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_template_nature"
        )
        res["context"] = {"default_appareil_id": self.id}

        return res

    def return_directory_id(self, name):
        rslt = None
        results = self.env["muk_dms.directory"].search([("name", "=", name)])
        for obj in results:
            rslt = obj.id
        return rslt

    def action_select_procedure_it(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.instruction_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_it_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id(
                    "Instructions de Travail"
                ),
                "default_type_file": "ins",
            },
            "target": "new",
        }

    def action_select_procedure_mm(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.maitenance_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_mm_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id(
                    "Manuel de Maintenance"
                ),
                "default_type_file": "man",
            },
            "target": "new",
        }

    def action_select_procedure_ope(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.operatoire_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_ope_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id("Mode Operatoire"),
                "default_type_file": "ope",
            },
            "target": "new",
        }

    def action_select_procedure_codif(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.codification_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_codif_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id("Codification"),
                "default_type_file": "codif",
            },
            "target": "new",
        }

    def action_select_procedure_spec(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.specification_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_spec_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id(
                    "Specification de qualite"
                ),
                "default_type_file": "spec",
            },
            "target": "new",
        }

    def action_select_procedure_mos(self):
        self._cr.execute("update muk_dms_file set variant='t'")
        self._cr.commit()
        for obj in self.soudage_ids:
            self._cr.execute(
                "update muk_dms_file set variant='f' where id=" + str(obj.file_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template.procedure",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("arfi.view_product_template_procedure_mos_form").id,
                    "form",
                )
            ],
            "context": {
                "default_appareil_id": self.id,
                "default_directory_id": self.return_directory_id(
                    "Mode Operatoire de Soudage"
                ),
                "default_type_file": "mos",
            },
            "target": "new",
        }

    def action_image(self):
        self._cr.execute(
            "select id from ir_attachment where res_id="
            + str(self.id)
            + " and res_model='product.template' and res_field='image'"
        )
        for res in self.env.cr.fetchall():
            file_id = res[0]
            if file_id:
                url = "/web/content/" + str(file_id)
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "new",
                }

    def action_edit(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (self.env.ref("arfi.product_template_appareil_form_view").id, "form")
            ],
        }

    def action_procedure(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref(
                        "arfi.product_template_appareil_procedure_create_form_view"
                    ).id,
                    "form",
                )
            ],
        }

    def action_outillage(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref(
                        "arfi.product_template_appareil_outillage_create_form_view"
                    ).id,
                    "form",
                )
            ],
        }

    def action_pps(self):

        if self.order_id.kks_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.kks",
                "view_mode": "form",
                "view_type": "form",
                "res_id": self.order_id.kks_id.id,
                "views": [
                    (
                        self.env.ref("arfi.product_kks_risque_create_view_form").id,
                        "form",
                    )
                ],
                "target": "new",
            }
        else:
            raise ValidationError(
                _("Attention! Cette commande n'est affectée à aucun appareil.")
            )

    @api.multi
    def print_product_template_cartouche(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_template_cartouche(data)

    def _print_product_template_cartouche(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_producttemplatecartouche", data=data
        )

    @api.multi
    def print_product_template_outillage(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_template_outillage(data)

    def _print_product_template_outillage(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_producttemplateoutillage", data=data
        )

    @api.multi
    def print_product_template_outillage_tarage(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_template_outillage_tarage(data)

    def _print_product_template_outillage_tarage(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_producttemplateoutillagetarage", data=data
        )

    @api.multi
    def copy(self, default=None):
        # TDE FIXME: should probably be copy_data
        self.ensure_one()
        if default is None:
            default = {}
        if "child_ids" not in default:
            default["child_ids"] = _("%s (copy)") % self.name

        return super(product_template, self).copy(default=default)


class product_piece(models.Model):
    _name = "product.piece"
    _order = "order_,appareil_id,no_piece"

    def _compute_procedure_count(self):
        read_group_res = self.env["product.procedure"].read_group(
            [("piece_id", "in", self.ids)], ["piece_id"], ["piece_id"]
        )
        group_data = dict(
            (data["piece_id"][0], data["piece_id_count"]) for data in read_group_res
        )
        for obj in self:
            obj.procedure_count = group_data.get(obj.id, 0)

    def compute_order(self):
        import re

        for obj in self:
            if obj.no_piece:
                no_piece = obj.no_piece.replace("*", "")
                no_piece = no_piece.replace(" ", "")
                partition = no_piece.partition(".")
                _logger.info(no_piece)
                if no_piece.isdigit():
                    rslt = no_piece
                elif no_piece.count(".") == 1 and (
                    (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and partition[2].isdigit()
                    )
                    or (
                        partition[0] == ""
                        and partition[1] == "."
                        and partition[2].isdigit()
                    )
                    or (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and partition[2] == ""
                    )
                ):
                    rslt = float(no_piece)
                elif no_piece.count(".") == 1 and (
                    (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and not partition[2].isdigit()
                    )
                ):
                    rslt = float(partition[0])
                elif (
                    no_piece.count(".") == 2
                    and partition[0].isdigit()
                    and partition[1] == "."
                    and partition[2].isdigit()
                ):
                    rslt = float(str(partition[0]) + "." + str(partition[2]))
                elif (
                    no_piece.count(".") == 2
                    and partition[0].isdigit()
                    and partition[1] == "."
                    and not partition[2].isdigit()
                ):
                    rslt = float(str(partition[0]))
                elif (
                    no_piece.count(".") == 0
                    and not no_piece.isdigit()
                    and len(no_piece) == 2
                    and no_piece[:1].isdigit()
                    and not no_piece[-1:].isdigit()
                ):
                    rslt = float(no_piece[:1])
                elif (
                    len(no_piece) == 3
                    and no_piece[:2].isdigit()
                    and not no_piece[-1:].isdigit()
                ):
                    rslt = float(no_piece[:2])
                else:
                    rslt = -1

            else:
                rslt = 0
            _logger.info("rslt" + str(rslt))
            obj.update(
                {
                    "order_": rslt,
                }
            )

    def update_order(self):
        import re

        self._cr.execute("select id,no_piece from product_piece")
        for res in self.env.cr.fetchall():
            no_piece = res[1]
            if no_piece:
                no_piece = no_piece.replace("*", "")
                no_piece = no_piece.replace(" ", "")
                partition = no_piece.partition(".")
                _logger.info(no_piece)
                if no_piece.isdigit():
                    rslt = no_piece
                elif no_piece.count(".") == 1 and (
                    (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and partition[2].isdigit()
                    )
                    or (
                        partition[0] == ""
                        and partition[1] == "."
                        and partition[2].isdigit()
                    )
                    or (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and partition[2] == ""
                    )
                ):
                    rslt = float(no_piece)
                elif no_piece.count(".") == 1 and (
                    (
                        partition[0].isdigit()
                        and partition[1] == "."
                        and not partition[2].isdigit()
                    )
                ):
                    rslt = float(partition[0])
                elif (
                    no_piece.count(".") == 2
                    and partition[0].isdigit()
                    and partition[1] == "."
                    and partition[2].isdigit()
                ):
                    rslt = float(str(partition[0]) + "." + str(partition[2]))
                elif (
                    no_piece.count(".") == 2
                    and partition[0].isdigit()
                    and partition[1] == "."
                    and not partition[2].isdigit()
                ):
                    rslt = float(str(partition[0]))
                elif (
                    no_piece.count(".") == 0
                    and not no_piece.isdigit()
                    and len(no_piece) == 2
                    and no_piece[:1].isdigit()
                    and not no_piece[-1:].isdigit()
                ):
                    rslt = float(no_piece[:1])
                elif (
                    len(no_piece) == 3
                    and no_piece[:2].isdigit()
                    and not no_piece[-1:].isdigit()
                ):
                    rslt = float(no_piece[:2])
                else:
                    rslt = -1

            else:
                rslt = 0

            self._cr.execute(
                "update product_piece set order_="
                + str(rslt)
                + " where id="
                + str(res[0])
            )
            self._cr.commit()
        return True

    name = fields.Char("Pièce")
    no_piece = fields.Char("N° Pièce", required=True)
    reference_appareil = fields.Char("Référence Appareil")
    code_matiere = fields.Char("Code Matière")
    code_piece = fields.Char("Code Pièce")
    diam1 = fields.Char("Diam1")
    diam2 = fields.Char("Diam2")
    longueur = fields.Char("Longueur")
    largeur = fields.Char("Largeur")
    profond = fields.Char("Profond")
    poids = fields.Char("Poids")
    order_id = fields.Many2one("product.order", "Commande")
    appareil_id = fields.Many2one(
        "product.template", "Appareil", select=True, ondelete="cascade"
    )
    material_id = fields.Many2one("product.product.material", "Matière")
    operation_ids = fields.One2many(
        "product.order.operation",
        "piece_id",
        string="Opérations",
        domain=[("order_", "=", 1)],
    )
    procedure_ids = fields.One2many(
        "product.procedure", "piece_id", string="Procédures"
    )
    instruction_ids = fields.One2many(
        "product.procedure",
        "piece_id",
        string="Instructions de Maintenance",
        domain=[("type_file", "=", "ins")],
    )
    maitenance_ids = fields.One2many(
        "product.procedure",
        "piece_id",
        string="Manuel de Maintenance",
        domain=[("type_file", "=", "man")],
    )
    operatoire_ids = fields.One2many(
        "product.procedure",
        "piece_id",
        string="Mode Opératoire",
        domain=[("type_file", "=", "ope")],
    )
    param1 = fields.Char("Param1")
    download_image = fields.Boolean("Image téléchargée", default=False)
    order_ = fields.Float(
        compute="compute_order",
        String="Name",
        readonly=False,
        store=True,
    )
    procedure_count = fields.Integer(
        compute="_compute_procedure_count",
        type="integer",
        string="# of Procedures",
        method=True,
    )
    # reference_ids = fields.Many2many(related='material_id.reference_ids', store=False)

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image",
        attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.",
    )
    image_medium = fields.Binary(
        "Medium-sized image",
        attachment=True,
        help="Medium-sized image of the product. It is automatically "
        "resized as a 128x128px image, with aspect ratio preserved, "
        "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.",
    )
    image_small = fields.Binary(
        "Small-sized image",
        attachment=True,
        help="Small-sized image of the product. It is automatically "
        "resized as a 64x64px image, with aspect ratio preserved. "
        "Use this field anywhere a small image is required.",
    )
    photo_name = fields.Char("Nom du fichier", size=256)
    photo = fields.Binary("Image")
    photo_name_after = fields.Char("Nom du fichier", size=256)
    photo_after = fields.Binary("Image")
    degat_id = fields.Many2one("product.degat", "Nature de dégâts")
    etat_id = fields.Many2one("product.etat", "Etat")
    tof_name = fields.Char("Nom du fichier", size=256)
    tof = fields.Binary("Image")
    variant = fields.Boolean("Variant", default=True)
    has_plan = fields.Boolean("Plan", default=False)

    @api.multi
    def name_get(self):
        import sys

        reload(sys)
        sys.setdefaultencoding("utf-8")
        if not len(self.ids):
            return []
        resuhh = []
        for record in self:
            resuhh.append((record.id, str(record.no_piece) + " - " + str(record.name)))
        return resuhh

    def action_delete(self):

        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_piece_delete_wizard"
        )
        res["context"] = {"default_piece_id": self.id}

        return res

    def action_image(self):
        self._cr.execute(
            "select id from ir_attachment where res_id="
            + str(self.id)
            + " and res_model='product.piece' and res_field='image'"
        )
        for res in self.env.cr.fetchall():
            file_id = res[0]
            if file_id:
                url = "/web/content/" + str(file_id)
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "new",
                }

    def action_select_operation(self):
        self._cr.execute("update product_operation set variant='t'")
        self._cr.commit()
        for obj in self.operation_ids:
            self._cr.execute(
                "update product_operation set variant='f' where id="
                + str(obj.operation_id.id)
            )
            self._cr.commit()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_piece_order_operation_wizard"
        )
        res["context"] = {
            "default_piece_id": self.id,
            "default_appareil_id": self.appareil_id.id,
            "default_order_id": self.order_id.id,
        }

        return res

    def action_material(self):
        self._cr.execute("select id from product_product_material_search")
        for res in self.env.cr.fetchall():
            obj_id = res[0]
        self._cr.execute(
            "update product_product_material_search set material_id=Null,designation='',norme_id=Null,reference_id=Null,\
                        piece_id="
            + str(self.id)
        )
        self._cr.commit()
        self._cr.execute(
            "update product_product_material_reference set material_search_id=Null"
        )
        self._cr.commit()
        if self.material_id:
            designation = ""
            if self.material_id.designation:
                designation = self.material_id.designation
            self._cr.execute(
                "update product_product_material_search set material_id="
                + str(self.material_id.id)
                + ",designation='"
                + designation
                + "'"
            )
            self._cr.commit()

            self._cr.execute(
                "update product_product_material_reference set material_search_id="
                + str(obj_id)
                + "\
                            where material_id="
                + str(self.material_id.id)
            )
            self._cr.commit()

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.product.material.search",
            "view_mode": "form",
            "view_type": "form",
            "res_id": obj_id,
            "target": "new",
            "views": [
                (
                    self.env.ref("arfi.product_product_material_search_form_view").id,
                    "form",
                )
            ],
        }

    def action_material_readonly(self):
        self._cr.execute("select id from product_product_material_search")
        for res in self.env.cr.fetchall():
            obj_id = res[0]
        self._cr.execute(
            "update product_product_material_search set material_id=Null,designation='',norme_id=Null,reference_id=Null,\
                        piece_id="
            + str(self.id)
        )
        self._cr.commit()
        self._cr.execute(
            "update product_product_material_reference set material_search_id=Null"
        )
        self._cr.commit()
        if self.material_id:
            designation = ""
            if self.material_id.designation:
                designation = self.material_id.designation
            self._cr.execute(
                "update product_product_material_search set material_id="
                + str(self.material_id.id)
                + ",designation='"
                + designation
                + "'"
            )
            self._cr.commit()

            self._cr.execute(
                "update product_product_material_reference set material_search_id="
                + str(obj_id)
                + "\
                            where material_id="
                + str(self.material_id.id)
            )
            self._cr.commit()

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.product.material.search",
            "view_mode": "form",
            "view_type": "form",
            "res_id": obj_id,
            "target": "new",
            "views": [
                (
                    self.env.ref(
                        "arfi.product_product_material_search_readonly_form_view"
                    ).id,
                    "form",
                )
            ],
        }

    def action_piece(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.piece",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(self.env.ref("arfi.product_piece_form_view").id, "form")],
        }

    def action_piece_order(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.piece",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(self.env.ref("arfi.product_order_piece_form_view").id, "form")],
        }

    def action_procedure(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.piece",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref("arfi.product_piece_procedure_create_form_view").id,
                    "form",
                )
            ],
            "target": "new",
        }

    def return_order(self, no_piece):
        if no_piece:
            no_piece = no_piece.replace("*", "")
            no_piece = no_piece.replace(" ", "")
            partition = no_piece.partition(".")
            _logger.info(no_piece)
            if no_piece.isdigit():
                rslt = no_piece
            elif no_piece.count(".") == 1 and (
                (
                    partition[0].isdigit()
                    and partition[1] == "."
                    and partition[2].isdigit()
                )
                or (
                    partition[0] == ""
                    and partition[1] == "."
                    and partition[2].isdigit()
                )
                or (
                    partition[0].isdigit()
                    and partition[1] == "."
                    and partition[2] == ""
                )
            ):
                rslt = float(no_piece)
            elif no_piece.count(".") == 1 and (
                (
                    partition[0].isdigit()
                    and partition[1] == "."
                    and not partition[2].isdigit()
                )
            ):
                rslt = float(partition[0])
            elif (
                no_piece.count(".") == 2
                and partition[0].isdigit()
                and partition[1] == "."
                and partition[2].isdigit()
            ):
                rslt = float(str(partition[0]) + "." + str(partition[2]))
            elif (
                no_piece.count(".") == 2
                and partition[0].isdigit()
                and partition[1] == "."
                and not partition[2].isdigit()
            ):
                rslt = float(str(partition[0]))
            elif (
                no_piece.count(".") == 0
                and not no_piece.isdigit()
                and len(no_piece) == 2
                and no_piece[:1].isdigit()
                and not no_piece[-1:].isdigit()
            ):
                rslt = float(no_piece[:1])
            elif (
                len(no_piece) == 3
                and no_piece[:2].isdigit()
                and not no_piece[-1:].isdigit()
            ):
                rslt = float(no_piece[:2])
            else:
                rslt = -1

        else:
            rslt = 0
        return rslt

    @api.model
    def create(self, vals):
        """Store the initial standard price in order to be able to retrieve the cost of a product template for a given date"""
        # TDE FIXME: context brol
        tools.image_resize_images(vals)
        if vals["no_piece"]:
            vals["order_"] = self.return_order(vals["no_piece"])
        template = super(product_piece, self).create(vals)
        return template

    @api.onchange("no_piece")  # if these fields are changed, call method
    def check_change(self):
        self.order_ = self.return_order(self.no_piece)

    @api.onchange("image")  # if these fields are changed, call method
    def update_has_plan(self):
        if self.image:
            rslt = True
        else:
            rslt = False
        self.has_plan = rslt

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(product_piece, self).write(vals)
        return res


class product_category(models.Model):
    _inherit = "product.category"
    _order = "complete_name"

    @api.multi
    def name_get(self):

        res = super(product_category, self).name_get()
        data = []
        for obj in self:
            display_value = ""
            display_value += obj.description or ""
            data.append((obj.id, display_value))
        return data

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + [("description", "ilike", name)]), limit=limit)
            if recs:
                return recs.name_get()
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()

    type = fields.Selection(
        [("type", "Type"), ("ss_type", "Sous Type")], "Type", default="type", help=""
    )
    description = fields.Char("Déscription")
    ss_categ_attribute_ids = fields.Many2many(
        "product.attribute",
        "ss_categ_attribute_rel",
        "ss_categ_id",
        "attribute_id",
        "Informations Techniques",
    )
    complete_name = fields.Char(
        compute="complete_name_get",
        String="Name",
        readonly=True,
        store=True,
    )


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"
    _order = "attribute_sequence"

    value = fields.Char("Valeur")
    reference = fields.Char("Réference Appareil")
    attribute_sequence = fields.Integer(related="attribute_id.sequence", store=True)
    attribute = fields.Char(related="attribute_id.name", store=True)

    def action_delete(self):

        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_attribute_delete_wizard"
        )
        res["context"] = {"default_attribute_line_id": self.id}
        return res

    def action_smp(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_id": self.product_tmpl_id.id,
            "views": [
                (
                    self.env.ref(
                        "arfi.product_template_appareil_smp_create_form_view"
                    ).id,
                    "form",
                )
            ],
        }

    @api.onchange("product_tmpl_id")  # if these fields are changed, call method
    def check_change(self):
        self.reference = self.product_tmpl_id.name

    _sql_constraints = [
        (
            "name_uniq",
            "unique (product_tmpl_id,attribute_id)",
            "Attention! Enregistrement unique",
        ),
    ]


class product_appareil_outillage(models.Model):
    _name = "product.appareil.outillage"

    appareil_id = fields.Many2one("product.template", "Appareil")
    outillage_id = fields.Many2one("product.outillage", "Outillage")
    code = fields.Char(
        related="outillage_id.code", string="Code", store=True, readonly=True
    )
    reference = fields.Char("Réference")
    qte = fields.Integer("Qte Demandée")

    @api.onchange("appareil_id")
    def _onchange_appareil(self):
        self.reference = self.appareil_id.name


class product_appareil_outillage_tarage(models.Model):
    _name = "product.appareil.outillage.tarage"

    appareil_id = fields.Many2one("product.template", "Appareil")
    outillage_id = fields.Many2one("product.outillage", "Outillage")
    code = fields.Char(
        related="outillage_id.code", string="Code", store=True, readonly=True
    )
    reference = fields.Char("Réference")
    qte = fields.Integer("Qte Demandée")

    @api.onchange("appareil_id")
    def _onchange_appareil(self):
        self.reference = self.appareil_id.name


class product_appareil_price(models.Model):
    _name = "product.appareil.price"

    appareil_id = fields.Many2one("product.template", "Appareil")
    nature_id = fields.Many2one("product.nature", "Action")
    purchase_price = fields.Float("Prix d'achat")
    sale_price = fields.Float("Prix de vente")

    @api.onchange("sale_price")  # if these fields are changed, call method
    def _onchange_sale_price(self):
        if self.appareil_id:
            self._cr.execute(
                """ UPDATE product_kks_tarif a SET montant={0} 
                              FROM product_template b WHERE a.appareil_id=b.id
                              AND  b.name='{1}' AND nature_id={2}""".format(
                    self.sale_price, self.appareil_id.name, self.nature_id.id
                )
            )

    @api.onchange("purchase_price")  # if these fields are changed, call method
    def _onchange_purchase_price(self):
        if self.appareil_id:
            self._cr.execute(
                """ UPDATE product_kks_tarif a SET montant2={0} 
                                          FROM product_template b WHERE a.appareil_id=b.id
                                          AND  b.name='{1}' AND nature_id={2}""".format(
                    self.purchase_price, self.appareil_id.name, self.nature_id.id
                )
            )
