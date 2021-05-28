# -*- coding: utf-8 -*-

import time
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)


class ReportKKSEchafaudage(models.AbstractModel):
    _name = "report.arfi.action_report_productkksechafaudage"

    @api.model
    def render_html(self, docids, data=None):

        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = []

        records = self.env["product.kks.echafaudage"].search([("kks_id", "=", docs.id)])

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "records": records,
            "time": time,
        }
        return self.env["report"].render(
            "arfi.action_report_productkksechafaudage", docargs
        )


class ReportKKSEchafaudageArret(models.AbstractModel):
    _name = "report.arfi.action_report_productkksechafaudagearret"

    def _get_info(self, customer_id, arret_id):
        return {"customer": customer_id[1], "arret": arret_id[1]}

    @api.model
    def render_html(self, docids, data=None):

        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = self.env["product.kks.echafaudage.arret"].search(
            [
                ("customer_id", "=", docs.customer_id.id),
                ("arret_id", "=", docs.arret_id.id),
            ]
        )

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "records": records,
            "get_info": self._get_info(
                data["form"]["customer_id"], data["form"]["arret_id"]
            ),
            "time": time,
        }
        return self.env["report"].render(
            "arfi.action_report_productkksechafaudagearret", docargs
        )


class ReportKKSFactureEchafaudageArret(models.AbstractModel):
    _name = "report.arfi.action_report_productkksfactureechafaudagearret"

    def _get_info(self, customer_id, arret_id):
        return {"customer": customer_id[1], "arret": arret_id[1]}

    @api.model
    def render_html(self, docids, data=None):

        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = self.env["product.kks.facture.echafaudage.arret"].search(
            [
                ("customer_id", "=", docs.customer_id.id),
                ("arret_id", "=", docs.arret_id.id),
            ]
        )
        unite = ""
        if records:
            unite = records[0].unite_id.code
        _logger.info("Unite" + str(unite))

        date = time.strftime("%A %d %b %Y")
        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "records": records,
            "unite": unite,
            "date": date,
            "get_info": self._get_info(
                data["form"]["customer_id"], data["form"]["arret_id"]
            ),
            "time": time,
        }
        return self.env["report"].render(
            "arfi.action_report_productkksfactureechafaudagearret", docargs
        )
