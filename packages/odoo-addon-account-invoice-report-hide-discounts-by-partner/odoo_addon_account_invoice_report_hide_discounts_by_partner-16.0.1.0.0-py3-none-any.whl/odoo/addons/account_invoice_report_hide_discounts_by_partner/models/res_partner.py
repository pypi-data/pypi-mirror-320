# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    show_discounts = fields.Boolean(
        default=False,
        string="Show Discounts in Invoices",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["show_discounts"]
