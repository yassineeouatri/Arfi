# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)



class product_import(models.Model):
    """
        A wizard to import product.
    """
    _name = 'product.import'
    _description = 'Product Import'

    file_name = fields.Char('Nom du fichier',size=256)
    file =  fields.Binary('Select *.csv', required=True,help="Select csv file.")

    _defaults = {
    }

    def import_product(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.template')
        for data in self.browse(cr, uid, ids, context):
            lines = (data.file.decode('base64')).split('\n')
            base=data.file_name.split(".")[0]
            extension=data.file_name.split(".")[1]
            if extension!='csv':
                raise ValidationError(_('Seuls les fichiers CSV sont autorisés à être importés'))
            ################################### import data ##################################################
            rownum = 0
            for line in lines[:-1]:
                if rownum == 0:
                    header=line.split(";")
                else :
                    code_matiere=type_=code_piece=no_piece=name=reference_appareil=diam1=diam2=longueur=largeur=profond=poids=param1=''
                    parent_id=material_id=None
                    data=line.split(";")
                    i=0
                    while i<len(header):
                        _logger.info(i)
                        _logger.info(header[i])
                        _logger.info(data[i])
                        if header[i]=='type':
                            type_=data[i]
                        if header[i]=='code_piece':
                            code_piece=data[i]
                        if header[i]=='no_piece':
                            no_piece=data[i]
                        if header[i]=='name':
                            name=data[i]
                        if header[i]=='reference_appareil':
                            reference_appareil=data[i]
                        if header[i]=='diam1':
                            diam1=data[i]
                        if header[i]=='diam2':
                            diam2=data[i]
                        if header[i]=='longueur':
                            longueur=data[i]
                        if header[i]=='largeur':
                            largeur=data[i]
                        if header[i]=='profond':
                            profond=data[i]
                        if header[i]=='poids':
                            poids=data[i]
                        if header[i]=='param1':
                            param1=data[i]
                        if header[i]=='code_matiere':
                            code_matiere=data[i]
                        i+=1
                    ################################################################################################
                    product_obj.create(cr, uid, {
                        'type': type_,
                        'code_piece': code_piece,
                        'no_piece': no_piece,
                        'name' : name,
                        'reference_appareil': reference_appareil,
                        'code_matiere' : code_matiere,
                        'diam1': diam1,
                        'diam2' : diam2,
                        'longueur': longueur,
                        'largeur': largeur,
                        'profond': profond,
                        'poids': poids,
                        'param1': param1,
                    })
                    cr.commit()
                rownum+=1
        cr.execute("""update product_template a set material_id=b.id
                        from  product_product_material b where a.code_matiere=b.code_matiere
                        and a.type='piece';
                        
                        update product_template a set parent_id=b.id
                        from  product_template b where a.reference_appareil=b.name
                        and a.type='piece' and b.type='appareil';""")
        cr.commit()
        return True

        # END
