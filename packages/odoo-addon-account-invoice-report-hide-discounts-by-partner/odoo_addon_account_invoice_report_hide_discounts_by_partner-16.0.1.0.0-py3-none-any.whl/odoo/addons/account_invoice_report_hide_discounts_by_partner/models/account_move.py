# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    show_discounts = fields.Boolean(
        compute="_compute_show_discounts",
        store=True,
        readonly=False,
        string="Show Discounts in Invoice",
    )

    @api.depends("partner_id")
    def _compute_show_discounts(self):
        for sel in self:
            res = False
            if sel.partner_id:
                res = sel.partner_id.show_discounts
            sel.show_discounts = res
