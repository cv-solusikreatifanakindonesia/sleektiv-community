# Part of Odoo, Sleektiv. See LICENSE file for full copyright and licensing details.

from . import models
from . import controllers
from . import utils

from sleektiv.addons.payment import reset_payment_provider


def uninstall_hook(env):
    reset_payment_provider(env, 'custom', custom_mode='on_site')
