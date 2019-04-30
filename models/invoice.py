# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
import datetime
import sys
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta
from docx import Document

class product_invoice(models.Model):

    _name = "product.invoice"
    _description = "Invoice"
    _inherit = ['ir.needaction_mixin']
    _order = 'name desc'
    
    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute("""select max(cast(substring(name,0,7) as numeric))+1 
                        from product_invoice
                        where length(name)=9
                        and substring(name,8,2)=to_char(now(),'YY')""")
        rslt= cr.fetchone()[0]
        return rslt
    
    @api.depends('invoice_line_ids','remise_pourcentage','tva_transport_pourcentage','retenue_pourcentage')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            montant = 0.0
            for line in obj.invoice_line_ids:
                montant+=line.montant
            obj.update({
                'montant' : montant,
                'retenue' : (montant*(((obj.retenue_pourcentage)*1.00/100))),
                'tva_transport' : (montant*(((obj.tva_transport_pourcentage)*1.00/100))),
                'remise' : (montant*(((obj.remise_pourcentage)*1.00/100))),
                'montant_ht': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100))),
                'tva': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*0.2,
                'montant_ttc': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*1.2,
                'montant_text' : self.trad((montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*1.2,'dirham','centime')
            })

    @api.depends('date_invoice')
    def compute_date_echeance(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            if obj.date_invoice:
                date_echeance = (datetime.datetime.strptime(obj.date_invoice, '%Y-%m-%d')+relativedelta(months=+3)).strftime('%Y-%m-%d')
                obj.update({
                    'date_echeance': date_echeance,
                })

            
    def get_name(self):
        i = '1'
        cr = self.env.cr
        cr.execute("""select cast(max(cast(substring(name,0,7) as numeric))+1  as text)
                        from product_invoice
                        where length(name)=9
                        and substring(name,8,2)=to_char(now(),'YY')""")
        for res in cr.fetchall():
            if res[0]:
                i= res[0]
        rslt =str(i.zfill(6))+'/'+str(time.strftime('%Y'))[2:4]
        
        return '/'
    name = fields.Char('Facture N°',default=get_name,size = 9,copy= False)
    type = fields.Selection([('invoice','Facture'),
                             ('devis','Devis'),
                             ('avoir','Avoir')],'Type',copy= True)
    company_id = fields.Many2one('res.company','Société',copy= True, required = True)
    date_invoice = fields.Date('Date Facture',default=fields.Date.today,copy= False)
    date_echeance = fields.Date(compute='compute_date_echeance',string= 'Date Facture',  copy=False, store=True)
    date_paiement = fields.Date('Date Paiement', copy=False)
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)],copy= True)
    order_id = fields.Many2one('product.order','Commande N°',copy= True)
    no_order  = fields.Char('Commande N°')
    bc = fields.Char('BC ou OL',copy= True)
    bl = fields.Char('BL',copy= True)
    ice = fields.Char('ICE',size = 15,copy= True)
    city = fields.Char('Adresse',copy= True)
    designation = fields.Char('Désignation',copy= True)
    customer_name = fields.Char(related='customer_id.name', store=True)
    montant = fields.Float(compute='_amount_all',string='Montant HT', readonly=True, store=True)
    montant_ht = fields.Float(compute='_amount_all',string='Montant Global HT', readonly=True, store=True)
    montant_ttc = fields.Float(compute='_amount_all',string='TTC', readonly=True, store=True)
    montant_text = fields.Text(compute='_amount_all',string='Montant', readonly=True, store=True)
    invoice_line_ids = fields.One2many('product.invoice.line','invoice_id','Lignes',copy= True)
    remise_pourcentage = fields.Float('Remise (%)',copy= True)
    remise = fields.Float(compute='_amount_all',string='Remise', readonly=True, store=True)
    tva_transport_pourcentage = fields.Float('TVA Transport (%)',copy= True)
    tva_transport = fields.Float(compute='_amount_all',string='TVA Transport', readonly=True, store=True)
    retenue_pourcentage = fields.Float('Retenue Garantie (%)',copy= True)
    retenue = fields.Float(compute='_amount_all',string='Retenue', readonly=True, store=True)
    tva = fields.Float(compute='_amount_all',string='TVA (20%)', readonly=True, store=True)
    rib = fields.Char('RIB',copy= True)
    swift = fields.Char('SWIFT',copy= True)
    mode_paiement = fields.Selection([('Cheque', 'Chèque'),('Virement','Virement'),('Espece','Espèce')], 'Mode Paiement')
    no_cheque = fields.Char('N° Chèque')
    no_virement = fields.Char('N° Virement')
    state = fields.Selection([
            ('draft','Non Payée'),
            ('open', 'Payée'),
        ], string='Etat', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,)
    
    def tradd(self,num):
        global t1,t2
        ch=''
        if num==0 :
            ch=''
        elif num<20:
            ch=t1[num]
        elif num>=20:
            if (num>=70 and num<=79)or(num>=90):
                z=int(num/10)-1
            else:
                z=int(num/10)
            ch=t2[z]
            num=num-z*10
            if (num==1 or num==11) and z<8:
                ch=ch+' et'
            if num>0:
                ch=ch+' '+self.tradd(num)
            else:
                ch=ch+self.tradd(num)
        return ch
    def tradn(self,num):
        global t1,t2
        ch=''
        flagcent=False
        if num>=1000000000:
            z=int(num/1000000000)
            ch=ch+self.tradn(z)+' milliard'
            if z>1:
                ch=ch+'s'
            num=num-z*1000000000
        if num>=1000000:
            z=int(num/1000000)
            ch=ch+self.tradn(z)+' million'
            if z>1:
                ch=ch+'s'
            num=num-z*1000000
        if num>=1000:
            if num>=100000:
                z=int(num/100000)
                if z>1:
                    ch=ch+' '+self.tradd(z)
                ch=ch+' cent'
                flagcent=True
                num=num-z*100000
                if int(num/1000)==0 and z>1:
                    ch=ch+'s'
            if num>=1000:
                z=int(num/1000)
                if (z==1 and flagcent) or z>1:
                    ch=ch+' '+self.tradd(z)
                num=num-z*1000
            ch=ch+' mille'
        if num>=100:
            z=int(num/100)
            if z>1:
                ch=ch+' '+self.tradd(z)
            ch=ch+" cent"
            num=num-z*100
            if num==0 and z>1:
                ch=ch+'s'
        if num>0:
            ch=ch+" "+self.tradd(num)
        return ch
    def trad(self,nb, unite="euro", decim="centime"):
        global t1,t2
        nb=round(nb,2)
        t1=["","un","deux","trois","quatre","cinq","six","sept","huit","neuf","dix","onze","douze","treize","quatorze","quinze","seize","dix-sept","dix-huit","dix-neuf"]
        t2=["","dix","vingt","trente","quarante","cinquante","soixante","septante","quatre-vingt","nonante"]
        z1=int(nb)
        z3=(nb-z1)*100
        z2=int(round(z3,0))
        if z1==0:
            ch="zéro"
        else:
            ch=self.tradn(abs(z1))
        if z1>1 or z1<-1:
            if unite!='':
                ch=ch+" "+unite+'s'
        else:
            ch=ch+" "+unite
        if z2>0:
            ch=ch+self.tradn(z2)
            if z2>1 or z2<-1:
                if decim!='':
                    ch=ch+" "+decim+'s'
            else:
                ch=ch+" "+decim
        if nb<0:
            ch="moins "+ch
        return ch.upper()
    @api.onchange('customer_id')
    def _onchange_kks(self):
        if self.customer_id:
            self.city = self.customer_id.city
            self.ice = self.customer_id.barcode
            
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            i = '1'
            cr = self.env.cr
            cr.execute("""select cast(max(cast(substring(name,0,7) as numeric))+1  as text)
                                    from product_invoice
                                    where length(name)=9
                                    and substring(name,8,2)=to_char(now(),'YY')
                                    and company_id={}""".format(self.company_id.id))
            for res in cr.fetchall():
                if res[0]:
                    i = res[0]
            self.name = str(i.zfill(6)) + '/' + str(time.strftime('%Y'))[2:4]
            self.swift = self.company_id.swift
            self.rib = self.company_id.rib
            
    @api.constrains('ice')
    def _check_ice(self):
        for record in self:
            if record.ice:
                if len(record.ice) != 15 :
                    raise ValidationError(_("Attention! Le numéro ICE est composé de 15 chiffres."))  
                if not record.ice.isdigit(): 
                    raise ValidationError(_("Attention! L'ICE ne doit contenir que des chiffres."))    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                if len(record.name) != 9 :
                    raise ValidationError(_("Attention! Le numéro de la facture doit contenir 9 caractères.")) 
                if record.name[6:7]!='/' or not record.name[0:6].isdigit() or not record.name[7:9].isdigit(): 
                    raise ValidationError(_("Attention! Le numéro de la facture doit être de la forme 999999/99.")) 
    @api.multi
    def action_convert_to_invoice(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default['type'] = 'invoice'
        invoice_id=super(product_invoice, self).copy(default=default)
        if invoice_id:
            invoice=self.env['product.invoice'].search([('id', '=', invoice_id.id)])                
            action = {
                        'type': 'ir.actions.act_window',
                        'res_model': 'product.invoice',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': invoice.id,
                        'views': [(self.env.ref('arfi.product_invoice_form_view').id, 'form')],
                       
                    }
    
            return action
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        invoice_id=super(product_invoice, self).copy(default=default)
        return invoice_id
    
    @api.multi
    def button_dummy(self):
        invoice_id = self.create({'customer_id' : self.customer_id.id,
                                 'company_id' : self.company_id.id,
                                 'city' : self.city,
                                 'bl' : self.bl,
                                 'ice' : self.ice,
                                 'bc' : self.bc,
                                 'designation' : self.designation,
                                 'rib' : self.rib,
                                 'swift' : self.swift})
       
                
        return True
   
    
    @api.multi
    def action_invoice_draft(self):
        self.write({'state': 'draft'})
    @api.multi
    def action_invoice_open(self):
        self.write({'state': 'open'})
        
    @api.multi
    def invoice_print(self):
        data = {}
        data['form'] = self.read(['id'])[0]
        return self._invoice_print(data)
    def _invoice_print(self, data):
        data['form'].update(self.read(['id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productinvoice', data=data)
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_invoice_line(models.Model):

    _name = "product.invoice.line"
    _description = "Invoice Line"
    _order = 'kks'
    
    @api.one
    @api.depends('price_unit', 'qte')
    def _compute_price(self):
        self.montant = self.price_unit * self. qte
        
    invoice_id = fields.Many2one('product.invoice', 'Facture')
    qte = fields.Float('Qte' , default = 1)
    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    price_unit = fields.Float('PU HT (Dhs)')
    montant =  fields.Float(string='Montant',
                                store=True, readonly=True, compute='_compute_price')
class product_devis(models.Model):

    _name = "product.devis"
    _description = "Devis"
    _inherit = ['ir.needaction_mixin']
    _order = 'name desc'
    
    @api.model
    def _needaction_count(self, domain=None):
        cr = self.env.cr
        cr.execute("""select max(cast(substring(name,0,7) as numeric))+1 
                        from product_devis
                        where length(name)=9
                        and substring(name,8,2)=to_char(now(),'YY')""")
        rslt= cr.fetchone()[0]
        return rslt
    
    @api.depends('devis_line_ids','remise_pourcentage','tva_transport_pourcentage','retenue_pourcentage')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            montant = 0.0
            for line in obj.devis_line_ids:
                montant+=line.montant
            obj.update({
                'montant' : montant,
                'retenue' : (montant*(((obj.retenue_pourcentage)*1.00/100))),
                'tva_transport' : (montant*(((obj.tva_transport_pourcentage)*1.00/100))),
                'remise' : (montant*(((obj.remise_pourcentage)*1.00/100))),
                'montant_ht': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100))),
                'tva': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*0.2,
                'montant_ttc': (montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*1.2,
                'montant_text' : self.trad((montant*(1-((obj.retenue_pourcentage+obj.tva_transport_pourcentage+obj.remise_pourcentage)*1.00/100)))*1.2,'dirham','centime')
            })
            
    def get_name(self):
        i = '1'
        cr = self.env.cr
        if self.type =="devis":
            cr.execute("""select cast(max(cast(substring(name,0,7) as numeric))+1  as text)
                            from product_devis
                            where length(name)=9
                            and substring(name,8,2)=to_char(now(),'YY')""")
            for res in cr.fetchall():
                if res[0]:
                    i= res[0]
        rslt =str(i.zfill(6))+'/'+str(time.strftime('%Y'))[2:4]
        
        return rslt
    name = fields.Char('Facture N°',default=get_name,size = 9,copy= False)
    type = fields.Selection([('devis','Devis')],'Type',copy= True)
    company_id = fields.Many2one('res.company','Société',copy= True)
    date_devis = fields.Date('Date',default=fields.Date.today,copy= False)
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)],copy= True)
    order_id = fields.Many2one('product.order','Commande N°',copy= True)
    no_order  = fields.Char('Commande N°')
    da = fields.Char('DA N°',copy= True)
    ao = fields.Char('AO N°',copy= True)
    ice = fields.Char('ICE',size = 15,copy= True)
    city = fields.Char('Adresse',copy= True)
    designation = fields.Char('Désignation',copy= True)
    customer_name = fields.Char(related='customer_id.name', store=True)
    montant = fields.Float(compute='_amount_all',string='Montant HT', readonly=True, store=True)
    montant_ht = fields.Float(compute='_amount_all',string='Montant Global HT', readonly=True, store=True)
    montant_ttc = fields.Float(compute='_amount_all',string='TTC', readonly=True, store=True)
    montant_text = fields.Text(compute='_amount_all',string='Montant', readonly=True, store=True)
    devis_line_ids = fields.One2many('product.devis.line','devis_id','Lignes',copy= True)
    remise_pourcentage = fields.Float('Remise (%)',copy= True)
    remise = fields.Float(compute='_amount_all',string='Remise', readonly=True, store=True)
    tva_transport_pourcentage = fields.Float('TVA Transport (%)',copy= True)
    tva_transport = fields.Float(compute='_amount_all',string='TVA Transport', readonly=True, store=True)
    retenue_pourcentage = fields.Float('Retenue Garantie (%)',copy= True)
    retenue = fields.Float(compute='_amount_all',string='Retenue', readonly=True, store=True)
    tva = fields.Float(compute='_amount_all',string='TVA (20%)', readonly=True, store=True)
    rib = fields.Char('RIB',copy= True)
    swift = fields.Char('SWIFT',copy= True)
    state = fields.Selection([
            ('draft','Etat bruillon'),
            ('open', 'Validée'),
        ], string='Status', index=True, readonly=True, default='draft',track_visibility='onchange', copy=False,)
    
    def tradd(self,num):
        global t1,t2
        ch=''
        if num==0 :
            ch=''
        elif num<20:
            ch=t1[num]
        elif num>=20:
            if (num>=70 and num<=79)or(num>=90):
                z=int(num/10)-1
            else:
                z=int(num/10)
            ch=t2[z]
            num=num-z*10
            if (num==1 or num==11) and z<8:
                ch=ch+' et'
            if num>0:
                ch=ch+' '+self.tradd(num)
            else:
                ch=ch+self.tradd(num)
        return ch

    def tradn(self,num):
        global t1,t2
        ch=''
        flagcent=False
        if num>=1000000000:
            z=int(num/1000000000)
            ch=ch+self.tradn(z)+' milliard'
            if z>1:
                ch=ch+'s'
            num=num-z*1000000000
        if num>=1000000:
            z=int(num/1000000)
            ch=ch+self.tradn(z)+' million'
            if z>1:
                ch=ch+'s'
            num=num-z*1000000
        if num>=1000:
            if num>=100000:
                z=int(num/100000)
                if z>1:
                    ch=ch+' '+self.tradd(z)
                ch=ch+' cent'
                flagcent=True
                num=num-z*100000
                if int(num/1000)==0 and z>1:
                    ch=ch+'s'
            if num>=1000:
                z=int(num/1000)
                if (z==1 and flagcent) or z>1:
                    ch=ch+' '+self.tradd(z)
                num=num-z*1000
            ch=ch+' mille'
        if num>=100:
            z=int(num/100)
            if z>1:
                ch=ch+' '+self.tradd(z)
            ch=ch+" cent"
            num=num-z*100
            if num==0 and z>1:
                ch=ch+'s'
        if num>0:
            ch=ch+" "+self.tradd(num)
        return ch


    def trad(self,nb, unite="euro", decim="centime"):
        global t1,t2
        nb=round(nb,2)
        t1=["","un","deux","trois","quatre","cinq","six","sept","huit","neuf","dix","onze","douze","treize","quatorze","quinze","seize","dix-sept","dix-huit","dix-neuf"]
        t2=["","dix","vingt","trente","quarante","cinquante","soixante","septante","quatre-vingt","nonante"]
        z1=int(nb)
        z3=(nb-z1)*100
        z2=int(round(z3,0))
        if z1==0:
            ch="zéro"
        else:
            ch=self.tradn(abs(z1))
        if z1>1 or z1<-1:
            if unite!='':
                ch=ch+" "+unite+'s'
        else:
            ch=ch+" "+unite
        if z2>0:
            ch=ch+self.tradn(z2)
            if z2>1 or z2<-1:
                if decim!='':
                    ch=ch+" "+decim+'s'
            else:
                ch=ch+" "+decim
        if nb<0:
            ch="moins "+ch
        return ch.upper()
    @api.onchange('customer_id')
    def _onchange_kks(self):
        if self.customer_id:
            self.city = self.customer_id.city
            self.ice = self.customer_id.barcode
            
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.swift = self.company_id.swift
            self.rib = self.company_id.rib
            
    @api.constrains('ice')
    def _check_ice(self):
        for record in self:
            if record.ice:
                if len(record.ice) != 15 :
                    raise ValidationError(_("Attention! Le numéro ICE est composé de 15 chiffres."))  
                if not record.ice.isdigit(): 
                    raise ValidationError(_("Attention! L'ICE ne doit contenir que des chiffres."))    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                if len(record.name) != 9 :
                    raise ValidationError(_("Attention! Le numéro de la facture doit contenir 9 caractères.")) 
                if record.name[6:7]!='/' or not record.name[0:6].isdigit() or not record.name[7:9].isdigit(): 
                    raise ValidationError(_("Attention! Le numéro de la facture doit être de la forme 999999/99.")) 
    @api.multi
    def action_convert_to_invoice(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        invoice_id = self.env['product.invoice'].create({'customer_id' : self.customer_id.id,
                                 'company_id' : self.company_id.id,
                                 'city' : self.city,
                                 'type' : 'invoice',
                                 'ice' : self.ice,
                                 'designation' : self.designation,
                                 'rib' : self.rib,
                                 'swift' : self.swift,
                                  'montant' :self.montant,
                                'montant_ht' : self.montant_ht,
                                'montant_ttc' : self.montant_ttc,
                                'montant_text' : self.montant_text,
                                'remise_pourcentage' : self.remise_pourcentage,
                                'remise' : self.remise,
                                'tva_transport_pourcentage' : self.tva_transport_pourcentage,
                                'tva_transport' : self.tva_transport,
                                'retenue_pourcentage' : self.retenue_pourcentage,
                                'retenue' : self.retenue,
                                'tva'  : self.tva})
        for obj in self.devis_line_ids:
            invoice_line_id = self.env['product.invoice.line'].create({'invoice_id' :  invoice_id.id,
                                                'qte' : obj.qte,
                                                'kks' : obj.kks,
                                                'designation' : obj.designation,
                                                'price_unit' : obj.price_unit,
                                                'montant' : obj.montant})
        if invoice_id:
            invoice=self.env['product.invoice'].search([('id', '=', invoice_id.id)])                
            action = {
                        'type': 'ir.actions.act_window',
                        'res_model': 'product.invoice',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': invoice.id,
                        'views': [(self.env.ref('arfi.product_invoice_form_view').id, 'form')],
                       
                    }
    
            return action
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        devis_id=super(product_devis, self).copy(default=default)
        return devis_id
    
    @api.multi
    def button_dummy(self):
        devis_id = self.create({'customer_id' : self.customer_id.id,
                                 'company_id' : self.company_id.id,
                                 'city' : self.city,
                                 'bl' : self.bl,
                                 'ice' : self.ice,
                                 'bc' : self.bc,
                                 'designation' : self.designation,
                                 'rib' : self.rib,
                                 'swift' : self.swift})
       
                
        return True
   
    
    @api.multi
    def action_devis_draft(self):
        self.write({'state': 'draft'})
    @api.multi
    def action_devis_open(self):
        self.write({'state': 'open',
                    'montant_text' : self.trad(self.montant_ttc,'dirham','centime')})
        
    @api.multi
    def devis_print(self):
        data = {}
        data['form'] = self.read(['id'])[0]
        return self._devis_print(data)
    def _devis_print(self, data):
        data['form'].update(self.read(['id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productdevis', data=data)
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_devis_line(models.Model):

    _name = "product.devis.line"
    _description = "Devis Line"
    _order = 'kks'
    
    @api.one
    @api.depends('price_unit', 'qte')
    def _compute_price(self):
        self.montant = self.price_unit * self. qte
        
    devis_id = fields.Many2one('product.devis', 'Facture')
    qte = fields.Float('Qte' , default = 1)
    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    price_unit = fields.Float('PU HT (Dhs)')
    montant =  fields.Float(string='Montant',
                                store=True, readonly=True, compute='_compute_price')

class res_company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    @api.depends('bank_id','city_id','no_compte','cle_rib')
    def _compute_rib(self):
        """
        Compute the total amounts of the SO.
        """
        for obj in self:
            obj.update({
                'rib' : str(obj.bank_id.code)+' '+str(obj.city_id.code)+' '+str(obj.no_compte)+' '+str(obj.cle_rib),
                'swift' : obj.bank_id.code_bank+obj.bank_id.code_country+obj.bank_id.code_emplacement+obj.bank_id.code_branche })
    bank_id = fields.Many2one('product.bank','Banque')
    city_id = fields.Many2one('product.city','Ville')
    no_compte = fields.Char('N° Compte Bancaire',size=16)
    cle_rib = fields.Char('Clé Rib',size=2)
    rib = fields.Char(compute='_compute_rib',string='RIB', readonly=True, store=True)
    swift = fields.Char(compute='_compute_rib',string='SWIFT', readonly=True, store=True)
    
   
class product_bank(models.Model):

    _name = "product.bank"
    _description = "Banques"
    _order = 'code'
    
  
    name = fields.Char('Libellée')
    code = fields.Char('Code',size=3)
    code_bank = fields.Char('Code Banque',size=4)
    code_country = fields.Char('Code Pays',size=2)
    code_emplacement = fields.Char('Code Emplacement',size=2)
    code_branche = fields.Char('Code Branche',size=3)
    
class product_city(models.Model):

    _name = "product.city"
    _description = "Villes"
    _order = 'code'
    
  
    name = fields.Char('Libellée')
    code = fields.Char('Code',size=3)
    province = fields.Char('Province', size= 64)
