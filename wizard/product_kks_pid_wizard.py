# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import fitz
import logging
import webbrowser
import base64
from pyPdf import PdfFileReader, PdfFileWriter
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo import tools, _
#from wand.image import Image

_logger = logging.getLogger(__name__)


def get_directory(self):
    results = self.env['product.image.directory'].search([('type', '=', 'reporting')])
    for result in results:
        directory = result.name
    return directory


class product_kks_pid_wizard(models.Model):
    _name = 'product.kks.pid.wizard'
    _description = 'Product KKS PID Wizard'

    name = fields.Char('Etat', default='PID')
    kks_id = fields.Many2one('product.kks', 'KKS', required=True)
    appareil = fields.Char('Appareil Associé')
    note = fields.Text('Informations Techniques')

    @api.onchange('kks_id')
    def _onchange_kks_id(self):
        if self.kks_id.appareil_id:
            self.appareil = self.kks_id.appareil_id.name
            rslt = ''
            for obj in self.kks_id.appareil_id.attribute_line_ids:
                rslt1 = rslt2 = ''
                if obj.attribute_id.name:
                    rslt1 = obj.attribute_id.name
                if obj.value:
                    rslt2 = obj.value
                rslt += rslt1 + " : " + rslt2 + "\n"
            self.note = rslt


class product_kks_pid_file(models.Model):
    _name = 'product.kks.pid.file'
    _description = 'Product KKS PID File'
    _rec_name = 'filename'

    filename = fields.Char('Nom du fichier', )
    file = fields.Binary('Fichier')
    annotation_ids = fields.One2many('product.kks.pid.annotation', 'file_id', 'Annotations')

    """def convert_pdf2img(self, directory, filename):
        print directory+filename
        with Image(filename=directory+filename) as img:
            print('width =', img.width)
            print('height =', img.height)
            print('pages = ', len(img.sequence))
            print('resolution = ', img.resolution)

        with img.convert('png') as converted:
            converted.save(filename=directory+filename+'.png')
        return True"""

    @api.model
    def create(self, vals):
        template = super(product_kks_pid_file, self).create(vals)
        results = self.env['product.image.directory'].search([('type', '=', 'reporting')])
        for result in results:
            directory = result.name
        self.write_file(vals['filename'], vals['file'], directory)
        #self.convert_pdf2img(directory,vals['filename'])
        return template


    def write_file(self, filename, file, directory):
        with open(directory + filename, 'wb') as f:
            f.write(base64.decodestring(file))
            f.close()

    def action_get_annotation(self):
        self._cr.execute("delete from product_kks_pid_annotation where file_id = {}".format(self.id))
        self._cr.commit()
        results = self.env['product.image.directory'].search([('type', '=', 'reporting')])
        for result in results:
            directory = result.name
        self.write_file(self.filename, self.file, directory)
        doc = fitz.open(directory + self.filename)  # open the PDF
        page = doc[0]  # access page n (0-based)
        annot = page.firstAnnot  # get first annotation
        i = 0  # counter for file idents
        # loop through the page's annotations
        Liste = []
        while annot:
            i += 1  # increase counter
            d = annot.info  # get annot's info dictionary
            self.env['product.kks.pid.annotation'].create({'file_id': self.id,
                                                           'title': d['title'],
                                                           'content': d['content'],
                                                           'subject': d['subject'],
                                                           'name': d['name']})
            annot = annot.next  # get next annot on page
        return True


class product_kks_pid_annotation(models.Model):
    _name = 'product.kks.pid.annotation'
    _description = 'Annotations'

    file_id = fields.Many2one('product.kks.pid.file', 'Fichier')
    name = fields.Char('Type', readonly=True)
    title = fields.Char('Titre', readonly=True)
    content = fields.Char('Contenue', )
    subject = fields.Char('Sujet', readonly=True)

    def write_file(self, path, file):
        with open(path, 'wb') as f:
            f.write(base64.decodestring(file))
            f.close()
    def download_file(self, path, file_id):
        data=open(path, 'rb').read().encode('base64')
        results = self.env['product.kks.pid.file'].search([('id', '=', file_id)])
        results.write({'file' : data})
        return True

    def action_update_annotation(self):
        results = self.env['product.image.directory'].search([('type', '=', 'reporting')])
        for result in results:
            directory = result.name
        file_name= self.file_id.filename.split('.')[0]
        extension = self.file_id.filename.split('.')[1]
        file_data = self.file_id.file
        path = directory + file_name + str(time.strftime('%H%M%S')) + '.' + extension
        self.write_file(path, file_data)
        doc = fitz.open(path)  # open the PDF
        page = doc[0]  # access page n (0-based)
        annot = page.firstAnnot  # get first annotation
        i = 0  # counter for file idents
        # loop through the page's annotations
        Liste = []
        while annot:
            i += 1  # increase counter
            info = annot.info  # get annot's info dictionary
            if info["title"] == self.title:
                info["content"] = self.content
                print('update annotation {} with content {}'.format(self.title, self.content))
            annot.setInfo(info)
            annot.update()
            annot = annot.next  # get next annot on page
        path_out = directory + file_name + '.' + extension
        doc.save(path_out, garbage=4, deflate=True, clean=True)
        self.download_file(path_out, self.file_id.id)
        return True

    def action_view_annotation(self):
        results = self.env['product.image.directory'].search([('type', '=', 'reporting')])
        for result in results:
            directory = result.name
        file_name = self.file_id.filename.split('.')[0]
        extension = self.file_id.filename.split('.')[1]
        file_data = self.file_id.file
        path_file = directory+file_name+'.'+extension
        self.write_file(path_file, file_data)
        pdf_file = PdfFileReader(open(path_file, "rb"))
        page = pdf_file.getPage(0)
        print(page.cropBox.getLowerLeft())
        print(page.cropBox.getLowerRight())
        print(page.cropBox.getUpperLeft())
        print(page.cropBox.getUpperRight())

        with open(path_file, "rb") as in_f:
            input1 = PdfFileReader(in_f)
            output = PdfFileWriter()

            numPages = input1.getNumPages()
            print "document has %s pages." % numPages

            for i in range(numPages):
                page = input1.getPage(i)
                print page.mediaBox.getUpperRight_x(), page.mediaBox.getUpperRight_y()
                page.trimBox.lowerLeft = (0, 0)
                page.trimBox.upperRight = (100, 100)
                page.cropBox.lowerLeft = (0, 0)
                page.cropBox.upperRight = (2592, 1686)
                output.addPage(page)
            path_out = directory + file_name + time.strftime('%H%M%S')+'.' + extension
            with open(path_out, "wb") as out_f:
                output.write(out_f)
        return webbrowser.open_new(r'file://'+path_out)
