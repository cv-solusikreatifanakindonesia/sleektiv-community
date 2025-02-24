# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_sale_order_fields(self):
        field_names = super()._get_sale_order_fields()
        field_names.append('reward_id')
        return field_names
