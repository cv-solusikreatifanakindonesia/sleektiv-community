# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv.tests import Form, TransactionCase, tagged

@tagged('-at_install', 'post_install')
class TestFormCreate(TransactionCase):

    def test_create_res_lang(self):
        lang_form = Form(self.env['res.lang'])
        lang_form.url_code = 'LANG'
        lang_form.name = 'a lang name'
        lang_form.code = 'a lang code'
        lang_form.save()
