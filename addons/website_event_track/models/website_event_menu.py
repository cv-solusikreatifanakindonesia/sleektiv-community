# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv import fields, models


class EventMenu(models.Model):
    _inherit = "website.event.menu"

    menu_type = fields.Selection(
        selection_add=[('track', 'Event Tracks Menus'), ('track_proposal', 'Event Proposals Menus')],
        ondelete={'track': 'cascade', 'track_proposal': 'cascade'})
