# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
import sys
import xlsxwriter
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class product_purchase(models.Model):

    _name = "product.purchase"
    _description = "Achats"
    _order = "date_purchase desc"
    _rec_name = "create_date"

    @api.depends("purchase_line_ids")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            montant = 0.0
            for line in obj.purchase_line_ids:
                montant += line.montant
            obj.update(
                {
                    "montant_ht": montant,
                    "tva": montant * 0.2,
                    "montant_ttc": montant * 1.2,
                }
            )

    @api.depends("purchase_evaluation_ids")
    def _amount_evaluation(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            evaluation = 0.0
            for line in obj.purchase_evaluation_ids:
                evaluation += line.note_id.name
            obj.update(
                {
                    "note_evaluation": evaluation,
                }
            )

    def action_select_evaluation(self):
        self._cr.execute("update product_purchase_type_evaluation set variant='t'")
        self._cr.commit()
        for obj in self.purchase_evaluation_ids:
            self._cr.execute(
                "update product_purchase_type_evaluation set variant='f' where id="
                + str(obj.type_evaluation_id.id)
            )
            self._cr.commit()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.purchase.evaluation.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref(
                        "arfi.view_product_purchase_evaluation_wizard_form"
                    ).id,
                    "form",
                )
            ],
            "context": {"default_purchase_id": self.id},
            "target": "new",
        }

    create_date = fields.Datetime("Date de création", readonly=True)
    date_purchase = fields.Date("Date Commande", copy=False)
    date_reception = fields.Date("Date réception", copy=False)
    customer_id = fields.Many2one(
        "res.partner", "Client", domain=[("customer", "=", True)], copy=True
    )
    supplier_id = fields.Many2one("res.supplier", "Fournisseur", copy=True)
    contact_id = fields.Many2one("res.contact", "Contact Fournisseur", copy=True)
    bc = fields.Char("BC N°", copy=True)
    bl = fields.Char("BL N°", copy=True)
    conforme = fields.Boolean("Conforme")
    delai = fields.Integer("Délai")
    no_affaire = fields.Char("Affaire N°")
    note = fields.Text("Observation")
    montant_ht = fields.Float(
        compute="_amount_all", string="Montant Global HT", readonly=True, store=True
    )
    montant_ttc = fields.Float(
        compute="_amount_all", string="TTC", readonly=True, store=True
    )
    tva = fields.Float(
        compute="_amount_all", string="TVA (20%)", readonly=True, store=True
    )
    note_evaluation = fields.Integer(
        compute="_amount_evaluation",
        string="Note évaluation",
        readonly=True,
        store=True,
    )
    purchase_line_ids = fields.One2many(
        "product.purchase.line", "purchase_id", "Lignes", copy=True
    )
    purchase_evaluation_ids = fields.One2many(
        "product.purchase.evaluation", "purchase_id", "Lignes", copy=True
    )

    @api.onchange("supplier_id")
    def onchange_supplier_id(self):
        res = {}
        if self.supplier_id:
            res["domain"] = {"contact_id": [("supplier_id", "=", self.supplier_id.id)]}
        else:
            res["domain"] = {"contact_id": []}
        return res


class product_purchase_line(models.Model):

    _name = "product.purchase.line"
    _description = "Achats Line"

    @api.one
    @api.depends("price_unit", "qte", "remise")
    def _compute_price(self):
        self.montant = (self.price_unit * self.qte) * (1 - (self.remise * 1.00 / 100))

    @api.onchange("magasin_id")
    def _onchange_magasin(self):
        rslt = ""
        pieces = self.env["product.kks.piece"].search(
            [("magasin_id", "=", self.magasin_id.id)]
        )
        for piece in pieces:
            rslt = piece.piece_id.name
        self.designation = rslt

    purchase_id = fields.Many2one("product.purchase", "Commande")
    magasin_id = fields.Many2one("product.magasin", "Code Magasin")
    outillage_id = fields.Many2one("product.outillage", "Outillage")
    supplier_id = fields.Many2one(
        "res.supplier",
        related="purchase_id.supplier_id",
        string="Fournisseur",
        store=True,
        readonly=False,
    )
    contact_id = fields.Many2one(
        "res.contact",
        related="purchase_id.contact_id",
        string="Contact Fournisseur",
        store=True,
        readonly=False,
    )
    remise = fields.Float("Remise (%)")
    qte = fields.Float("Qte", default=1)
    designation = fields.Char("Désignation")
    price_unit = fields.Float("PU HT (Dhs)")
    montant = fields.Float(
        string="Montant", store=True, readonly=True, compute="_compute_price"
    )


class product_purchase_evaluation(models.Model):

    _name = "product.purchase.evaluation"
    _description = "Achats Evaluation"

    purchase_id = fields.Many2one("product.purchase", "Commande")
    type_evaluation_id = fields.Many2one(
        "product.purchase.type.evaluation", "Type évaluation"
    )
    note_id = fields.Many2one("product.purchase.note", "Note")


class product_purchase_type_evaluation(models.Model):

    _name = "product.purchase.type.evaluation"
    _description = "Type Evaluation"
    _order = "code"

    def get_code(self):
        i = 1
        cr = self.env.cr
        cr.execute("""select max(code)+1 from product_purchase_type_evaluation""")
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = i
        return rslt

    code = fields.Integer("Code", default=get_code)
    name = fields.Char("Type d'évaluation")
    variant = fields.Boolean("Variant", default=True)
    _sql_constraints = [
        ("name_uniq", "unique (name)", "Attention! Enregistrement unique"),
    ]


class product_purchase_note(models.Model):

    _name = "product.purchase.note"
    _description = "Notes"
    _order = "code"

    def get_code(self):
        i = 1
        cr = self.env.cr
        cr.execute("""select max(code)+1 from product_purchase_note""")
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = i
        return rslt

    code = fields.Integer("Code", default=get_code)
    name = fields.Integer("Note")


class product_purchase_activity(models.Model):

    _name = "product.purchase.activity"
    _description = "Activities"
    _order = "code"

    def get_code(self):
        i = "1"
        cr = self.env.cr
        cr.execute(
            """select cast(max(cast(code as numeric))+1  as text)
                        from product_purchase_activity"""
        )
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = str(i.zfill(3))

        return rslt

    code = fields.Char("Code", default=get_code, size=3)
    name = fields.Char("Activité")

    @api.constrains("code")
    def _check_code(self):
        for record in self:
            if record.code:
                if len(record.code) != 3:
                    raise ValidationError(
                        _("Attention! Le code est composé de 5 chiffres.")
                    )
                if not record.code.isdigit():
                    raise ValidationError(
                        _("Attention! Le code ne doit contenir que des chiffres.")
                    )


class product_bc(models.Model):

    _name = "product.bc"
    _description = "Bon de Commandes"
    _inherit = ["ir.needaction_mixin"]
    _order = "name desc"

    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute(
            """select max(cast(substring(name,0,7) as numeric))+1 
                            from product_bc
                            where length(name)=9
                            and substring(name,8,2)=to_char(now(),'YY')"""
        )
        rslt = cr.fetchone()[0]
        return rslt

    def get_name(self):
        i = "1"
        cr = self.env.cr
        cr.execute(
            """select cast(max(cast(substring(name,0,7) as numeric))+1  as text)
                        from product_bc
                        where length(name)=9
                        and substring(name,8,2)=to_char(now(),'YY')"""
        )
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = str(i.zfill(6)) + "/" + str(time.strftime("%Y"))[2:4]

        return rslt

    name = fields.Char("BC N°", default=get_name, size=9, copy=False)
    no_commande = fields.Char("Commande N°")
    date_bc = fields.Date("Date BC")
    arret_id = fields.Many2one("product.arret", "Arrêt")
    unite_id = fields.Many2one("product.unite", "Code Unité")
    travaux_id = fields.Many2one("product.travaux", "Travaux")
    supplier_id = fields.Many2one("res.supplier", "Fournisseur", copy=True)
    bc_line_ids = fields.One2many("product.bc.line", "bc_id", "Lignes de BC")

    @api.multi
    def print_bc_report_pdf(self):
        return self.env["report"].get_action(self, "arfi.report_productbc")

    def get_return(self, fichier):
        url = "/web/static/reporting/" + fichier
        if url:
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
                "nodestroy": True,
            }
        else:
            return True

    @api.multi
    def print_bc_report_excel(self):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env["product.image.directory"].search(
            [("type", "=", "reporting")]
        )
        for result in results:
            directory = result.name
        fichier = "Bon de Commande _" + time.strftime("%H%M%S") + ".xlsx"
        workbook = xlsxwriter.Workbook(directory + fichier)
        style_title = workbook.add_format(
            {
                "bg_color": "#003366",
                "color": "white",
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style_titre = workbook.add_format(
            {
                "color": "#003366",
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 18,
                "font_name": "tahoma",
            }
        )
        style_titre2 = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 14,
                "font_name": "tahoma",
                "border": 2,
            }
        )
        style = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style_number = workbook.add_format(
            {
                "num_format": "#,##0.00",
                "text_wrap": True,
                "bold": 1,
                "align": "right",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style__ = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "right": 1,
            }
        )
        style_ = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "left": 1,
            }
        )
        feuille = workbook.add_worksheet("BC")
        feuille.set_zoom(85)
        feuille.freeze_panes(4, 0)
        feuille.set_tab_color("yellow")
        feuille.set_column("A:A", 5.33)
        feuille.set_column("B:B", 14.33)
        feuille.set_column("C:C", 16)
        feuille.set_column("D:D", 40.33)
        feuille.set_column("E:E", 16.83)
        feuille.set_column("F:F", 15.33)
        feuille.set_column("G:G", 16.67)
        feuille.merge_range("A1:H1", "BON DE COMMANDE N°" + self.name, style_titre)
        titre = (
            "Désignation :"
            + self.travaux_id.name
            + " arrêt "
            + self.arret_id.name
            + " unité "
            + self.unite_id.name
        )
        feuille.merge_range("A3:E3", titre, style_titre2)
        feuille.write("F3", "Prix de vente")
        feuille.write("G3", "Prix d'achat")
        x = 4
        feuille.write("A" + str(x), "item", style_title)
        feuille.write("B" + str(x), "KKS", style_title)
        feuille.write("C" + str(x), "Marque", style_title)
        feuille.write("D" + str(x), "Réference", style_title)
        feuille.write("E" + str(x), "Action", style_title)
        feuille.write("F" + str(x), "Montant JLEC", style_title)
        feuille.write("G" + str(x), "Montant MIPROS", style_title)

        records = self.bc_line_ids
        x = x + 1
        sale_price = purchase_price = ""
        for record in records:
            feuille.write("A" + str(x), record.item, style)
            feuille.write("B" + str(x), record.kks_id.name, style)
            feuille.write("C" + str(x), record.maker_id.name, style)
            feuille.write("D" + str(x), record.appareil_id.name, style)
            feuille.write("E" + str(x), record.nature_id.name, style)
            feuille.write("F" + str(x), record.sale_price, style_number)
            feuille.write("G" + str(x), record.purchase_price, style_number)
            feuille.write("H" + str(x), "", style_)

            sale_price += "+F" + str(x)
            purchase_price += "+G" + str(x)
            x = x + 1
        feuille.write("E" + str(x), "", style__)
        feuille.write_formula("F" + str(x), sale_price[1:], style_number)
        feuille.write_formula("G" + str(x), purchase_price[1:], style_number)
        feuille.write("H" + str(x), "", style_)
        workbook.close()
        return self.get_return(fichier)


class product_bc_line(models.Model):

    _name = "product.bc.line"
    _description = "Lignes de BC"

    bc_id = fields.Many2one("product.bc", "BC")
    kks_id = fields.Many2one("product.kks", "Code KKS")
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
    purchase_price = fields.Float("Prix d'achat")
    sale_price = fields.Float("Prix de vente")

    @api.onchange("nature_id", "appareil_id")
    def _onchange_nature_id(self):
        if self.nature_id and self.appareil_id:
            purchase_price = sale_price = 0
            objs = self.env["product.appareil.price"].search(
                [
                    ("appareil_id", "=", self.appareil_id.id),
                    ("nature_id", "=", self.nature_id.id),
                ]
            )
            for obj in objs:
                purchase_price = obj.purchase_price
                sale_price = obj.sale_price
            self.purchase_price = purchase_price
            self.sale_price = sale_price


class product_bc_piece(models.Model):

    _name = "product.bc.piece"
    _description = "Bon de Commandes des pièces"
    _inherit = ["ir.needaction_mixin"]
    _order = "name desc"

    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute(
            """select max(cast(substring(name,0,7) as numeric))+1 
                            from product_bc_piece
                            where length(name)=9
                            and substring(name,8,2)=to_char(now(),'YY')"""
        )
        rslt = cr.fetchone()[0]
        return rslt

    def get_name(self):
        i = "1"
        cr = self.env.cr
        cr.execute(
            """select cast(max(cast(substring(name,0,7) as numeric))+1  as text)
                        from product_bc_piece
                        where length(name)=9
                        and substring(name,8,2)=to_char(now(),'YY')"""
        )
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = str(i.zfill(6)) + "/" + str(time.strftime("%Y"))[2:4]

        return rslt

    name = fields.Char("BC N°", default=get_name, size=9, copy=False)
    date_bc = fields.Date("Date BC")
    company_id = fields.Many2one("res.company", "Société", copy=True)
    supplier_id = fields.Many2one("res.supplier", "Fournisseur", copy=True)
    bc_line_ids = fields.One2many(
        "product.bc.piece.line", "bc_id", "Lignes de BC", copy=True
    )

    @api.multi
    def print_bc_report_pdf(self):
        if self.company_id.name == "ARFI":
            return self.env["report"].get_action(self, "arfi.report_productbcpiecearfi")
        if self.company_id.name == "MECA ETANCHE":
            return self.env["report"].get_action(self, "arfi.report_productbcpiecemeca")

    def get_return(self, fichier):
        url = "/web/static/reporting/" + fichier
        if url:
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
                "nodestroy": True,
            }
        else:
            return True

    @api.multi
    def print_bc_report_excel(self):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env["product.image.directory"].search(
            [("type", "=", "reporting")]
        )
        for result in results:
            directory = result.name
        fichier = "Bon de Commande _" + time.strftime("%H%M%S") + ".xlsx"
        workbook = xlsxwriter.Workbook(directory + fichier)
        style_title = workbook.add_format(
            {
                "bg_color": "#003366",
                "color": "white",
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style_titre = workbook.add_format(
            {
                "color": "#003366",
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 18,
                "font_name": "tahoma",
            }
        )
        style = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style_number = workbook.add_format(
            {
                "num_format": "#,##0.00",
                "text_wrap": True,
                "bold": 1,
                "align": "right",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        style__ = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "right": 1,
            }
        )
        style_ = workbook.add_format(
            {
                "text_wrap": True,
                "bold": 1,
                "left": 1,
            }
        )
        feuille = workbook.add_worksheet("BC")
        feuille.set_zoom(85)
        feuille.freeze_panes(3, 0)
        feuille.set_tab_color("yellow")
        feuille.set_column("A:A", 12.33)
        feuille.set_column("B:B", 70)
        feuille.set_column("C:C", 16)
        feuille.set_column("D:D", 18.57)
        feuille.merge_range("A1:D1", "BON DE COMMANDE N°" + self.name, style_titre)

        x = 3
        feuille.write("A" + str(x), "Code", style_title)
        feuille.write("B" + str(x), "Désignation", style_title)
        feuille.write("C" + str(x), "S Famille", style_title)
        feuille.write("D" + str(x), "Quantité Demandée", style_title)

        records = self.bc_line_ids
        x = x + 1
        qte = ""
        for record in records:
            feuille.write("A" + str(x), record.code_interne, style)
            feuille.write("B" + str(x), record.piece_id.name, style)
            feuille.write("C" + str(x), record.magasin_id.code, style)
            feuille.write("D" + str(x), record.qte, style_number)

            qte += "+D" + str(x)
            x = x + 1
        feuille.write("C" + str(x), "", style__)
        feuille.write_formula("D" + str(x), qte[1:], style_number)
        feuille.write("E" + str(x), "", style_)
        workbook.close()
        return self.get_return(fichier)


class product_bc_piece_line(models.Model):

    _name = "product.bc.piece.line"
    _description = "Lignes de BC"

    bc_id = fields.Many2one("product.bc.magasin", "BC")
    magasin_id = fields.Many2one("product.magasin", "Code Magasin")
    piece_id = fields.Many2one("product.piece", "Désignation")
    code_interne = fields.Char("Code Interne")
    qte = fields.Integer("Quantité Demandée")

    @api.onchange("magasin_id")
    def _onchange_magasin(self):
        rslt = None
        pieces = self.env["product.kks.piece"].search(
            [("magasin_id", "=", self.magasin_id.id)]
        )
        for piece in pieces:
            rslt = piece.piece_id.id
        self.piece_id = rslt
