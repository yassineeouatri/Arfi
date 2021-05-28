# -*- coding: utf-8 -*-

import time
import logging
from odoo import api, models
from datetime import datetime


_logger = logging.getLogger(__name__)


class ReportOrderCustomer(models.AbstractModel):
    _name = "report.arfi.action_report_productordercustomer"

    @api.model
    def render_html(self, docids, data=None):
        _logger.info(2)
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        records = []
        orders = self.env["product.order"].search(
            [("customer_id", "=", docs.customer_id.id)]
        )
        _logger.info(orders)
        for order in orders:
            if order.date_next_ctr:
                year = datetime.strptime(order.date_next_ctr, "%Y-%m-%d").year
                if int(docs.year) == int(year):
                    records.append(order)
        _logger.info(orders)
        docargs = {
            "doc_ids": self.ids,
            "doc_model": self.model,
            "docs": docs,
            "time": time,
            "orders": records,
        }
        return self.env["report"].render(
            "arfi.action_report_productordercustomer", docargs
        )
