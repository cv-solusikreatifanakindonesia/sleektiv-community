# Part of Sleektiv. See LICENSE file for full copyright and licensing details.
from sleektiv import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    employee_id = fields.Many2one('hr.employee', string="Employee", help="The employee who made the cash move.")
