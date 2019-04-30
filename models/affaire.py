# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
import sys
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from docx import Document

class product_affaire(models.Model):

    _name = "product.affaire"
    _description = "Affaires"
    _inherit = ['ir.needaction_mixin']
    _order = 'name desc'
    
    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute("""select cast(max(cast(name as numeric))+1 as integer)
                        from product_affaire
                        where length(name)=6""")
        rslt= cr.fetchone()[0]
        return rslt
    
          
    def get_name(self):
        i = '1'
        cr = self.env.cr
        cr.execute("""select cast(max(cast(name as numeric))+1 as integer)
                        from product_affaire
                        where length(name)=6""")
        for res in cr.fetchall():
            if res[0]:
                i= res[0]
        rslt =str(str(i).zfill(6))
        
        return rslt
    name = fields.Char('Affaire N°',default=get_name,size = 6)
    type = fields.Selection([('colmatage','Colmatage'),
                             ('Remise en etat (REE)','Remise en état (REE)'),
                             ('GPPM','Gestion de parc et prévision matériel'),
                             ('Essai sur site','Essai sur site'),
                             ('Fabrication/Revente','Fabrication/Revente')],'Type')
    date_affaire = fields.Date("Date d'ouverture",default=fields.Date.today)
    no_parent = fields.Char('N° contrat Mère')
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)])
    person_id = fields.Many2one('res.partner.person','Demandeur')
    title_id = fields.Many2one('res.partner.title','Titre')
    city_id = fields.Many2one('product.city','Ville')
    mobile = fields.Char('GSM')
    phone = fields.Char('Tél')
    fax = fields.Char('Fax')
    distance_km = fields.Integer('Distance Km')
    distance_temps  = fields.Char('Distance temps')
    standard  = fields.Char('Standard')
    travaux_plan = fields.Selection([('oui','Oui'),('non','Non')], 'Travaux planifiés')
    date_prevu = fields.Date('Date prévue de réalisation',default=fields.Date.today)
    @api.onchange('customer_id')
    def onchange_customer_id(self):
        res = {}
        if self.customer_id:
            res['domain'] = {'person_id': [('partner_id', '=', self.customer_id.id)]}
        else:
            res['domain'] = {'person_id': []}
        return res
    @api.onchange('person_id')
    def onchange_person_id(self):
        if self.person_id:
            self.fax = self.person_id.fax
            self.mobile = self.person_id.mobile
            self.phone = self.person_id.phone
            self.title_id = self.person_id.title_id.id
            self.standard = self.person_id.standard