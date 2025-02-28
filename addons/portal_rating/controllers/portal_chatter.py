# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv.osv import expression

from sleektiv.addons.portal.controllers import mail


class PortalChatter(mail.PortalChatter):

    def _setup_portal_message_fetch_extra_domain(self, data):
        domains = [super()._setup_portal_message_fetch_extra_domain(data)]
        if data.get('rating_value', False) is not False:
            domains.append([('rating_value', '=', float(data['rating_value']))])
        return expression.AND(domains)
