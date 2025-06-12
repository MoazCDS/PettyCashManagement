from odoo import models, fields, api
from odoo.api import onchange
from odoo.exceptions import ValidationError

class PettyCashReconciliation(models.Model):
    _name = "petty.cash.reconciliation"
    _description = "Petty Cash Reconciliation"

    reconciled_amount = fields.Float(compute="_compute_reconciled_amount", string="Reconciled Amount", readonly=True)

    vendor_bills_ids = fields.Many2many('account.move')
    attachment_ids = fields.Many2many   ('ir.attachment')
    petty_request_id = fields.Many2one('petty.cash.request', readonly=True)
    journal_entry_id = fields.Many2one('account.move', readonly=True)


    @api.depends('vendor_bills_ids.amount_total')
    def _compute_reconciled_amount(self):
        for rec in self:
            rec.reconciled_amount = sum(rec.vendor_bills_ids.mapped('amount_total'))


    def unlink(self):
        for rec in self:
            if rec.petty_request_id.state != 'draft':
                raise ValidationError("Petty cash request has to be draft to delete")
        return super().unlink()