# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv import fields, models


class ResPartnerActivation(models.Model):
    _name = 'res.partner.activation'
    _order = 'sequence'
    _description = 'Partner Activation'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
