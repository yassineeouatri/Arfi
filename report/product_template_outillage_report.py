# -*- coding: utf-8 -*-

import time
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)


class ReportPRODUCTOUTILLAGE(models.AbstractModel):
    _name = "report.arfi.action_report_producttemplateoutillage"

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
        }
        return self.env["report"].render(
            "arfi.action_report_producttemplateoutillage", docargs
        )


class ReportPRODUCTOUTILLAGETARAGE(models.AbstractModel):
    _name = "report.arfi.action_report_producttemplateoutillagetarage"

    def _get_info(self, customer_id, arret_id):
        return {"customer": customer_id[1], "arret": arret_id[1]}

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
        }
        return self.env["report"].render(
            "arfi.action_report_producttemplateoutillagetarage", docargs
        )
