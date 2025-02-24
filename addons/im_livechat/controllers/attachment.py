# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import NotFound

from sleektiv import _
from sleektiv.http import route, request
from sleektiv.addons.mail.controllers.attachment import AttachmentController
from sleektiv.exceptions import AccessError
from sleektiv.addons.mail.models.discuss.mail_guest import add_guest_to_context


class LivechatAttachmentController(AttachmentController):
    @route()
    @add_guest_to_context
    def mail_attachment_upload(self, ufile, thread_id, thread_model, is_pending=False, **kwargs):
        thread = request.env[thread_model]._get_thread_with_access(
            int(thread_id), mode=request.env[thread_model]._mail_post_access, **kwargs
        )
        if not thread:
            raise NotFound()
        if (
            thread_model == "discuss.channel"
            and thread.channel_type == "livechat"
            and not thread.livechat_active
            and not request.env.user._is_internal()
        ):
            raise AccessError(_("You are not allowed to upload attachments on this channel."))
        return super().mail_attachment_upload(ufile, thread_id, thread_model, is_pending, **kwargs)
