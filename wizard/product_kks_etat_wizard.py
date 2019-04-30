# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import logging
import xlsxwriter
import sys
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import tools, _
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class product_kks_etat_wizard(models.Model):
    
    _name = 'product.kks.etat.wizard'
    _description = 'Product KKS Etat Wizard'
    
    name = fields.Char('Etat',default='Etat')
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)])
    facture_id = fields.Many2one('product.kks.facture','Facture')
    arret_id = fields.Many2one('product.arret','Arrêt')
    type_pdr = fields.Selection([('type1','Pièces à sortir du magasin'),('type2',"Liste générale PDR pour l'arrêt")],'Type PDR')
    type_outillage = fields.Selection([('type1','Essai sur site'),('type2',"Révision")],'Type outillage')
    type_travaux = fields.Selection([('1','Tout'),
                                     ('2',"Révision"),('3','Révision Chaudière'),('4',"Révision Machine"),
                                     ('5','Révision Vanne'),('6','Révision Vanne Chaudière'),('7',"Révision Vanne Machine"),
                                     ('8','Révision Soupapes'),('9','Révision Soupapes Chaudière'),('10',"Révision Soupapes Machine"),
                                     ('11','Changement Vanne'),('12','Changement Vanne Chaudière'),('13',"Changement Vanne Machine"),
                                     ('14','Changement PE'),('15','Tarage'),('16',"Tarage sur site"),
                                     ('17','Facture Echafaudages Vannes')
                                     ],'Type travaux')
    type_contrat = fields.Selection([('Contrat','Contrat'),('BC',"BC")],'Contrat/BC')
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
    def get_return(self,fichier):
        url = '/web/static/reporting/' + fichier
        if url:
            return { 'type': 'ir.actions.act_url','target': 'new', 'url': url, 'nodestroy': True }
        else:
            return True
    @api.multi
    def print_pdr_report_excel(self):
        data = {}
        data['form'] = self.read(['customer_id', 'arret_id' ,'type_pdr'])[0]
        if data['form']['type_pdr']=='type1':
            return self.generer_pdr_report_excel1(data)
        elif data['form']['type_pdr']=='type2':
            return self.generer_pdr_report_excel2(data)
        else :
            raise UserError(_('Merci de remplir le champs (Type PDR)'))           
    def generer_pdr_report_excel2(self,data):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env['product.image.directory'].search([('type','=','reporting')])
        for result in results:
            directory=result.name
        arret_id=data['form']['arret_id'][0]
        arret = self.env['product.arret'].search([('id','=',arret_id)])
        customer_id=data['form']['customer_id'][0]
        customer = self.env['res.partner'].search([('id','=',customer_id)])
        fichier="PDR _"+time.strftime('%H%M%S')+".xlsx"
        workbook = xlsxwriter.Workbook(directory + fichier)
        style_title = workbook.add_format({'bg_color' : '#003366','color' : 'white','text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'top' : 1, 'bottom' : 1,})
        style_titre = workbook.add_format({'color' : '#003366','text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'font_size' : 18, 'font_name' : 'tahoma'})
        style_titre2 = workbook.add_format({'text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'font_size' : 14, 'font_name' : 'tahoma' ,'border' : 2})
        style = workbook.add_format({'text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter','top' : 1, 'bottom' : 1, })
        style_ = workbook.add_format({'text_wrap' : True,'bold' :1,   'top' : 1, 'bottom' : 1,})
        style1 = workbook.add_format({  'text_wrap' : True,  'align' : 'center','valign' : 'vcenter','top' : 1, 'bottom' : 1,})
        style1_ = workbook.add_format({  'text_wrap' : True,  'top' : 1, 'bottom' : 1,})
        feuille=workbook.add_worksheet('PDR')
        feuille.set_zoom(85)
        feuille.freeze_panes(5, 0)
        feuille.set_tab_color('yellow')
        feuille.set_column('A:A', 16.71)
        feuille.set_column('B:I', 10)
        feuille.set_column('J:J', 76)
        feuille.set_column('K:K', 6)
        feuille.set_column('L:L', 15)
        feuille.set_column('M:M', 53)
        feuille.set_column('N:N', 22)
        feuille.merge_range('A1:N1', 'LISTE PDR ARRET', style_titre)
        record = self.env['product.kks.arret'].search([('arret_id', '=', arret_id)],limit=1)
        titre='Unité : '+record.unite_id.code+'           Arrêt : '+arret.name+'            Client : '+customer.name
        feuille.merge_range('E3:L3', titre, style_titre2)
        x=5
        feuille.write('A'+str(x),'Code Mag',style_title)
        feuille.write('B'+str(x),'Qté instalée',style_title)
        feuille.write('C'+str(x),'Stock',style_title)
        feuille.write('D'+str(x),'Absolue',style_title)
        feuille.write('E'+str(x),'Nécessaire',style_title)
        feuille.write('F'+str(x),'Recommandé',style_title)
        feuille.write('G'+str(x),'Sécurité',style_title)
        feuille.write('H'+str(x),'Quantité à sortir',style_title)
        feuille.write('I'+str(x),'Quantité à commander',style_title)
        feuille.write('J'+str(x),'Designation',style_title)
        feuille.write('K'+str(x),'item',style_title)
        feuille.write('L'+str(x),'KKS',style_title)
        feuille.write('M'+str(x),'Refference',style_title)
        feuille.write('N'+str(x),'Marque',style_title)
        
        records = self.env['product.kks.pdr.full.report'].search([('customer_id', '=', customer_id),
                                                        ('arret_id', '=', arret_id)])
        x=x+1
        for record in records:            
            if record.row==record.nbr:
                feuille.write('A'+str(x),record.magasin_id.code,style)
                feuille.write('B'+str(x),record.qte_installe,style)
                feuille.write('C'+str(x),record.stock,style)
                feuille.write('D'+str(x),record.absolue,style)
                feuille.write('E'+str(x),record.necessaire,style)
                feuille.write('F'+str(x),record.recommander,style)
                feuille.write('G'+str(x),record.securite,style)
                feuille.write('H'+str(x),record.qte_a_sortir,style)
                feuille.write('I'+str(x),record.qte_a_commander,style)
                feuille.write('J'+str(x),record.designation,style_)
                feuille.write('K'+str(x),record.item,style)
                feuille.write('L'+str(x),record.kks,style)
                feuille.write('M'+str(x),record.reference,style_)
                feuille.write('N'+str(x),record.maker_id.name,style)
            else :
                feuille.write('A'+str(x),record.magasin_id.code,style1)
                feuille.write('B'+str(x),'',style1)
                feuille.write('C'+str(x),'',style1)
                feuille.write('D'+str(x),'',style1)
                feuille.write('E'+str(x),'',style1)
                feuille.write('F'+str(x),'',style1)
                feuille.write('G'+str(x),'',style1)
                feuille.write('H'+str(x),'',style1)
                feuille.write('I'+str(x),'',style1)
                feuille.write('J'+str(x),record.designation,style1_)
                feuille.write('K'+str(x),record.item,style1)
                feuille.write('L'+str(x),record.kks,style1)
                feuille.write('M'+str(x),record.reference,style1_)
                feuille.write('N'+str(x),record.maker_id.name,style1)
            x=x+1

        workbook.close()
        return self.get_return(fichier)
    def generer_pdr_report_excel1(self,data):
        reload(sys)
        sys.setdefaultencoding("UTF8")
        results = self.env['product.image.directory'].search([('type','=','reporting')])
        for result in results:
            directory=result.name
        arret_id=data['form']['arret_id'][0]
        arret = self.env['product.arret'].search([('id','=',arret_id)])
        customer_id=data['form']['customer_id'][0]
        customer = self.env['res.partner'].search([('id','=',customer_id)])
        fichier="PDR _"+time.strftime('%H%M%S')+".xlsx"
        workbook = xlsxwriter.Workbook(directory + fichier)
        style_title = workbook.add_format({'bg_color' : '#003366','color' : 'white','text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'top' : 1, 'bottom' : 1,})
        style_titre = workbook.add_format({'color' : '#003366','text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'font_size' : 18, 'font_name' : 'tahoma'})
        style_titre2 = workbook.add_format({'text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter',
                                                          'font_size' : 14, 'font_name' : 'tahoma' ,'border' : 2})
        style = workbook.add_format({'text_wrap' : True,'bold' :1,  'align' : 'center','valign' : 'vcenter','top' : 1, 'bottom' : 1, })
        style_ = workbook.add_format({'text_wrap' : True,'bold' :1,   'top' : 1, 'bottom' : 1,})
        style1 = workbook.add_format({  'text_wrap' : True,  'align' : 'center','valign' : 'vcenter','top' : 1, 'bottom' : 1,})
        style1_ = workbook.add_format({  'text_wrap' : True,  'top' : 1, 'bottom' : 1,})
        feuille=workbook.add_worksheet('PDR')
        feuille.set_zoom(85)
        feuille.freeze_panes(5, 0)
        feuille.set_tab_color('yellow')
        feuille.set_column('A:A', 16.71)
        feuille.set_column('B:C', 10)
        feuille.set_column('D:D', 76)
        feuille.set_column('E:E', 6)
        feuille.set_column('F:F', 15)
        feuille.set_column('G:G', 53)
        feuille.set_column('H:H', 22)
        feuille.merge_range('A1:H1', 'Liste des PDR à sortir du magasin', style_titre)
        record = self.env['product.kks.arret'].search([('arret_id', '=', arret_id)],limit=1)
        titre='Unité : '+record.unite_id.code+'           Arrêt : '+arret.name+'            Client : '+customer.name
        feuille.merge_range('D3:G3', titre, style_titre2)
        x=5
        feuille.write('A'+str(x),'Code Mag',style_title)
        feuille.write('B'+str(x),'Qté Demandée',style_title)
        feuille.write('C'+str(x),'Qté Stock',style_title)
        feuille.write('D'+str(x),'Designation',style_title)
        feuille.write('E'+str(x),'item',style_title)
        feuille.write('F'+str(x),'KKS',style_title)
        feuille.write('G'+str(x),'Refference',style_title)
        feuille.write('H'+str(x),'Marque',style_title)
        
        records = self.env['product.kks.pdr.sortir.report'].search([('customer_id', '=', customer_id),
                                                        ('arret_id', '=', arret_id)])
        x=x+1
        for record in records:            
            if record.row==record.nbr:
                feuille.write('A'+str(x),record.magasin_id.code,style)
                feuille.write('B'+str(x),record.qte_a_sortir,style)
                feuille.write('C'+str(x),record.stock,style)
                feuille.write('D'+str(x),record.designation,style_)
                feuille.write('E'+str(x),record.item,style)
                feuille.write('F'+str(x),record.kks,style)
                feuille.write('G'+str(x),record.reference,style_)
                feuille.write('H'+str(x),record.maker_id.name,style)
            else :
                feuille.write('A'+str(x),record.magasin_id.code,style1)
                feuille.write('B'+str(x),'',style1)
                feuille.write('C'+str(x),'',style1)
                feuille.write('D'+str(x),record.designation,style1_)
                feuille.write('E'+str(x),record.item,style1)
                feuille.write('F'+str(x),record.kks,style1)
                feuille.write('G'+str(x),record.reference,style1_)
                feuille.write('H'+str(x),record.maker_id.name,style1)
            x=x+1

        workbook.close()
        return self.get_return(fichier)
    
    @api.multi
    def print_pdr_report(self):
        data = {}
        data['form'] = self.read(['customer_id', 'arret_id' ,'type_pdr'])[0]
        if data['form']['type_pdr']=='type1':
            return self._print_pdr_report2(data)
        elif data['form']['type_pdr']=='type2':
            return self._print_pdr_report(data)
        else :
            raise UserError(_('Merci de remplir le champs (Type PDR)'))
    
    def _print_pdr_report(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkkspdr', data=data)
    def _print_pdr_report2(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkkspdrsortir', data=data)
    
    @api.multi
    def print_echafaudage_report(self):
        data = {}
        data['form'] = self.read(['customer_id', 'arret_id'])[0]
        return self._print_echafaudage_report(data)
    def _print_echafaudage_report(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkksechafaudagearret', data=data)
    
    @api.multi
    def print_outillage_report(self):
        data = {}
        data['form'] = self.read(['customer_id', 'arret_id' ,'type_outillage'])[0]
        if data['form']['type_outillage']=='type1':
            return self._print_outillage_report2(data)
        elif data['form']['type_outillage']=='type2':
            return self._print_outillage_report(data)
        else :
            raise UserError(_('Merci de remplir le champs (Type Outillage)'))
    
    def _print_outillage_report(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkksoutillage', data=data)
    def _print_outillage_report2(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkksoutillagetarage', data=data)
    
    @api.multi
    def print_facture_report(self):
        data = {}
        data['form'] = self.read(['customer_id', 'arret_id' ,'type_travaux','type_contrat'])[0]
        if data['form']['type_travaux']=='17':
            return self._print_facture_report_(data)
        elif data['form']['type_travaux'] in ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16') : 
            fact=data['form']['type_contrat']
            type_extraction=''
            requete=" and fact='"+fact+"'"          
            if data['form']['type_travaux'] in ('2','3','4','5','6','7','8','9','10') :                
                nature_id=self.env['product.nature'].search([('name','=','Révision')],limit=1).id
                if nature_id :
                    requete +=' and nature_id='+str(nature_id)+' '   
                if data['form']['type_travaux']=='2':
                    type_extraction="Révision"
                if data['form']['type_travaux']=='3':
                    type_extraction="Révision chaudière"
                    type_implantation_id=self.env['product.type.implantation'].search([('name','=','Chaudière')],limit=1).id
                    if type_implantation_id:
                        requete=requete+' and type_implantation_id='+str(type_implantation_id)
                if data['form']['type_travaux']=='4':
                    type_extraction="Révision machine"
                    type_implantation_id=self.env['product.type.implantation'].search([('name','=','Machine')],limit=1).id
                    if type_implantation_id:
                        requete=requete+' and type_implantation_id='+str(type_implantation_id)
                if data['form']['type_travaux'] in ('5','6','7'):
                    type_appareil_id=self.env['product.category'].search([('name','=','VANN'),('type','=','type')],limit=1).id
                    ss_type_appareil_ids = self.env['product.category'].search([('parent_id','=',type_appareil_id),('type','=','ss_type')])
                    obj_ids=''
                    for obj in ss_type_appareil_ids:
                        obj_ids +=','+str(obj.id)
                    requete=requete+' and ss_type_appareil_id in ('+str(obj_ids[1:])+')'
                    if data['form']['type_travaux']=='5':
                        type_extraction="Révision vanne"
                    
                    if data['form']['type_travaux']=='6':
                        type_extraction="Révision vanne chaudière"
                        type_implantation_id=self.env['product.type.implantation'].search([('name','=','Chaudière')],limit=1).id
                        if type_implantation_id:
                            requete=requete+' and type_implantation_id='+str(type_implantation_id)
                    if data['form']['type_travaux']=='7':
                        type_extraction="Révision vanne machine"
                        type_implantation_id=self.env['product.type.implantation'].search([('name','=','Machine')],limit=1).id
                        if type_implantation_id:
                            requete=requete+' and type_implantation_id='+str(type_implantation_id)
                if data['form']['type_travaux'] in ('8','9','10'):
                    type_appareil_id=self.env['product.category'].search([('name','=','SOUP'),('type','=','type')],limit=1).id
                    ss_type_appareil_ids = self.env['product.category'].search([('parent_id','=',type_appareil_id),('type','=','ss_type')])
                    obj_ids=''
                    for obj in ss_type_appareil_ids:
                        obj_ids +=','+str(obj.id)
                    requete=requete+' and ss_type_appareil_id in ('+str(obj_ids[1:])+')'
                    if data['form']['type_travaux']=='8':
                        type_extraction="Révision Soupapes"
                    if data['form']['type_travaux']=='9':
                        type_extraction="Révision Soupapes chaudière"
                        type_implantation_id=self.env['product.type.implantation'].search([('name','=','Chaudière')],limit=1).id
                        if type_implantation_id:
                            requete=requete+' and type_implantation_id='+str(type_implantation_id)
                    if data['form']['type_travaux']=='10':
                        type_extraction="Révision Soupapes machine"
                        type_implantation_id=self.env['product.type.implantation'].search([('name','=','Machine')],limit=1).id
                        if type_implantation_id:
                            requete=requete+' and type_implantation_id='+str(type_implantation_id)
                
            if data['form']['type_travaux'] in ('11','12','13') : 
                self._cr.execute("select id from product_nature where name like 'Changement siège' or name like 'Sou%' or name like 'Changement siège'")               
                type_appareil_id=self.env['product.category'].search([('name','=','VANN'),('type','=','type')],limit=1).id
                ss_type_appareil_ids = self.env['product.category'].search([('parent_id','=',type_appareil_id),('type','=','ss_type')])
                obj_ids=''
                for obj in ss_type_appareil_ids:
                    obj_ids +=','+str(obj.id)
                requete=requete+' and ss_type_appareil_id in ('+str(obj_ids[1:])+')'
                ids=''
                nature_ids=self.env['product.nature'].search([('name','in',('Changement siège',
                                                                           'Soudure',
                                                                           'Soudure Manchette',
                                                                           'Travaux'))])
                if nature_ids :
                    for obj in nature_ids:
                        ids+=','+str(obj.id)
                    requete +=' and nature_id in ('+str(ids[1:])+') '  
                if   data['form']['type_travaux'] in ('11') :   
                    type_extraction="Changement Vannes"
                if   data['form']['type_travaux'] in ('12') :   
                    type_extraction="Changement Vannes Chaudière"
                    type_implantation_id=self.env['product.type.implantation'].search([('name','=','Chaudière')],limit=1).id
                    if type_implantation_id:
                        requete=requete+' and type_implantation_id='+str(type_implantation_id)
                if   data['form']['type_travaux'] in ('13') :   
                    type_extraction="Changement Vannes Machine"
                    type_implantation_id=self.env['product.type.implantation'].search([('name','=','Machine')],limit=1).id
                    if type_implantation_id:
                        requete=requete+' and type_implantation_id='+str(type_implantation_id)
            if data['form']['type_travaux']=='14':
                type_extraction="Changement PE"
                nature_id=self.env['product.nature'].search([('name','=','Changement PE')],limit=1).id
                if nature_id :
                    requete =requete+' and nature_id='+str(nature_id)+' ' 
            if data['form']['type_travaux']=='15':
                type_extraction="Tarage"
                nature_id=self.env['product.nature'].search([('name','=','Tarage')],limit=1).id
                if nature_id :
                    requete =requete+' and nature_id='+str(nature_id)+' ' 
            obj_facture=self.env['product.kks.facture.line']
            self._cr.execute('delete from product_kks_facture')
            self._cr.execute('delete from product_kks_facture_line')
            self._cr.execute("insert into product_kks_facture(name,date_facture,arret_id,customer_id,type_extraction,montant_text,type_facture)\
                                values('Facture',date(now()),"+str(data['form']['arret_id'][0])+","+str(data['form']['customer_id'][0])+",'"+type_extraction+"','"+self.trad(134552.30,'dirham','centime')+"','DEM')")
            facture_id=self.env['product.kks.facture'].search([('name','=','Facture')],limit=1)
            self.write({'facture_id' : facture_id.id})
            self._cr.execute("select item,reference,maker_id,montant,kks_id,unite_id,travaux_id,nature_id from product_kks_facture_arret\
                                where customer_id="+str(data['form']['customer_id'][0])+"\
                                and arret_id="+str(data['form']['arret_id'][0])+requete)
            for res in self.env.cr.fetchall():
                obj_facture.create({'facture_id' : facture_id.id,
                                    'item' : res[0],
                                    'reference' : res[1],
                                    'maker_id' : res[2],
                                    'montant' : res[3],
                                    'kks_id' : res[4],
                                    'unite_id' : res[5],
                                    'travaux_id' : res[6],
                                    'nature_id':res[7]
                                    })
        
            self._cr.execute("select distinct unite_id from product_kks_facture_arret\
                                where customer_id="+str(data['form']['customer_id'][0])+"\
                                and arret_id="+str(data['form']['arret_id'][0])+requete)
            for res in self.env.cr.fetchall():
                if res[0]:  
                    unite_id=res[0]
                    self._cr.execute("update product_kks_facture set unite_id="+str(unite_id))
            montant_ttc=0
            self._cr.execute("select montant_ttc from product_kks_facture where name='Facture'")
            for res in self.env.cr.fetchall():
                if res[0]:
                    montant_ttc=res[0]
            self._cr.execute("update product_kks_facture set montant_text='"+self.trad(montant_ttc,'dirham','centime')+"'")
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.kks.facture',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.facture_id.id,
                'views': [(self.env.ref('arfi.view_facture_changement_form').id, 'form')],
                 }
        else :
            raise UserError(_('Merci de remplir le champs (Type Travaux et Type Contrat)'))
    def _print_facture_report_(self, data):
        data['form'].update(self.read(['customer_id', 'arret_id','type_travaux','type_contrat'])[0])
        return self.env['report'].get_action(self, 'arfi.action_report_productkksfactureechafaudagearret', data=data)
