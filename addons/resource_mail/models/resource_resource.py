# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv import fields, models


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    im_status = fields.Char(related='user_id.im_status')
