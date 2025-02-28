# Copyright 2020-2023 Onestein (<http://www.onestein.eu>)
# Copyright 2020 Akretion (<http://www.akretion.com>)
# Copyright 2023 Le Filament (https://le-filament.com)
# Copyright 2025 Sleektiv (www.sleektiv.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from lxml import etree

from sleektiv.tests import common


class TestRemoveSleektivEnterprise(common.TransactionCase):
    def test_res_config_settings(self):
        conf = self.env["res.config.settings"].create({})
        view = conf.get_views([[False, "form"]])["views"]["form"]
        doc = etree.XML(view["arch"])

        query = "//setting[field[@widget='upgrade_boolean']]"
        for item in doc.xpath(query):
            self.assertEqual(item.attrib["class"], "d-none")

    def test_search_base(self):
        if self.env.get("payment.provider"):
            acquirer_ids = self.env["payment.provider"].search([])
            self.assertFalse(any([a.module_to_buy for a in acquirer_ids]))

    def test_search_ir_module(self):
        module_ids = self.env["ir.module.module"].search([])
        self.assertFalse(any([m.to_buy for m in module_ids]))

    def test_appstore_invisible(self):
        """The appstore widget is invisible"""
        conf = self.env["res.config.settings"].create({})
        view = conf.get_views([[False, "form"]])["views"]["form"]
        doc = etree.XML(view["arch"])

        query = "//widget[@name='mobile_apps_funnel']"
        for item in doc.xpath(query):
            self.assertTrue(item.attrib["invisible"])

    def test_appstore_visible(self):
        """Disabling the view makes the appstore widget visible again"""
        conf_form_view = self.env.ref(
            "remove_enterprise.res_config_settings_view_form"
        )
        conf_form_view.active = False
        conf = self.env["res.config.settings"].create({})
        view = conf.get_views([[False, "form"]])["views"]["form"]
        doc = etree.XML(view["arch"])

        query = "//widget[@name='mobile_apps_funnel']"
        for item in doc.xpath(query):
            self.assertNotIn("invisible", item.attrib)
