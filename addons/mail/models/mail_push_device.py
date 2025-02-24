# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

import json
import logging as logger

from sleektiv import api, fields, models
from ..tools.jwt import generate_vapid_keys, InvalidVapidError

_logger = logger.getLogger(__name__)


class MailPushDevice(models.Model):
    _name = 'mail.push.device'
    _description = "Push Notification Device"

    partner_id = fields.Many2one(
        'res.partner', string='Partner', index=True, required=True,
        default=lambda self: self.env.user.partner_id)
    endpoint = fields.Char(string='Browser endpoint', required=True)
    keys = fields.Char(string='Browser keys', required=True,
                       help=("It's refer to browser keys used by the notification: \n"
                             "- p256dh: It's the subscription public key generated by the browser. The browser will \n"
                             "          keep the private key secret and use it for decrypting the payload\n"
                             "- auth: The auth value should be treated as a secret and not shared outside of Sleektiv"))
    expiration_time = fields.Datetime(string='Expiration Token Date')

    _sql_constraints = [('endpoint_unique', 'unique(endpoint)', 'The endpoint must be unique !')]

    @api.model
    def get_web_push_vapid_public_key(self):
        ir_params_sudo = self.env['ir.config_parameter'].sudo()
        public_key = 'mail.web_push_vapid_public_key'
        public_key_value = ir_params_sudo.get_param(public_key)
        # Regenerate new Keys if public key not present
        if not public_key_value:
            self.sudo().search([]).unlink()  # Reset all devices (ServiceWorker)
            private_key_value, public_key_value = generate_vapid_keys()
            ir_params_sudo.set_param('mail.web_push_vapid_private_key', private_key_value)
            ir_params_sudo.set_param(public_key, public_key_value)
            _logger.info("WebPush: missing public key, new VAPID keys generated")
        return public_key_value

    @api.model
    def register_devices(self, **kw):
        sw_vapid_public_key = kw.get('vapid_public_key')
        valid_sub = self._verify_vapid_public_key(sw_vapid_public_key)
        if not valid_sub:
            raise InvalidVapidError("Invalid VAPID public key")
        endpoint = kw.get('endpoint')
        browser_keys = kw.get('keys')
        if not endpoint or not browser_keys:
            return
        search_endpoint = kw.get('previousEndpoint', endpoint)
        mail_push_device = self.sudo().search([('endpoint', '=', search_endpoint)])
        if mail_push_device:
            if mail_push_device.partner_id is not self.env.user.partner_id:
                mail_push_device.write({
                    'endpoint': endpoint,
                    'expiration_time': kw.get('expirationTime'),
                    'keys': json.dumps(browser_keys),
                    'partner_id': self.env.user.partner_id,
                })
        else:
            self.sudo().create([{
                'endpoint': endpoint,
                'expiration_time': kw.get('expirationTime'),
                'keys': json.dumps(browser_keys),
                'partner_id': self.env.user.partner_id.id,
            }])

    @api.model
    def unregister_devices(self, **kw):
        endpoint = kw.get('endpoint')
        if not endpoint:
            return
        mail_push_device = self.sudo().search([
            ('endpoint', '=', endpoint)
        ])
        if mail_push_device:
            mail_push_device.unlink()

    def _verify_vapid_public_key(self, sw_public_key):
        ir_params_sudo = self.env['ir.config_parameter'].sudo()
        db_public_key = ir_params_sudo.get_param('mail.web_push_vapid_public_key')
        return db_public_key == sw_public_key
