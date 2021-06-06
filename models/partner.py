# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import xlsxwriter
import time
import sys

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    code = fields.Integer("Code")
    contact = fields.Char("Contact")
    place_ids = fields.One2many("res.partner.place", "partner_id", "Lieux")
    person_ids = fields.One2many("res.partner.person", "partner_id", "Contacts")
    order_ids = fields.One2many(
        "product.order", "customer_id", "Commandes", readonly=True
    )
    purchase_ids = fields.One2many(
        "product.purchase", "customer_id", "Achats", readonly=True
    )
    affaire_ids = fields.One2many(
        "product.affaire", "customer_id", "Affaires", readonly=True
    )
    contrat_ids = fields.One2many(
        "product.kks.tarif", "customer_id", "Contrats", readonly=True
    )
    invoice_ids = fields.One2many(
        "product.invoice", "customer_id", "Factures", readonly=True
    )
    recovery_ids = fields.One2many(
        "product.invoice.recovery", "customer_id", "Recouvrement", readonly=True
    )
    contract_appareil_ids = fields.One2many(
        "product.contract.appareil", "customer_id", "Contrats Appareils", readonly=True
    )
    contract_piece_ids = fields.One2many(
        "product.contract.piece", "customer_id", "Contrats Pièces", readonly=True
    )
    price = fields.Float("Prix")

    @api.constrains("barcode")
    def _check_ice(self):
        for record in self:
            if record.barcode:
                if len(record.barcode) != 15:
                    raise ValidationError(
                        _("Attention! Le numéro ICE est composé de 15 chiffres.")
                    )
                if not record.barcode.isdigit():
                    raise ValidationError(
                        _("Attention! L'ICE ne doit contenir que des chiffres.")
                    )

    @api.model
    def create(self, vals):
        self._cr.execute("select max(code) from res_partner")
        code = self.env.cr.fetchall()[0][0]
        if not code:
            code = 0
        vals["code"] = code + 1
        result = super(res_partner, self).create(vals)
        return result

    @api.multi
    def print_contracts(self):
        data = {}
        data["form"] = self.read(["id"])[0]
        return self.generer_contrat_report_excel(data)

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

    def generer_contrat_report_excel(self, data):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env["product.image.directory"].search(
            [("type", "=", "reporting")]
        )
        for result in results:
            directory = result.name
        self.env["res.partner"].search([("id", "=", self.id)])
        fichier = "Contrats _" + self.name + "_" + time.strftime("%H%M%S") + ".xlsx"
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
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
            }
        )
        feuille = workbook.add_worksheet("Contrats")
        feuille.set_zoom(85)
        feuille.freeze_panes(3, 0)
        feuille.set_tab_color("yellow")
        feuille.set_column("A:A", 7)
        feuille.set_column("B:B", 17)
        feuille.set_column("C:C", 70)
        feuille.set_column("D:D", 30)
        feuille.set_column("E:E", 30)
        feuille.set_column("F:G", 10)
        feuille.set_column("H:H", 12)
        feuille.merge_range("A1:H1", "LISTE DES CONTRATS : " + self.name, style_titre)
        x = 3
        feuille.write("A" + str(x), "Item", style_title)
        feuille.write("B" + str(x), "Code KKS", style_title)
        feuille.write("C" + str(x), "Appareil", style_title)
        feuille.write("D" + str(x), "Code Mag", style_title)
        feuille.write("E" + str(x), "Nature Travaux", style_title)
        feuille.write("F" + str(x), "Choix", style_title)
        feuille.write("G" + str(x), "Fact", style_title)
        feuille.write("H" + str(x), "Montant", style_title)

        records = self.env["product.kks.tarif"].search(
            [("customer_id", "=", self.id)], order="kks_id asc"
        )
        x = x + 1
        for record in records:
            magasin = ""
            pieces = self.env["product.piece"].search(
                [("name", "=", record.appareil_id.name)], limit=1
            )
            if pieces:
                magasins = self.env["product.kks.piece"].search(
                    [("piece_id", "=", pieces.id)], limit=1
                )
                if magasins:
                    magasin = magasins.magasin_id.code
            feuille.write("A" + str(x), record.item, style)
            feuille.write("B" + str(x), record.kks_id.name, style)
            feuille.write("C" + str(x), record.appareil_id.name, style)
            feuille.write("D" + str(x), magasin, style)
            feuille.write("E" + str(x), record.nature_id.name, style)
            feuille.write("F" + str(x), record.choice, style)
            feuille.write("G" + str(x), record.fact, style)
            feuille.write("H" + str(x), record.montant, style_number)
            x = x + 1

        workbook.close()
        return self.get_return(fichier)


class res_contact(models.Model):
    _name = "res.contact"
    _description = "Contact Fournisseurs"
    _rec_name = "contact"
    _order = "code"

    code = fields.Integer("Numéro", readonly=True)
    supplier_id = fields.Many2one("res.supplier", "Raison sociale")
    contact = fields.Char("Contact")
    street = fields.Char("Adresse")
    phone = fields.Char("Tél")
    fax = fields.Char("Fax")
    mobile = fields.Char("GSM")
    email = fields.Char("Email")

    @api.model
    def create(self, vals):
        self._cr.execute("select max(code) from res_contact")
        code = self.env.cr.fetchall()[0][0]
        if not code:
            code = 0
        vals["code"] = code + 1
        result = super(res_contact, self).create(vals)
        return result


class res_supplier(models.Model):
    _name = "res.supplier"
    _description = "Fournisseurs"

    def get_code(self):
        i = "1"
        cr = self.env.cr
        cr.execute(
            """select cast(max(cast(code as numeric))+1 as text) from res_supplier"""
        )
        for res in cr.fetchall():
            if res[0]:
                i = res[0]
        rslt = str(i.zfill(4))
        return rslt

    code = fields.Char("Code Raison Sociale", default=get_code, size=4)
    name = fields.Char("Raison Sociale", required=True)
    activity_id = fields.Many2one("product.purchase.activity", "Activité")
    person_ids = fields.One2many("res.contact", "supplier_id", "Contacts")
    purchase_ids = fields.One2many(
        "product.purchase", "supplier_id", "Liste des achats", readonly=True
    )

    @api.model
    def create(self, vals):
        vals["code"] = str(vals["code"]).zfill(4)
        vals["name"] = vals["name"].upper()
        result = super(res_supplier, self).create(vals)
        return result


class res_partner_place(models.Model):
    _name = "res.partner.place"
    _rec_name = "description"

    partner_id = fields.Many2one("res.partner", "Client")
    code = fields.Char("Code")
    code_place = fields.Char("Code Place")
    description = fields.Char("Déscription")


class res_partner_person(models.Model):
    _name = "res.partner.person"

    name = fields.Char("Nom et Prénom")
    partner_id = fields.Many2one("res.partner", "Client")
    title_id = fields.Many2one("res.partner.title", "Titre")
    street = fields.Char("Adresse")
    phone = fields.Char("Tél")
    mobile = fields.Char("Portable")
    fax = fields.Char("Fax")
    email = fields.Char("Email")
    standard = fields.Char("Standard")
