from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

class PettyCashRequest(models.Model):
    _name = "petty.cash.request"
    _description = "Petty Cash Request"
    _rec_name = "employee_id"

    sequence = fields.Char(string="Name", default="New")
    request_date = fields.Date(string="Date")
    amount_request = fields.Float(string="Amount")
    purpose = fields.Text(string="Purpose")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled'),
    ], default='draft')
    remaining_amount = fields.Float(compute="_compute_remaining_amount", string="Remaining amount", readonly=True)
    month = fields.Integer(compute="_compute_month", string="Month", store=True)

    employee_id = fields.Many2one('hr.employee', required=True, string="Employee")
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    reconciliation_ids = fields.One2many('petty.cash.reconciliation','petty_request_id',string="Reconciliations")

    def print_custom_pdf(self):
        return self.env.ref('petty_cash_management.petty_cash_report').report_action(self)


    @api.model
    def create(self, vals):
        res = super(PettyCashRequest, self).create(vals)
        if res.amount_request == 0:
            raise ValidationError("The Amount Can't Be 0")
        if res.sequence == 'New':
            res.sequence = self.env['ir.sequence'].next_by_code('petty_cash_seq')
        return res

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_submitted(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

    def action_paid(self):
        for rec in self:
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,
                'date': rec.request_date,
                'ref': f"Petty Cash for {rec.employee_id.name}",
                'line_ids': [
                    (0, 0, {
                        'account_id': rec.journal_id.default_account_id.id,
                        'debit': rec.amount_request,
                        'credit': 0.0,
                        'name': 'Petty Cash Allocation',
                    }),
                    (0, 0, {
                        'account_id': rec.journal_id.default_account_id.id,
                        'debit': 0.0,
                        'credit': rec.amount_request,
                        'name': 'Cash Payment',
                    }),
                ],
            })
            reconciliation = self.env['petty.cash.reconciliation'].create({
                'petty_request_id': rec.id,
                'journal_entry_id': move.id,
            })
            move.state = 'posted'
            rec.state = 'paid'

    def action_reconciled(self):
        for rec in self:
            rec.state = 'reconciled'

    @api.depends("request_date")
    def _compute_month(self):
        for rec in self:
            rec.month = rec.request_date.month

    @api.depends("amount_request", "reconciliation_ids.reconciled_amount")
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.amount_request - rec.reconciliation_ids.reconciled_amount