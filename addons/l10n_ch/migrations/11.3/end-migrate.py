# Part of Sleektiv. See LICENSE file for full copyright and licensing details.
from sleektiv import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for company in env["res.company"].search([("chart_template", "=", "ch")], order="parent_path"):
        env["account.chart.template"].try_loading("ch", company)
