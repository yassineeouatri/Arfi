# -*- coding: utf-8 -*-

import time
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)


class ReportKKSOUTILLAGE(models.AbstractModel):
    _name = "report.arfi.action_report_productkksoutillage"

    def _get_info(self, customer_id, arret_id):
        return {"customer": customer_id[1], "arret": arret_id[1]}

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = self.env["product.kks.outillage.arret"].search(
            [
                ("customer_id", "=", docs.customer_id.id),
                ("arret_id", "=", docs.arret_id.id),
            ]
        )

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "records": records,
            "get_info": self._get_info(
                data["form"]["customer_id"], data["form"]["arret_id"]
            ),
        }
        return self.env["report"].render(
            "arfi.action_report_productkksoutillage", docargs
        )


class ReportKKSOUTILLAGETARAGE(models.AbstractModel):
    _name = "report.arfi.action_report_productkksoutillagetarage"

    def _get_info(self, customer_id, arret_id):
        return {"customer": customer_id[1], "arret": arret_id[1]}

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = self.env["product.kks.outillage.tarage.arret"].search(
            [
                ("customer_id", "=", docs.customer_id.id),
                ("arret_id", "=", docs.arret_id.id),
            ]
        )

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "records": records,
            "get_info": self._get_info(
                data["form"]["customer_id"], data["form"]["arret_id"]
            ),
        }
        return self.env["report"].render(
            "arfi.action_report_productkksoutillagetarage", docargs
        )
