# Part of Odoo, Sleektiv. See LICENSE file for full copyright and licensing details.

from sleektiv.tools import file_path

_directory = 'sale_pdf_quote_builder/tests/files/'

forms_pdf = file_path(_directory + 'test_forms.pdf', filter_ext=('.pdf',))
plain_pdf = file_path(_directory + 'test_plain.pdf', filter_ext=('.pdf',))
