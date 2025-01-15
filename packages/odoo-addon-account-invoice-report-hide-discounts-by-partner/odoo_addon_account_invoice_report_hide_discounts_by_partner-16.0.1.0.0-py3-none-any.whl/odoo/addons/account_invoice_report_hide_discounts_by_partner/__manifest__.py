# Copyright 2025 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Report Hide Discounts by Partner",
    "summary": "Account Invoice Report Hide Discounts by Partner",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/sygel-technology/sy-account-invoice-reporting",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "reports/report_invoice.xml",
    ],
}
