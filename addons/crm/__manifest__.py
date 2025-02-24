# -*- coding: utf-8 -*-
# Part of Odoo, Sleektiv. See LICENSE file for full copyright and licensing details.


{
    'name': 'CRM',
    'version': '1.8',
    'category': 'Sales/CRM',
    'sequence': 15,
    'summary': 'Track leads and close opportunities',
    'website': 'https://sleektiv.com/app/crm',
    'depends': [
        'base_setup',
        'sales_team',
        'mail',
        'calendar',
        'resource',
        'utm',
        'web_tour',
        'contacts',
        'digest',
        'phone_validation',
    ],
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',

        'data/crm_lead_merge_template.xml',
        'data/crm_lead_prediction_data.xml',
        'data/crm_lost_reason_data.xml',
        'data/crm_stage_data.xml',
        'data/crm_team_data.xml',
        'data/digest_data.xml',
        'data/ir_action_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/crm_recurring_plan_data.xml',
        'data/crm_tour.xml',

        'wizard/crm_lead_lost_views.xml',
        'wizard/crm_lead_to_opportunity_views.xml',
        'wizard/crm_lead_to_opportunity_mass_views.xml',
        'wizard/crm_merge_opportunities_views.xml',
        'wizard/crm_lead_pls_update_views.xml',

        'views/calendar_views.xml',
        'views/crm_recurring_plan_views.xml',
        'views/crm_lost_reason_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_member_views.xml',
        'views/digest_views.xml',
        'views/mail_activity_plan_views.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/utm_campaign_views.xml',
        'report/crm_activity_report_views.xml',
        'report/crm_opportunity_report_views.xml',
        'views/crm_team_views.xml',
        'views/crm_menu_views.xml',
        'views/crm_helper_templates.xml',
    ],
    'demo': [
        'data/crm_team_demo.xml',
        'data/mail_template_demo.xml',
        'data/crm_team_member_demo.xml',
        'data/mail_activity_type_demo.xml',
        'data/crm_lead_demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'crm/static/src/**',
            ('remove', 'crm/static/src/views/forecast_graph/**'),
            ('remove', 'crm/static/src/views/forecast_pivot/**'),
        ],
        'web.assets_backend_lazy': [
            'crm/static/src/views/forecast_graph/**',
            'crm/static/src/views/forecast_pivot/**',
        ],
        'web.assets_tests': [
            'crm/static/tests/tours/**/*',
        ],
        'web.assets_unit_tests': [
            'crm/static/tests/mock_server/**/*',
            'crm/static/tests/crm_test_helpers.js'
        ],
        'web.qunit_suite_tests': [
            'crm/static/tests/**/*',
            ('remove', 'crm/static/tests/tours/**/*'),
            ('remove', 'crm/static/tests/mock_server/**/*'),
            ('remove', 'crm/static/tests/crm_test_helpers.js')
        ],
    },
    'license': 'LGPL-3',
}
