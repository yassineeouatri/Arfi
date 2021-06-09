# -*- coding: utf-8 -*-

import time
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class ReportKKSFACTURE(models.AbstractModel):
    _name = "report.arfi.action_report_productkksfacture"

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        _logger.info("Model          " + self.model)
        _logger.info("Model          " + str(self.id))
        _logger.info("Model          " + str(docs))
        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "date": time.strftime("%A %d %b %Y"),
        }
        return self.env["report"].render(
            "arfi.action_report_productkksfacture", docargs
        )


class ReportKKSPV(models.AbstractModel):
    _name = "report.arfi.action_report_productkkspv"

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "date": time.strftime("%A %d %b %Y"),
        }
        return self.env["report"].render("arfi.action_report_productkkspv", docargs)


class ReportKKSFACTURECHANGEMENT(models.AbstractModel):
    _name = "report.arfi.action_report_productkksfacturechangement"

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "date": time.strftime("%A %d %b %Y"),
        }
        return self.env["report"].render(
            "arfi.action_report_productkksfacturechangement", docargs
        )


class ReportKKSPVCHANGEMENT(models.AbstractModel):
    _name = "report.arfi.action_report_productkkspvchangement"

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "date": time.strftime("%A %d %b %Y"),
        }
        return self.env["report"].render(
            "arfi.action_report_productkkspvchangement", docargs
        )
