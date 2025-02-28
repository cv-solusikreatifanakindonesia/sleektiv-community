# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv import fields, models


class PostReason(models.Model):
    _name = "forum.post.reason"
    _description = "Post Closing Reason"
    _order = 'name'

    name = fields.Char(string='Closing Reason', required=True, translate=True)
    reason_type = fields.Selection([('basic', 'Basic'), ('offensive', 'Offensive')], string='Reason Type', default='basic')
