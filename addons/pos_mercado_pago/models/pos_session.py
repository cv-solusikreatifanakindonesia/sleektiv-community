# Part of Sleektiv. See LICENSE file for full copyright and licensing details.
from sleektiv import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('mp_id_point_smart')
        return result
