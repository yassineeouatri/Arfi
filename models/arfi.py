# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
import logging
import datetime
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from docx import Document
import sys
from odoo.osv import expression
_logger = logging.getLogger(__name__)

class product_plan_original(models.Model):
    _name = 'product.plan.original'

    appareil_id = fields.Many2one('product.template','Appareil', required=False)
    file_name = fields.Char('Nom du fichier', size=256)
    file = fields.Binary("Fichier")

class product_procedure(models.Model):
    _name = 'product.procedure'

    appareil_id = fields.Many2one('product.template','Appareil', required=False)
    piece_id = fields.Many2one('product.piece','Pièce', required=False)
    directory_id = fields.Many2one('muk_dms.directory', string="Directory", required=False)
    file_id = fields.Many2one('muk_dms.file', 'Fichier',
                                domain="[('directory','=',directory_id)]",
                                change_default=True,help="")
    type_file = fields.Selection([('ins','Instruction de travail'),
                             ('ope','Mode Opératoire'),('man','Manuel de Maintenance')] ,'Type du fichier' , required=False)
    
    def download_file_(self):
        url="/dms/file/download/"+str(self.file_id.id)
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
    def write_file(self,data, filename):
        with open(filename, 'wb') as f:
            f.write(data)  
    def download_file(self):
        import base64
        reload(sys)
        sys.setdefaultencoding("utf-8")
        results = self.env['product.image.directory'].search([('type','=','reporting')])
        for result in results:
            directory=result.name
        self._cr.execute("select filename,file_extension,type_file,file from muk_dms_file a\
                    left join muk_dms_database_data  b\
                    on a.file_ref=concat('muk_dms.database_data,',b.id)\
                    where a.id="+str(self.file_id.id))
        for res in self.env.cr.fetchall():
            filename=res[0]
            file_extension=res[1]
            data=res[3]
        #destination='C:\\Users\\Yassine\\workspace\\arfi_2010\\addons\\web\\static\\reporting\\'+filename
        destination=directory+filename
        data=base64.decodestring(data)
        self.write_file(data, destination)
        url="/web/static/reporting/"+filename
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
    def return_directory_id(self,name):
        rslt=None
        results = self.env['muk_dms.directory'].search([('name', '=', name)])
        for obj in results:
            rslt=obj.id
        return rslt
    @api.onchange('type_file')
    def _onchange_type_file(self):
        if self.type_file=="prev":
            self.directory_id=self.return_directory_id("Plan Prevention")
        elif self.type_file=="ins":
            self.directory_id=self.return_directory_id("Instructions de Travail")
        elif self.type_file=="ope":
            self.directory_id=self.return_directory_id("Mode Operatoire")
        elif self.type_file=="man":
            self.directory_id=self.return_directory_id("Manuel de Maintenance")
        else :
            self.directory_id=None
     
class product_datetarif(models.Model):
    _name = 'product.datetarif'
    _order = 'date'
    
    @api.depends('date')
    def compute_name(self):
        for obj in self:
            if obj.date:
                obj.name=datetime.datetime.strptime(obj.date, '%Y-%m-%d').strftime('%d/%m/%Y')
            else :
                obj.name=''

    name = fields.Char(compute="compute_name",store=True)     
    date = fields.Date('Date')
    code = fields.Char('Code')

class product_degat(models.Model):
    _name = 'product.degat'
    _order = 'name'
    
    name = fields.Char("Nature de dégât")  
    
class product_etat(models.Model):
    _name = 'product.etat'
    _order = 'name'
    
    name = fields.Char("Etat") 
    
class product_operation(models.Model):

    _name = "product.operation"
    _description = "Product Operation"
    _order = 'name'
    
    code =  fields.Char("Code", required=False)
    name = fields.Char("Nom", required=False)
    code_operation = fields.Char('Code Opération')
    application = fields.Selection([('appareil','Appareil'),('piece','Pièce')],"S'applique à", required=False)
    variant = fields.Boolean('Variant',default=True)
    
    _sql_constraints = [
            ('name_uniq', 'unique (code,name,application)', "Attention! Enregistrement unique !"),
    ]
class product_nature(models.Model):

    _name = "product.nature"
    _description = "Product Nature"
    _order = "name"
    
    code =  fields.Char("Code", required=False)
    name = fields.Char("Nom", required=False)
    variant = fields.Boolean('Variant',default=True)
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique !"),
    ]
class product_tarif(models.Model):

    _name = "product.tarif"
    _description = "Product Tarif"
    _order = "name"
    
    code =  fields.Char("Code", required=False)
    name = fields.Char("Nom", required=False)
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class product_info(models.Model):

    _name = "product.info"
    _description = "Product Info"
    _order = "sequence"
    
    code = fields.Char("Code", required=False)
    name = fields.Char("Libellé", required=False)
    variant = fields.Boolean('Variant',default=True)
    sequence = fields.Integer('Sequence')
  
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_unite(models.Model):

    _name = "product.unite"
    _description = "Unite"
    _order = 'name'
    
    code = fields.Char("Code", size=6,required=True)
    name = fields.Char("Unité", required=True)
    
    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].zfill(2)
        result = super(product_unite, self).create(vals)
        return result
    _sql_constraints = []
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_travaux(models.Model):

    _name = "product.travaux"
    _description = "Travaux"
    _order = 'name'
    
    code = fields.Char("Code",required=False)
    name = fields.Char("Libellé",required=False)
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_arret(models.Model):

    _name = "product.arret"
    _description = "Arrets"
    _order = 'date'
    
    @api.depends('date')
    def compute_name(self):
        for obj in self:
            if obj.date:
                obj.name=datetime.datetime.strptime(obj.date, '%Y-%m-%d').strftime('%d/%m/%Y')
            else :
                obj.name=''

    name = fields.Char(compute="compute_name",store=True)       
    code = fields.Char("N° d'affaire",required=False)
    date = fields.Date("Date", required=True)
    
    _sql_constraints = [
            ('name_uniq', 'unique (date)', "Attention! Enregistrement unique"),
    ]
    
class product_implantation(models.Model):

    _name = "product.implantation"
    _description = "Implantation"
    
    code = fields.Char("Code", size=6,required=False)
    name = fields.Char("Implantation", required=False)
    
    @api.model
    def create(self, vals):
        vals['code'] = vals['code'].zfill(6)
        result = super(product_implantation, self).create(vals)
        return result
    _sql_constraints = [
            ('name_uniq', 'unique (code)', "Attention! Enregistrement unique"),
    ]
    
class product_type_implantation(models.Model):

    _name = "product.type.implantation"
    _description = "Type Implantation"
    
    name = fields.Char("Libellé", required=False)
   
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
    
    

class product_mesure_test(models.Model):

    _name = "product.mesure.test"
    _description = "Mesure Test"
    _order = "name"
    
    name = fields.Char("Libellé", required=False)
    variant = fields.Boolean('Variant',default=True)
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_mesure_service(models.Model):

    _name = "product.mesure.service"
    _description = "Mesure service"
    _order = "name"
    
    name = fields.Char("Libellé", required=False)
    variant = fields.Boolean('Variant',default=True)
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
class product_echafaudage(models.Model):

    _name = "product.echafaudage"
    _description = "Product Echafaudage"
    _order = 'code'
    _rec_name="libelle"
    
    code = fields.Char("Code", required=False)
    libelle = fields.Char("Libellé", required=False)
    
    @api.model
    def create(self, vals):
        vals['code'] = vals['code'].zfill(7)
        result = super(product_echafaudage, self).create(vals)
        return result
    _sql_constraints = [
            ('name_uniq', 'unique (code)', "Attention! Enregistrement unique"),
    ]
    
class product_outillage(models.Model):

    _name = "product.outillage"
    _description = "Product Outillage"
    _order = 'code'
    _rec_name= "designation"
    
    code =  fields.Char("Code", required=False)
    designation =  fields.Char("Désignation", required=False)
    photo_name = fields.Char('Nom du fichier', size=256)
    photo = fields.Binary("Image")
    stock =  fields.Integer('Stock')
    qte_dem =  fields.Integer('Qte Demandée')
    
    _sql_constraints = [
            ('name_uniq', 'unique (code)', "Attention! Enregistrement unique"),
    ]
    @api.multi
    def name_get(self):
        if not len(self.ids):
            return []
        resuhh = []
        for record in self:
            resuhh.append((record.id, record.designation))
        return resuhh
    def code_get(self):
        if not len(self.ids):
            return []
        resuhh = []
        for record in self:
            if record.code:
                resuhh.append((record.id, record.code))
        return resuhh

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + [('code', 'ilike', name)]),limit=limit)
            if recs :
                return recs.code_get()
        if not recs:
            recs = self.search([('designation', operator, name)] + args, limit=limit)
        return recs.name_get()
class product_essai_organisme(models.Model):

    _name = "product.essai.organisme"
    _description = "Product Essai Organisme"
    _order = 'type,name'
    
    type = fields.Selection([('person','Personne'),('organisme','Organisme')],'Type')
    name = fields.Char("Nom", required=False)
    code_person = fields.Char("Code Person", required=False)
    code_organisme = fields.Char("Code Organisme", required=False)
    
    
class product_essai_nom(models.Model):

    _name = "product.essai.nom"
    _description = "Essai Nom"
    
    name = fields.Char("Nom", required=False)
    organisme_id = fields.Many2one('product.essai.organisme', 'Organisme')
    
class product_template_maker(models.Model):

    _name = "product.template.maker"
    _description = "Product template Maker"
    
    code = fields.Char("Code", required=False)
    name = fields.Char("Fabricant", required=False)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized image of the product. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]

class product_product_material_norme(models.Model):

    _name = "product.product.material.norme"
    _description = "Product Product Material Norme"
    _order= "name"
    
    name = fields.Char("Norme", required=False)
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Attention! Enregistrement unique"),
    ]
    
    
class product_product_material_reference(models.Model):

    _name = "product.product.material.reference"
    _description = "Product Product Material Reference"
    _rec_name= 'reference'

    no_arfi = fields.Char("N° Arfi", required=False)
    material_id = fields.Many2one('product.product.material',string='N° Arfi')
    material_search_id = fields.Many2one('product.product.material.search',string='N° Arfi')
    norme_id = fields.Many2one('product.product.material.norme',string='Norme')
    norme = fields.Char("Norme", required=False)
    reference = fields.Char("Référence", required=False)
        
    @api.onchange('material_id') # if these fields are changed, call method
    def check_change(self):
        self.no_arfi = self.material_id.name
        
    @api.onchange('norme_id') # if these fields are changed, call method
    def change_norme(self):
        self.norme = self.norme_id.name
        

class product_product_material(models.Model):

    _name = "product.product.material"
    _description = "Product Product Material"
    
    name =  fields.Char("Référence", required=False)
    designation =  fields.Char("Désignation", required=False)
    code_matiere =  fields.Char("Code Matière", required=False)
    reference_ids =  fields.One2many('product.product.material.reference','material_id',string='Références', readonly=False)
    
    @api.model
    def create(self, vals):
        """if vals['name']:
            vals['name'] = vals['name'].zfill(4)"""
        result = super(product_product_material, self).create(vals)
        return result
    @api.multi
    def write(self, vals):
        "vals['name'] = vals['name'].zfill(4)"
        result = super(product_product_material, self).write(vals)
        return result
    @api.multi
    def name_get(self):
        if not len(self.ids):
            return []
        resuhh = []
        product_name = []
        for record in self:
            """if record.designation:
                product_name = '[' + str(record.designation) + ']'
                product_name += str(record.name)
                s = resuhh.append((record.id, product_name))

            else:"""
            s = resuhh.append((record.id, record.name))

        return resuhh
    def designation_get(self):
        if not len(self.ids):
            return []
        resuhh = []
        for record in self:
            if record.designation:
                resuhh.append((record.id, record.designation))
        return resuhh

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + [('designation', 'ilike', name)]),limit=limit)
            if recs :
                return recs.designation_get()
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
class product_product_material_search(models.Model):

    _name = "product.product.material.search"
    _description = "Product Product Material Search"
    
    
    @api.onchange('material_id')
    def onchange_material_id(self):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self._cr.execute("select id from product_product_material_search")
        for res in self.env.cr.fetchall():
            obj_id=res[0]
        self._cr.execute("update product_product_material_reference set material_search_id=Null")
        self._cr.commit()
        if self.material_id:
            designation=''
            if self.material_id.designation:
                designation=self.material_id.designation
            self._cr.execute("update product_product_material_search set designation='"+str(designation)+"'")
            self._cr.commit()
            self._cr.execute("update product_product_material_reference set material_search_id="+str(obj_id)+"\
                            where material_id="+str(self.material_id.id))
            self._cr.commit()
        reference_ids = self.env['product.product.material.reference'].search( [('material_id', '=', self.material_id.id)])
        return {'value': {'reference_ids': reference_ids,'designation' : self.material_id.designation}}
    
    @api.onchange('norme_id')
    def onchange_norme_id(self):
        if self.norme_id:    
            if self.material_id.id:
                return {'value': {'reference_id': None},'domain': {'reference_id': [('norme_id','=',self.norme_id.id),
                                                                                    ('material_id','=',self.material_id.id)]}} 
            else:
                return {'value': {'reference_id': None},'domain': {'reference_id': [('norme_id','=',self.norme_id.id)]}}
            
    @api.onchange('reference_id')
    def onchange_reference_id(self):
        if self.reference_id and self.norme_id: 
            return {'value': {'material_id': self.reference_id.material_id.id}} 
        
        
    piece_id = fields.Many2one('product.piece','Pièce')
    material_id = fields.Many2one('product.product.material','N° ARFI')
    norme_id = fields.Many2one('product.product.material.norme','Norme') 
    reference_id = fields.Many2one('product.product.material.reference','Réference')     
    designation = fields.Char("Désignation" ,readonly=True)
    
    def case_validate(self):
        if self.piece_id and self.material_id: 
            self._cr.execute("update product_piece set material_id="+str(self.material_id.id)+"\
                            where id="+str(self.piece_id.id))
            self._cr.commit()
        return True
    reference_ids =  fields.One2many('product.product.material.reference','material_search_id',string='Références', readonly=True)