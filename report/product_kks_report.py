# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class product_kks_report(models.Model):

    _name = "product.kks.report"
    _description = "KKS report"
    _auto = False

    kks_id = fields.Many2one('product.kks','KKS',readonly=True)
    ref_fab = fields.Char('Réf fabriquant',readonly=True)
    ref_com = fields.Char('Réf Commercial',readonly=True)
    reference = fields.Char('Référence',readonly=True)
    customer_id = fields.Many2one('res.partner','Client',readonly=True)
    maker_id = fields.Many2one('product.template.maker','Marque',readonly=True)
    ss_type_appareil_id = fields.Many2one('product.category','Sous Type Appareil' ,readonly=True)
    designation = fields.Char('Désignation',readonly=True)
    item = fields.Integer('Item',readonly=True)
    type = fields.Char('Type',readonly=True)
    magasin_id = fields.Many2one('product.magasin', 'Code Magasin',readonly=True)
    unite_id = fields.Many2one('product.unite','Code Unité',readonly=True)
    travaux_id = fields.Many2one('product.travaux','Travaux',readonly=True)
    arret_id = fields.Many2one('product.arret','Code Arrêt',readonly=True)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_report')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_report as (
                SELECT
                    row_number() OVER () as id,t.*
                FROM (
                    select customer_id,kp.magasin_id,item,k.id as kks_id,ss_type_appareil_id,pc.description as type,maker_id,concat('- REP: ',pp.no_piece,' ',pp.name) as designation,
                    ref_fab,ref_com,reference,(select id from product_unite limit 1) as unite_id,
                    (select id from product_travaux limit 1) as travaux_id,
                     (select id from product_arret limit 1) as arret_id
                    from product_kks k
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_category pc on pc.id=k.ss_type_appareil_id
                    left join product_piece pp on pp.id=kp.piece_id
                    group by customer_id,kp.magasin_id,item,k.id,ss_type_appareil_id,pc.description,maker_id,concat('- REP: ',pp.no_piece,' ',pp.name),
                    ref_fab,ref_com,reference) as t


            )
        """)
    def action_kks(self):
   
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.kks',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.kks_id.id,
            'views': [(self.env.ref('arfi.product_kks_view_form').id, 'form')],
             }
    def action_supplier(self):
   
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.magasin',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.magasin_id.id,
            'views': [(self.env.ref('arfi.product_magasin_form_view').id, 'form')],
             }
class product_ref_fab(models.Model):

    _name = "product.ref.fab"
    _description = "Ref Fab"
    _order = 'name'
    _auto = False

    name = fields.Char('Réf Fabriquant')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_ref_fab')
        self._cr.execute("""
            CREATE or REPLACE view product_ref_fab as (
                SELECT row_number() OVER () as id,t.*
                      FROM (select distinct ref_fab as name from product_kks_piece order by ref_fab) as t
            )
        """)
class product_ref_com(models.Model):

    _name = "product.ref.com"
    _description = "Ref Com"
    _order = 'name'
    _auto = False

    name = fields.Char('Réf Commercial')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_ref_com')
        self._cr.execute("""
            CREATE or REPLACE view product_ref_com as (
                SELECT row_number() OVER () as id,t.*
                      FROM (select distinct ref_com as name from product_kks_piece order by ref_com) as t
            )
        """)
class product_kks_magasin_report(models.Model):

    _name = "product.kks.magasin.report"
    _description = "Product KKs Magasin Report"
    _auto = False

    magasin_id = fields.Many2one('product.magasin', 'Code Magasin')
    magasin = fields.Char('Magasin')
    qte_installe = fields.Char('Qté Installée')
    stock = fields.Char('Stock')
    absolue = fields.Char('Absolue')
    necessaire = fields.Char('Nécessaire')
    recommander = fields.Char('Recommander')
    securite = fields.Char('Sécurité')
    qte_a_sortir = fields.Char('Qté à sortir')
    qte_a_commander = fields.Char('Qté à commander')
    qte_commander = fields.Char('Qté commander')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_magasin_report')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_magasin_report as (
                  select row_number() OVER () as id,t.*
                FROM (
                    select id as magasin_id,magasin,string_agg(qte_installe,'') as qte_installe,string_agg(stock,'') as stock,string_agg(absolue,'') as absolue,
                            string_agg(necessaire,'') as necessaire,string_agg(recommander,'') as recommander,string_agg(securite,'') as securite,
                            string_agg(qte_a_sortir,'') as qte_a_sortir,string_agg(qte_a_commander,'') as qte_a_commander,string_agg(qte_commander,'') as qte_commander
                    from(
                    select mag.id,a.magasin_id,mag.code as magasin,
                    (case when info.name like 'Qté instalée' then value else '' end ) as qte_installe,
                    (case when info.name like 'Stock' then value else '' end ) as stock,
                    (case when info.name like 'Absolue' then value else '' end ) as absolue,
                    (case when info.name like 'Nécessaire' then value else '' end ) as necessaire,
                    (case when info.name like 'Recommandé' then value else '' end ) as recommander,
                    (case when info.name like 'Sécurité' then value else '' end ) as securite,
                    (case when info.name like 'Quantité à sortir' then value else '' end ) as qte_a_sortir,
                    (case when info.name like 'Quantité à commander' then value else '' end ) as qte_a_commander,
                    (case when info.name like 'Quantité commander' then value else '' end ) as qte_commander
                    from product_magasin mag
                    left join product_kks_stock a on mag.id=a.magasin_id
                    left join product_info info on info.id=a.info_id)as tab
                    group by id,magasin) as t
            )
        """)
class product_kks_pdr_report(models.Model):

    _name = "product.kks.pdr.report"
    _description = "Product KKs PDR Report"
    _auto = False

    reference = fields.Char('Référence')
    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    item = fields.Integer('Item')
    magasin_id = fields.Many2one('product.magasin', 'Code Magasin')
    maker_id = fields.Many2one('product.template.maker','Marque')
    unite_id = fields.Many2one('product.unite','Code Unité')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    qte_installe = fields.Char('Qté Installée')
    stock = fields.Char('Stock')
    absolue = fields.Char('Absolue')
    necessaire = fields.Char('Nécessaire')
    recommander = fields.Char('Recommander')
    securite = fields.Char('Sécurité')
    qte_a_sortir = fields.Char('Qté à sortir')
    qte_a_commander = fields.Char('Qté à commander')
    qte_commander = fields.Char('Qté commander')
    choice = fields.Boolean('Choix')
    nbr2 = fields.Float('PDR total')
    nbr3 = fields.Float('PDR A sortir')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_pdr_report')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_pdr_report as (
                SELECT
                    row_number() OVER () as id,t.*
                FROM (
                   select t1.*,t2.nbr2,t3.nbr3 from ( select choice, customer_id,concat('- REP: ',pp.no_piece,' ',pp.name) as designation,item,k.name as kks,reference,kp.magasin_id,maker_id,unite_id,arret_id,
                    qte_installe,stock,absolue,necessaire,recommander,securite,qte_a_sortir,qte_a_commander,qte_commander ,mag.code as magasin
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_piece pp on pp.id=kp.piece_id
                    inner join product_kks_magasin_report pkmr on kp.magasin_id=pkmr.magasin_id
                    inner join product_magasin mag on mag.id=kp.magasin_id
                    order by mag.code,k.name)as t1
                    left join
                (select kp.magasin_id,customer_id,arret_id,count(*) as nbr2
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_piece pp on pp.id=kp.piece_id
                    inner join product_kks_magasin_report pkmr on kp.magasin_id=pkmr.magasin_id
                    group by kp.magasin_id,customer_id,arret_id) as t2 on t1.magasin_id=t2.magasin_id and t1.customer_id=t2.customer_id and t1.arret_id=t2.arret_id
                left join
                (select kp.magasin_id,customer_id,arret_id,count(*) as nbr3
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_piece pp on pp.id=kp.piece_id
                    inner join product_kks_magasin_report pkmr on kp.magasin_id=pkmr.magasin_id
                    where choice='t'
                    group by kp.magasin_id,customer_id,arret_id) as t3 on t1.magasin_id=t3.magasin_id and t1.customer_id=t3.customer_id and t1.arret_id=t3.arret_id
                order by magasin,kks

                     ) as t

            )
        """)
class product_kks_pdr_full_report(models.Model):

    _name = "product.kks.pdr.full.report"
    _description = "Product KKs PDR FullReport"
    _order = 'id'
    _auto = False

    reference = fields.Char('Référence')
    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    item = fields.Integer('Item')
    magasin_id = fields.Many2one('product.magasin', 'Code Magasin')
    maker_id = fields.Many2one('product.template.maker','Marque')
    unite_id = fields.Many2one('product.unite','Code Unité')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    qte_installe = fields.Char('Qté Installée')
    stock = fields.Char('Stock')
    absolue = fields.Char('Absolue')
    necessaire = fields.Char('Nécessaire')
    recommander = fields.Char('Recommander')
    securite = fields.Char('Sécurité')
    qte_a_sortir = fields.Char('Qté à sortir')
    qte_a_commander = fields.Char('Qté à commander')
    qte_commander = fields.Char('Qté commander')
    choice = fields.Boolean('Choix')
    nbr = fields.Float('PDR total')
    row = fields.Float('PDR total')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_pdr_full_report')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_pdr_full_report as (
               SELECT
                    row_number() OVER () as id,row_number() over (partition by customer_id,arret_id,magasin) as row,t.*
                FROM (select t1.*,t2.nbr from ( select choice, customer_id,concat('- REP: ',pp.no_piece,' ',pp.name) as designation,item,k.name as kks,reference,kp.magasin_id,maker_id,unite_id,arret_id,
                    qte_installe,stock,absolue,necessaire,recommander,securite,qte_a_sortir,qte_a_commander,qte_commander ,pkmr.magasin
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_piece pp on pp.id=kp.piece_id
                    inner join product_kks_magasin_report pkmr on kp.magasin_id=pkmr.magasin_id
                    order by pkmr.magasin,k.name
                    )as t1
                left join
                (select kp.magasin_id,customer_id,arret_id,count(*) as nbr
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    group by kp.magasin_id,customer_id,arret_id) as t2 on t1.magasin_id=t2.magasin_id and t1.customer_id=t2.customer_id and t1.arret_id=t2.arret_id
                order by customer_id,arret_id,magasin,kks) as t
            )
        """)
class product_kks_pdr_sortir_report(models.Model):

    _name = "product.kks.pdr.sortir.report"
    _description = "Product KKs PDR sortir Report"
    _auto = False

    reference = fields.Char('Référence')
    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    item = fields.Integer('Item')
    magasin_id = fields.Many2one('product.magasin', 'Code Magasin')
    maker_id = fields.Many2one('product.template.maker','Marque')
    unite_id = fields.Many2one('product.unite','Code Unité')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    qte_installe = fields.Char('Qté Installée')
    stock = fields.Char('Stock')
    absolue = fields.Char('Absolue')
    necessaire = fields.Char('Nécessaire')
    recommander = fields.Char('Recommander')
    securite = fields.Char('Sécurité')
    qte_a_sortir = fields.Char('Qté à sortir')
    qte_a_commander = fields.Char('Qté à commander')
    qte_commander = fields.Char('Qté commander')
    choice = fields.Boolean('Choix')
    nbr = fields.Float('PDR total')
    row = fields.Float('PDR total')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_pdr_sortir_report')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_pdr_sortir_report as (
               SELECT
                    row_number() OVER () as id,row_number() over (partition by customer_id,arret_id,magasin) as row,t.*
                FROM (select t1.*,t2.nbr from ( select choice, customer_id,concat('- REP: ',pp.no_piece,' ',pp.name) as designation,item,k.name as kks,reference,kp.magasin_id,maker_id,unite_id,arret_id,
                    qte_installe,stock,absolue,necessaire,recommander,securite,qte_a_sortir,qte_a_commander,qte_commander ,pkmr.magasin
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    left join product_piece pp on pp.id=kp.piece_id
                    inner join product_kks_magasin_report pkmr on kp.magasin_id=pkmr.magasin_id
                    where choice='t'
                    order by pkmr.magasin,k.name
                    )as t1
                left join
                (select kp.magasin_id,customer_id,arret_id,count(*) as nbr
                    from product_kks k
                    inner join product_kks_arret ka on k.id=ka.kks_id
                    inner join product_kks_piece kp on k.id=kp.kks_id
                    where choice='t'
                    group by kp.magasin_id,customer_id,arret_id) as t2 on t1.magasin_id=t2.magasin_id and t1.customer_id=t2.customer_id and t1.arret_id=t2.arret_id
                order by customer_id,arret_id,magasin,kks) as t
            )
        """)        
class product_kks_echafaudage_arret(models.Model):

    _name = "product.kks.echafaudage.arret"
    _description = "Product KKs Echafaudage Arret"
    _auto = False
    
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)])
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    echafaudage_id = fields.Many2one('product.echafaudage','Code Echafaudage')
    qte = fields.Integer('Qte') 
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_echafaudage_arret')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_echafaudage_arret as (
                  select row_number() OVER () as id,t.*
                FROM (
                    select k.customer_id,ka.arret_id,ke.echafaudage_id,sum(ke.qte) as qte
                    from product_kks k
                    left join product_kks_arret ka on k.id=ka.kks_id
                    left join product_kks_echafaudage ke on ke.kks_id=k.id
                    inner join product_echafaudage pe on pe.id=ke.echafaudage_id
                    group by k.customer_id,ka.arret_id,ke.echafaudage_id) as t
            )
        """)
class product_kks_outillage_arret(models.Model):

    _name = "product.kks.outillage.arret"
    _description = "Product KKs Outillage Arret"
    _auto = False
    
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)])
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    outillage_id = fields.Many2one('product.outillage','Code Outillage')
    qte = fields.Integer('Qte à sortir') 
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_outillage_arret')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_outillage_arret as (
                  select row_number() OVER () as id,t.*
                FROM (
                    select arret_id,customer_id,outillage_id,sum(qte) as qte from product_kks k
                    left join product_kks_arret pka on k.id=kks_id
                    left join product_appareil_outillage pao on pao.reference=k.reference
                    where outillage_id is not null
                    group by arret_id,customer_id,outillage_id) as t
            )
        """)
class product_kks_outillage_tarage_arret(models.Model):

    _name = "product.kks.outillage.tarage.arret"
    _description = "Product KKs Outillage Tarage Arret"
    _auto = False
    
    customer_id = fields.Many2one('res.partner','Client',domain=[('customer','=',True)])
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    outillage_id = fields.Many2one('product.outillage','Code Outillage')
    qte = fields.Integer('Qte à sortir') 

    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_outillage_tarage_arret')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_outillage_tarage_arret as (
                  select row_number() OVER () as id,t.*
                FROM (
                     select arret_id,customer_id,outillage_id,sum(qte) as qte from product_kks k
                    left join product_kks_arret pka on k.id=kks_id
                    left join product_appareil_outillage_tarage pao on pao.reference=k.reference
                    where outillage_id is not null
                    group by arret_id,customer_id,outillage_id
                    ) as t
            )
        """)
class product_kks_facture_arret(models.Model):

    _name = "product.kks.facture.arret"
    _description = "Product KKs Facture Arret"
    _auto = False
    
    reference = fields.Char('Référence')
    kks_id = fields.Many2one('product.kks','KKS')
    item = fields.Integer('Item')
    maker_id = fields.Many2one('product.template.maker','Marque')
    unite_id = fields.Many2one('product.unite','Code Unité')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    nature_id = fields.Many2one('product.nature','Nature Travaux')
    travaux_id = fields.Many2one('product.travaux','Travaux')
    montant = fields.Float('Montant (Dhs)')
    fact = fields.Selection([('Contrat','Contrat'),('BC','BC')],'Fact')
    ss_type_appareil_id = fields.Many2one('product.category','Sous Type Appareil' )
    implantation_id = fields.Many2one('product.implantation', 'Implantation')
    type_implantation_id = fields.Many2one('product.type.implantation', 'Type Implantation')
    repere = fields.Float('Métrage(m3)')
    ligne = fields.Integer('N° Ligne Contrat')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_facture_arret')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_facture_arret as (
                  select row_number() OVER () as id,t.*
                FROM (
                    select k.id as kks_id,k.repere,type_implantation_id,implantation_id,k.ss_type_appareil_id,k.item,k.reference,ka.unite_id,k.maker_id,k.customer_id,ka.arret_id,kt.fact,kt.nature_id,kt.choice,kt.montant,ka.travaux_id,kt.ligne
                    from product_kks k
                    left join product_kks_arret ka on k.id=ka.kks_id
                    left join product_kks_tarif kt on kt.kks_id=k.id
                    where kt.choice='t'
                    ) as t
            )
        """)
class product_kks_facture_echafaudage_arret(models.Model):

    _name = "product.kks.facture.echafaudage.arret"
    _description = "Product KKs Facture Echafaudage Arret"
    _auto = False
    
    kks_id = fields.Many2one('product.kks','KKS')
    unite_id = fields.Many2one('product.unite','Code Unité')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    fact = fields.Selection([('Contrat','Contrat'),('BC','BC')],'Fact')
    repere = fields.Float('Métrage(m3)')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_facture_echafaudage_arret')
        self._cr.execute("""
            CREATE or REPLACE view product_kks_facture_echafaudage_arret as (
                  select row_number() OVER () as id,t.*
                FROM (
                    select distinct k.id as kks_id,k.repere,k.customer_id,ka.arret_id,unite_id,fact
                    from product_kks k
                    left join product_kks_arret ka on k.id=ka.kks_id
                    left join product_kks_tarif kt on kt.kks_id=k.id
                    where kt.choice='t' and repere>0
                    ) as t
            )
        """)
class product_kks_appel_commande_report(models.Model):

    _name = "product.kks.appel.commande.report"
    _description = "Product KKs Appel commande Report"
    _auto = False

    kks = fields.Char('KKS')
    designation = fields.Char('Désignation')
    code = fields.Char('Code')
    item = fields.Integer('Item')
    customer_id = fields.Many2one('res.partner','Client')
    arret_id = fields.Many2one('product.arret','Code Arrêt')
    qte = fields.Char('Qte')
    price = fields.Float('Prix H.T')
    no_ligne = fields.Char('N Ligne')
    contrat = fields.Char('Contrat')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kks_appel_commande_report')
        self._cr.execute("""
                CREATE or REPLACE view product_kks_appel_commande_report as (
                SELECT row_number() OVER () as id,t.*
                    from (
                        select pksp.no_ligne,pm.code,pm.id as magasin_id,max(pk.name) as kks,
                            concat('- REP: ',pp.no_piece,' ',pp.name) as designation,arret_id,max(item) as item,customer_id,stock.qte qte,
                            pksp.price,'avec' as contrat
                        from product_kks as pk
                        left join product_kks_arret pka on pk.id=pka.kks_id
                        inner join product_kks_piece pkp on pka.kks_id=pkp.kks_id
                        left join product_magasin pm on pm.id=pkp.magasin_id
                        left join product_piece pp on pp.id=pkp.piece_id
                        left join product_kks_supplier pksp  on pksp.magasin_id=pm.id
                        left join (select magasin_id,value as qte from product_kks_stock pks 
                            inner join product_info pi on pi.id=pks.info_id
                            and pi.name like 'Quantité à commander'	) as stock on stock.magasin_id=pm.id
                        where pkp.appel_commande = 't'
                        and pksp.no_ligne is not null 
                        and pksp.no_ligne not like ''
                        group by pksp.no_ligne,pm.code,pm.id,pp.no_piece,pp.name,arret_id,customer_id,stock.qte,pksp.price
                        union
                        select '',pm.code,pm.id as magasin_id,max(pk.name) as kks,
                            concat('- REP: ',pp.no_piece,' ',pp.name) as designation,arret_id,max(item) as item,customer_id,stock.qte qte,
                            pksp.price,'hors' as contrat
                        from product_kks as pk
                        left join product_kks_arret pka on pk.id=pka.kks_id
                        inner join product_kks_piece pkp on pka.kks_id=pkp.kks_id
                        left join product_magasin pm on pm.id=pkp.magasin_id
                        left join product_piece pp on pp.id=pkp.piece_id
                        left join product_kks_supplier pksp  on pksp.magasin_id=pm.id
                        left join (select magasin_id,value as qte from product_kks_stock pks 
                            inner join product_info pi on pi.id=pks.info_id
                            and pi.name like 'Quantité à commander'	) as stock on stock.magasin_id=pm.id
                        where pkp.appel_commande = 't'
                        and pm.id not in (select distinct magasin_id from product_kks_supplier where no_ligne is not null and no_ligne not like '')
                        group by pksp.no_ligne,pm.code,pm.id,pp.no_piece,pp.name,arret_id,customer_id,stock.qte,pksp.price
                        order by kks)
                    as t)
        """)        
