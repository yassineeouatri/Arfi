# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class product_order(models.Model):

    _name = "product.order"
    _description = "Commandes"
    _inherit = ["ir.needaction_mixin"]
    _order = "date_order desc"
    _rec_name = "kks_id"

    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute(
            """select max(cast(no_arfi as numeric))+1 from product_order
                    where no_arfi ~ '^[0-9\.]+$'
                    and length(no_arfi)=5"""
        )
        rslt = cr.fetchone()[0]
        return rslt

    def convert_float_hour(self, x):
        return time.strftime("%H:%M", time.gmtime(x))

    def _compute_piece_count(self):
        read_group_res = self.env["product.order.operation"].read_group(
            [("order_id", "in", self.ids)], ["order_id"], ["order_id"]
        )
        group_data = dict(
            (data["order_id"][0], data["order_id_count"]) for data in read_group_res
        )
        for obj in self:
            obj.operation_count = group_data.get(obj.id, 0)

    @api.depends("operation_appareil_ids.real_cost", "operation_piece_ids.real_cost")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            allotted_time = estimated_cost = spent_time = real_cost = price = 0.0
            allotted_time_operation = (
                estimated_cost_operation
            ) = spent_time_operation = real_cost_operation = price_operation = 0.0
            allotted_time_piece = (
                estimated_cost_piece
            ) = spent_time_piece = real_cost_piece = price_piece = 0.0
            for line in order.operation_appareil_ids:
                allotted_time += line.allotted_time
                estimated_cost += line.estimated_cost
                spent_time += line.spent_time
                real_cost += line.real_cost
                price += line.price
                allotted_time_operation += line.allotted_time
                estimated_cost_operation += line.estimated_cost
                spent_time_operation += line.spent_time
                real_cost_operation += line.real_cost
                price_operation += line.price
            for line in order.operation_piece_ids:
                allotted_time += line.allotted_time
                estimated_cost += line.estimated_cost
                spent_time += line.spent_time
                real_cost += line.real_cost
                price += line.price
                allotted_time_piece += line.allotted_time
                estimated_cost_piece += line.estimated_cost
                spent_time_piece += line.spent_time
                real_cost_piece += line.real_cost
                price_piece += line.price
            order.update(
                {
                    "allotted_time_total": allotted_time,
                    "estimated_cost_total": estimated_cost,
                    "spent_time_total": spent_time,
                    "real_cost_total": real_cost,
                    "price_total": price,
                    "allotted_time_operation_total": allotted_time_operation,
                    "estimated_cost_operation_total": estimated_cost_operation,
                    "spent_time_operation_total": spent_time_operation,
                    "real_cost_operation_total": real_cost_operation,
                    "price_operation_total": price_operation,
                    "allotted_time_piece_total": allotted_time_piece,
                    "estimated_cost_piece_total": estimated_cost_piece,
                    "spent_time_piece_total": spent_time_piece,
                    "real_cost_piece_total": real_cost_piece,
                    "price_piece_total": price_piece,
                    "marge_total": price - real_cost,
                }
            )

    name = fields.Char(
        "Nom",
        required=True,
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
        default=lambda self: _("/"),
    )
    type = fields.Selection(
        [
            ("Colmatage", "Colmatage"),
            ("Remise en etat (REE)", "Remise en état (REE)"),
        ],
        "Type",
    )
    code_order = fields.Char("Code commande")
    no_order = fields.Char("N° commande", required=True)
    date_order = fields.Date("Date commande", required=False)
    no_arfi = fields.Char("N° ARFI", default="*")
    customer_id = fields.Many2one(
        "res.partner", "Client", domain=[("customer", "=", True)]
    )
    place_id = fields.Many2one(
        "res.partner.place",
        "Lieu",
        domain="[('partner_id','=',customer_id)]",
        change_default=True,
        help="",
    )
    maker_id = fields.Many2one("product.template.maker", "Fabriquant")
    type_appareil_id = fields.Many2one(
        "product.category", "Type Appareil", domain=[("type", "=", "type")]
    )
    ss_type_appareil_id = fields.Many2one(
        "product.category",
        "Sous Type Appareil",
        required=False,
        domain="[('parent_id','=',type_appareil_id),('type','=','ss_type')]",
        change_default=True,
        help="",
    )
    appareil_id = fields.Many2one(
        "product.template", "Appareil", domain=[]
    )
    kks_id = fields.Many2one("product.kks", "KKS")
    reference_appareil = fields.Char("Référence")
    no_interne = fields.Char("N° Interne")
    no_serie = fields.Char("No Série")
    obs_devis = fields.Text("Observation Devis")
    obs_recap = fields.Text("Observation Récap")
    obs_atelier = fields.Text("Observation Atelier")
    essai_date = fields.Date("Date")
    essai_org = fields.Many2one(
        "product.essai.organisme", "Organisme", domain=[("type", "=", "organisme")]
    )
    essai_nom = fields.Many2one(
        "product.essai.organisme", "Nom", domain=[("type", "=", "person")]
    )
    essai_choix = fields.Integer("Essai Choix")
    essai_file = fields.Binary("Certificat")
    essai_file_name = fields.Char("Fichiers")
    essai_ = fields.Selection(
        [("soupape", "Soupape"), ("vanne", "Vanne"), ("vide", "Vide")],
        "Information tarage & épreuve",
    )
    essai_satisfaisant = fields.Boolean("Essai Satisfaisant")
    date_next_ctr = fields.Date("Date prochain control")
    date_next_retar = fields.Date("Date prochain retarage")
    service_ids = fields.One2many(
        "product.order.service", "order_id", "Services", copy=True
    )
    test_ids = fields.One2many(
        "product.order.test", "order_id", "Test et contrôles", copy=True
    )
    operation_appareil_ids = fields.One2many(
        "product.order.operation",
        "order_id",
        "Opérations",
        domain=[("piece_id", "=", None)],
        copy=True,
    )
    operation_piece_ids = fields.One2many(
        "product.order.operation",
        "order_id",
        "Opérations",
        domain=[("piece_id", "!=", None)],
        copy=True,
    )
    operation_piece_image_ids = fields.One2many(
        "product.order.piece.image", "order_id", "Images des pièces"
    )
    operation_appareil_image_ids = fields.One2many(
        "product.order.appareil.image", "order_id", "Images des pièces"
    )
    state = fields.Selection(
        [("new", "Nouvelle"), ("confirmed", "Confirmée"), ("cancelled", "Annulée")],
        default="new",
    )
    nbr = fields.Integer("Nbr", default=1)

    allotted_time_total = fields.Float(
        compute="_amount_all", string="Temps Alloué", method=True
    )
    estimated_cost_total = fields.Float(
        compute="_amount_all", string="Coût Estimatif", method=True
    )
    spent_time_total = fields.Float(
        compute="_amount_all", string="Temps Passé", method=True
    )
    real_cost_total = fields.Float(
        compute="_amount_all", string="Coût réel", method=True
    )
    price_total = fields.Float(compute="_amount_all", string="Prix", method=True)
    allotted_time_operation_total = fields.Float(
        compute="_amount_all", string="Temps Alloué", method=True
    )
    estimated_cost_operation_total = fields.Float(
        compute="_amount_all", string="Coût Estimatif", method=True
    )
    spent_time_operation_total = fields.Float(
        compute="_amount_all", string="Temps Passé", method=True
    )
    real_cost_operation_total = fields.Float(
        compute="_amount_all", string="Coût réel", method=True
    )
    price_operation_total = fields.Float(
        compute="_amount_all", string="Prix", method=True
    )
    allotted_time_piece_total = fields.Float(
        compute="_amount_all", string="Temps Alloué", method=True
    )
    estimated_cost_piece_total = fields.Float(
        compute="_amount_all", string="Coût Estimatif", method=True
    )
    spent_time_piece_total = fields.Float(
        compute="_amount_all", string="Temps Passé", method=True
    )
    real_cost_piece_total = fields.Float(
        compute="_amount_all", string="Coût réel", method=True
    )
    price_piece_total = fields.Float(compute="_amount_all", string="Prix", method=True)
    marge_total = fields.Float(compute="_amount_all", string="Marge", method=True)
    operation_count = fields.Integer(
        compute="_compute_piece_count",
        type="integer",
        string="# of operation",
        method=True,
    )
    print_expertise = fields.Boolean("Imprimer Temps passé/Intervenant?", default=False)
    note_expertise = fields.Text("Note")

    @api.multi
    def name_get(self):
        import sys

        reload(sys)
        sys.setdefaultencoding("utf-8")
        if not len(self.ids):
            return []
        resuhh = []
        for record in self:
            resuhh.append(
                (record.id, str(record.no_order) + " - " + str(record.kks_id.name))
            )
        return resuhh

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + [("no_order", "ilike", name)]), limit=limit)
            if recs:
                return recs.name_get()
        if not recs:
            recs = self.search([("kks_id.name", operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def copy(self, default=None):
        # TDE FIXME: should probably be copy_data
        self.ensure_one()
        if default is None:
            default = {}
        if "child_ids" not in default:
            # default['no_serie'] = self.no_serie+'(copie)'
            default["no_order"] = self.no_order + "(copie)"
            # default['no_arfi']  = self.no_arfi +'(copie)'
        id = super(product_order, self).copy(default=default)
        new_id = id.id
        _logger.info(
            "update product_order_operation set real_cost=0,price=0,spent_time=0,intervenant='' where order_id="
            + str(new_id)
        )
        self._cr.execute(
            "update product_order_operation set real_cost=0,price=0,spent_time=0,intervenant='' where order_id="
            + str(new_id)
        )
        # self._cr.execute("delete from product_order_operation  where order_id="+str(new_id)+" and piece_id is not null")
        return id

    @api.multi
    def print_product_order_operation(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_order_operation(data)

    def _print_product_order_operation(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_productorderoperation", data=data
        )

    @api.multi
    def print_product_order_operation_empty(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_order_operation_empty(data)

    def _print_product_order_operation_empty(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_productorderoperationempty", data=data
        )

    @api.multi
    def print_product_order_devis(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_order_devis(data)

    def _print_product_order_devis(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_productorderdevis", data=data
        )

    @api.multi
    def print_product_order_rapport(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self._print_product_order_rapport(data)

    def _print_product_order_rapport(self, data):
        data["form"].update(self.read(["id"])[0])
        return self.env["report"].get_action(
            self, "arfi.action_report_productorderrapport", data=data
        )

    @api.multi
    def action_appareil(self):
        user = self.env.user
        group_hr_atelier = self.env.ref("arfi.group_arfi_atelier")
        if group_hr_atelier in user.groups_id:
            if self.appareil_id:
                appareils = self.env["product.template"].search(
                    [("id", "=", self.appareil_id.id)]
                )
                action = {
                    "type": "ir.actions.act_window",
                    "res_model": "product.template",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": self.appareil_id.id,
                    "views": [
                        (
                            self.env.ref(
                                "arfi.product_order_appareil_create_view_form"
                            ).id,
                            "form",
                        )
                    ],
                }

                return action
            raise ValidationError(
                _("Attention! Cette commande n'est affectée à aucun appareil.")
            )
        else:
            if self.appareil_id:
                appareils = self.env["product.template"].search(
                    [("id", "=", self.appareil_id.id)]
                )
                if appareils:
                    appareils.write({"order_id": self.id})
                pieces = self.env["product.piece"].search(
                    [("appareil_id", "=", self.appareil_id.id)]
                )
                if pieces:
                    pieces.write({"order_id": self.id})
                operation = self.env["product.order.operation"].search(
                    [("appareil_id", "=", self.appareil_id.id)]
                )
                if operation:
                    operation.write({"order_": 0})
                operation = self.env["product.order.operation"].search(
                    [
                        ("appareil_id", "=", self.appareil_id.id),
                        ("order_id", "=", self.id),
                    ]
                )
                if operation:
                    operation.write({"order_": 1})

                action = {
                    "type": "ir.actions.act_window",
                    "res_model": "product.template",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": self.appareil_id.id,
                    "views": [
                        (
                            self.env.ref(
                                "arfi.product_order_appareil_create_view_form"
                            ).id,
                            "form",
                        )
                    ],
                }

                return action
            raise ValidationError(
                _("Attention! Cette commande n'est affectée à aucun appareil.")
            )

    @api.multi
    def action_kks(self):
        user = self.env.user
        group_hr_atelier = self.env.ref("arfi.group_arfi_atelier")
        if group_hr_atelier in user.groups_id:
            if self.kks_id:
                kks = self.env["product.kks"].search([("id", "=", self.kks_id.id)])
                action = {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": self.kks_id.id,
                    "views": [(self.env.ref("arfi.product_kks_view_form").id, "form")],
                }

                return action
            raise ValidationError(
                _("Attention! Cette commande n'est affecté à aucun KKS.")
            )
        else:
            if self.kks_id:
                kks = self.env["product.kks"].search([("id", "=", self.kks_id.id)])
                if kks:
                    kks.write({"order_id": self.id})
                action = {
                    "type": "ir.actions.act_window",
                    "res_model": "product.kks",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": self.kks_id.id,
                    "views": [(self.env.ref("arfi.product_kks_view_form").id, "form")],
                }

                return action
            raise ValidationError(
                _("Attention! Cette commande n'est affecté à aucun KKS.")
            )

    @api.multi
    def action_pid(self):
        if self.kks_id:
            return self.env["product.kks.pid.annotation"].action_open_annotation(
                self.kks_id.name
            )
        raise ValidationError(_("Attention! Cette commande n'est affecté à aucun KKS."))

    def action_realisation(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref("arfi.product_order_operation_create_view_form").id,
                    "form",
                )
            ],
            # 'target': 'new',
            "flags": {"form": {"action_buttons": True}},
        }

    def action_expertise(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref("arfi.product_order_expertise_create_view_form").id,
                    "form",
                )
            ],
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }

    def action_observation(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref("arfi.product_order_observation_create_view_form").id,
                    "form",
                )
            ],
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }

    def action_certificate(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref("arfi.product_order_certificate_create_view_form").id,
                    "form",
                )
            ],
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }

    def action_select_service(self):
        self._cr.execute("update product_mesure_service set variant='t'")
        self._cr.commit()
        for obj in self.service_ids:
            self._cr.execute(
                "update product_mesure_service set variant='f' where id="
                + str(obj.service_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order.service.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (self.env.ref("arfi.view_product_order_service_wizard_form").id, "form")
            ],
            "context": {"default_order_id": self.id},
            "target": "new",
        }

    def action_select_test(self):
        self._cr.execute("update product_mesure_test set variant='t'")
        self._cr.commit()
        for obj in self.test_ids:
            self._cr.execute(
                "update product_mesure_test set variant='f' where id="
                + str(obj.test_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.order.test.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (self.env.ref("arfi.view_product_order_test_wizard_form").id, "form")
            ],
            "context": {"default_order_id": self.id},
            "target": "new",
        }

    @api.onchange("appareil_id")
    def _onchange_appareil(self):
        self.type_appareil_id = self.appareil_id.categ_id.id
        self.ss_type_appareil_id = self.appareil_id.ss_categ_id.id
        self.maker_id = self.appareil_id.maker_id.id
        self.reference_appareil = self.appareil_id.name
        if self.appareil_id and self._origin:
            self._cr.execute(
                "update product_order_operation set appareil_id="
                + str(self.appareil_id.id)
                + "  where order_id="
                + str(self._origin.id)
            )
            self._cr.commit()

    @api.onchange("kks_id")
    def _onchange_kks(self):
        if self.kks_id:
            if self.kks_id.reference != self.reference_appareil:
                raise ValidationError(
                    _(
                        "Attention! La référence du KKS ne correspond pas à la référence de la commande."
                    )
                )

    @api.constrains("kks_id")
    def _check_kks(self):
        for record in self:
            if record.kks_id:
                if record.kks_id.reference != record.reference_appareil:
                    raise ValidationError(
                        _(
                            "Attention! La référence du KKS ne correspond pas à la référence de la commande."
                        )
                    )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            if "company_id" in vals:
                vals["name"] = self.env["ir.sequence"].with_context(
                    force_company=vals["company_id"]
                ).next_by_code("product.order") or _("/")
            else:
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "product.order"
                ) or _("/")

        result = super(product_order, self).create(vals)
        return result


class product_order_piece_image(models.Model):

    _name = "product.order.piece.image"
    _description = "Images des commandes des pieces"

    order_id = fields.Many2one("product.order", "Commande")
    piece_id = fields.Many2one("product.piece", "Pièce")
    photo_name = fields.Char("Nom du fichier", size=256)
    photo = fields.Binary("Image")
    photo_name_after = fields.Char("Nom du fichier", size=256)
    photo_after = fields.Binary("Image")
    degat_id = fields.Many2one("product.degat", "Nature de dégâts")
    etat_id = fields.Many2one("product.etat", "Etat")

    _sql_constraints = [
        ("name_uniq", "unique (order_id,piece_id)", "Attention! Enregistrement unique"),
    ]


class product_order_appareil_image(models.Model):

    _name = "product.order.appareil.image"
    _description = "Images des commandes des appareils"

    order_id = fields.Many2one("product.order", "Commande")
    appareil_id = fields.Many2one(
        "product.template", "Appareil", domain=[]
    )
    photo_name = fields.Char("Nom du fichier", size=256)
    photo = fields.Binary("Image")
    photo_name_after = fields.Char("Nom du fichier", size=256)
    photo_after = fields.Binary("Image")

    _sql_constraints = [
        (
            "name_uniq",
            "unique (order_id,appareil_id)",
            "Attention! Enregistrement unique",
        ),
    ]


class product_order_service(models.Model):

    _name = "product.order.service"
    _description = "Conditions de services"

    order_id = fields.Many2one("product.order", "Commande")
    code_order = fields.Char("Code Commande")
    service_id = fields.Many2one("product.mesure.service", "Conditions service")
    value = fields.Char("Valeur")

    def action_delete(self):
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_order_service_delete_wizard"
        )
        res["context"] = {"default_order_service_id": self.id}
        return res

    _sql_constraints = [
        (
            "name_uniq",
            "unique (order_id,service_id)",
            "Attention! Enregistrement unique",
        ),
    ]


class product_order_test(models.Model):

    _name = "product.order.test"
    _description = "Test et controles"

    order_id = fields.Many2one("product.order", "Commande")
    code_order = fields.Char("Code Commande")
    test_id = fields.Many2one("product.mesure.test", "Test")
    value = fields.Char("Valeur")

    def action_delete(self):
        res = self.env["ir.actions.act_window"].for_xml_id(
            "arfi", "open_product_order_test_delete_wizard"
        )
        res["context"] = {"default_order_test_id": self.id}
        return res

    _sql_constraints = [
        ("name_uniq", "unique (order_id,test_id)", "Attention! Enregistrement unique"),
    ]


class product_order_operation(models.Model):

    _name = "product.order.operation"
    _description = "Commandes Operations"
    _order = "order_operation,operation_name"

    @api.depends("estimated_cost", "allotted_time", "spent_time", "price")
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.allotted_time == 0:
                rslt = 0
            else:
                rslt = (line.estimated_cost / line.allotted_time) * line.spent_time
            line.update({"marge": "%.2f" % (line.price - rslt)})

    @api.depends("estimated_cost", "allotted_time", "spent_time")
    def _compute_real_cost(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.allotted_time == 0:
                rslt = 0
            else:
                rslt = (line.estimated_cost / line.allotted_time) * line.spent_time
            line.update({"real_cost": "%.2f" % rslt})

    def _inverse_real_cost(self):
        return True

    order_id = fields.Many2one("product.order", "Commande", required=False)
    type = fields.Selection([("appareil", "Appareil"), ("piece", "Pièce")], "Type")
    operation_id = fields.Many2one("product.operation", "Opération", required=True)
    operation_name = fields.Char(related="operation_id.name", store=True)
    appareil_id = fields.Many2one(
        "product.template",
        "Appareil",
        domain=[],
        required=False,
    )
    piece_id = fields.Many2one("product.piece", "Pièce")
    order_operation = fields.Float(
        related="piece_id.order_", string="REP", store=True, readonly=True
    )
    code_order = fields.Char("Code Commande")
    code_operation = fields.Char("Code Opération")
    code_piece = fields.Char("Code Pièce")
    poids_matiere = fields.Float("Poids Matière")
    coef_matiere = fields.Float("Coef Matière")
    allotted_time = fields.Float("Temps Alloué")
    estimated_cost = fields.Float("Coût Estimatif")
    spent_time = fields.Float("Temps Passé")
    real_cost = fields.Float(
        compute="_compute_real_cost",
        inverse="_inverse_real_cost",
        string="Coût réel",
        readonly=False,
        store=True,
    )
    price = fields.Float("Prix")
    intervenant = fields.Char("Intervenant")
    order_ = fields.Integer("Order", default=0)
    mat_sal = fields.Char("Intervenant")
    marge = fields.Float(
        compute="_compute_amount", string="Marge", readonly=True, store=True
    )

    def open_piece(self):
        if self.piece_id:
            self._cr.execute(
                "select id from product_order_piece_image where order_id="
                + str(self.order_id.id)
                + " and piece_id="
                + str(self.piece_id.id)
            )
            for res in self.env.cr.fetchall():
                res_id = res[0]
            if res_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.order.piece.image",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": res_id,
                    "views": [
                        (
                            self.env.ref("arfi.product_order_piece_image_form_view").id,
                            "form",
                        )
                    ],
                    "target": "new",
                    "flags": {"form": {"action_buttons": True}},
                }

    def open_appareil(self):
        if self.appareil_id:
            self._cr.execute(
                "select id from product_order_appareil_image where order_id="
                + str(self.order_id.id)
                + " and appareil_id="
                + str(self.appareil_id.id)
            )
            for res in self.env.cr.fetchall():
                res_id = res[0]
            if res_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "product.order.appareil.image",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_id": res_id,
                    "views": [
                        (
                            self.env.ref(
                                "arfi.product_order_appareil_image_form_view"
                            ).id,
                            "form",
                        )
                    ],
                    "target": "new",
                    "flags": {"form": {"action_buttons": True}},
                }

    @api.model
    def create(self, vals):
        self._cr.execute(
            """insert into product_order_piece_image(order_id,piece_id)
                            select distinct order_id,piece_id from product_order_operation
                            where piece_id is not null
                            and concat(order_id,piece_id) not in
                            (select concat(order_id,piece_id) from product_order_piece_image);"""
        )
        self._cr.execute(
            """insert into product_order_appareil_image(order_id,appareil_id)
                            select distinct order_id,appareil_id from product_order_operation
                            where appareil_id is not null
                            and concat(order_id,appareil_id) not in
                            (select concat(order_id,appareil_id) from product_order_appareil_image);"""
        )
        result = super(product_order_operation, self).create(vals)
        self._cr.commit()
        return result

    @api.multi
    def write(self, vals):
        self._cr.execute(
            """insert into product_order_piece_image(order_id,piece_id)
                            select distinct order_id,piece_id from product_order_operation
                            where piece_id is not null
                            and concat(order_id,piece_id) not in
                            (select concat(order_id,piece_id) from product_order_piece_image);"""
        )
        self._cr.execute(
            """insert into product_order_appareil_image(order_id,appareil_id)
                            select distinct order_id,appareil_id from product_order_operation
                            where appareil_id is not null
                            and concat(order_id,appareil_id) not in
                            (select concat(order_id,appareil_id) from product_order_appareil_image);"""
        )
        self._cr.commit()
        tools.image_resize_images(vals)
        res = super(product_order_operation, self).write(vals)
        return res

    _sql_constraints = [
        (
            "name_uniq",
            "unique (order_id,operation_id)",
            "Attention! Enregistrement unique",
        ),
    ]


class operation(models.Model):
    _name = "operation"
    _description = "Operations"

    @api.depends("real_cost", "price")
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.update({"marge": line.price - line.real_cost})

    code_order = fields.Char("Code Commande")
    code_operation = fields.Char("Code Opération")
    code_piece = fields.Char("Code Pièce")
    poids_matiere = fields.Float("Poids Matière")
    coef_matiere = fields.Float("Coef Matière")
    allotted_time = fields.Float("Temps Alloué")
    estimated_cost = fields.Float("Coût Estimatif")
    spent_time = fields.Float("Temps Passé")
    real_cost = fields.Float("Coût réel")
    price = fields.Float("Prix")
    intervenant = fields.Char("Intervenant")
    mat_sal = fields.Char("Intervenant")
    marge = fields.Float(
        compute="_compute_amount", string="Marge", readonly=True, store=True
    )


class commande(models.Model):

    _name = "commande"
    _description = "Commandes"

    code_order = fields.Char("Code commande")
    no_order = fields.Char("N° commande")
    date_order = fields.Date("Date commande", required=False)
    code_client = fields.Char("Code Client")
    code_place = fields.Char("Code Place")
    maker = fields.Char("Fabriquant")
    type_appareil = fields.Char("Type Appareil")
    ss_type_appareil = fields.Char("Sous Type Appareil")
    reference_appareil = fields.Char("Référence")
    no_interne = fields.Char("N° Interne")
    no_serie = fields.Char("No Série")
    obs_devis = fields.Text("Observation Devis")
    obs_recap = fields.Text("Observation Récap")
    obs_atelier = fields.Text("Observation Atelier")
    essai_satisfaisant = fields.Boolean("Essai Satisfaisant")
    essai_org = fields.Char("Organisme")
    essai_nom = fields.Char("Nom")
    essai_date = fields.Date("Date")
    essai_choix = fields.Integer("Essai Choix")
    essai_file = fields.Binary("Fichier")
    essai_file_name = fields.Char("Fichiers")
    date_next_ctr = fields.Date("Date prochain control")
    date_next_retar = fields.Date("Date prochain Retard")
    no_arfi = fields.Char("N° ARFI")
    nbr = fields.Integer("Nbr", default=1)


class commande_kks(models.Model):

    _name = "commande.kks"
    _description = "Commandes/Kks"

    code_order = fields.Char("Code commande")
    code_kks = fields.Char("Code commande")


class commande_appareil(models.Model):

    _name = "commande.appareil"
    _description = "Commandes/Appareil"

    code_order = fields.Char("Code commande")
    code_appareil = fields.Char("Code appareil")


class commande_update(models.Model):

    _name = "commande.update"
    _description = "Update commande"

    def update_commande(self):
        rownum = 0
        self._cr.execute(
            """select  com.code_order,no_order,date_order,no_arfi,par.id,pl.id,mak.id,cat.id,
                                t.id,com.reference_appareil,no_interne,no_serie,
                                obs_devis,obs_recap,obs_atelier,essai_date,org.id,t2.id,essai_choix,essai_satisfaisant,date_next_ctr,date_next_retar
                                from commande com
                                left join res_partner par on par.code=cast(com.code_client as integer)
                            left join res_partner_place pl on pl.code_place=com.code_place
                            left join product_template_maker mak on mak.code=com.maker
                            left join product_category cat on cat.name=com.type_appareil and cat.type='type'
                            left join (
                            select a.id,concat(b.name,'/',a.name) as name from product_category a inner join product_category b on a.parent_id=b.id
                            where a.type='ss_type' and b.type='type') as t on t.name=com.ss_type_appareil
                            left join product_essai_organisme org on org.code_organisme=com.essai_org and org.type='organisme'
                            left join
                            (select id,code_person from product_essai_organisme where type='person') as t2 on t2.code_person=com.essai_nom
                            where com.code_order not in
                            (select code_order from product_order)  """
        )
        for res in self.env.cr.fetchall():
            self.env["product.order"].create(
                {
                    "code_order": res[0],
                    "no_order": res[1],
                    "date_order": res[2],
                    "no_arfi": res[3],
                    "customer_id": res[4],
                    "place_id": res[5],
                    "maker_id": res[6],
                    "type_appareil_id": res[7],
                    "ss_type_appareil_id": res[8],
                    "reference_appareil": res[9],
                    "no_interne": res[10],
                    "no_serie": res[11],
                    "obs_devis": res[12],
                    "obs_recap": res[13],
                    "obs_atelier": res[14],
                    "essai_date": res[15],
                    "essai_org": res[16],
                    "essai_nom": res[17],
                    "essai_choix": res[18],
                    "essai_satisfaisant": res[19],
                    "date_next_ctr": res[20],
                    "date_next_retar": res[21],
                }
            )
            self._cr.commit()
            rownum += 1
            _logger.info(rownum)

        self._cr.execute(
            """update product_order a set customer_id=t.id
                            from(
                            select code_order,b.id from commande a
                            inner join res_partner b on cast(code_client as integer)=b.code) as t
                            where a.code_order=t.code_order """
        )
        self._cr.commit()
        self._cr.execute(
            """update product_order ord set kks_id=t.id
                            from (select ck.code_order,pk.id from commande_kks ck
                            inner join product_kks pk on pk.code=cast(ck.code_kks as integer) )as t
                            where t.code_order=ord.code_order """
        )
        self._cr.commit()
        self._cr.execute(
            """update product_order ord set appareil_id=t.id
                            from (select ca.code_order,pt.id from commande_appareil ca
                            inner join product_template pt on pt.no_app=ca.code_appareil )as t
                            where t.code_order=ord.code_order """
        )
        self._cr.commit()
        self._cr.execute("""delete from product_order_operation """)
        self._cr.commit()
        self._cr.execute(
            """insert into product_order_operation(code_order,code_operation,code_piece,poids_matiere,coef_matiere,allotted_time,estimated_cost,spent_time,
                            real_cost,price,intervenant,mat_sal,marge)
                            select code_order,code_operation,code_piece,poids_matiere,coef_matiere,allotted_time,estimated_cost,spent_time,
                            real_cost,price,intervenant,mat_sal,marge from operation """
        )
        self._cr.commit()
        self._cr.execute(
            """update product_order_operation a set appareil_id=b.appareil_id
                            from product_order b where b.code_order=a.code_order """
        )
        self._cr.commit()
        self._cr.execute(
            """update product_order_operation a set piece_id=b.id
                            from product_piece b where b.code_piece=a.code_piece """
        )
        self._cr.commit()
        self._cr.execute(
            """ update product_order_operation a set order_id=b.id
                            from product_order b where b.code_order=a.code_order"""
        )
        self._cr.commit()
        self._cr.execute(
            """ update product_order_operation a set operation_id=b.id
                            from product_operation b where b.code_operation=a.code_operation"""
        )
        self._cr.commit()
        return True
