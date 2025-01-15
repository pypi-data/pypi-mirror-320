# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestHideDiscountsByPartner(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super(TestHideDiscountsByPartner, cls).setUpClass()
        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Test partner 1",
                "show_discounts": False,
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
                "show_discounts": True,
            }
        )

    def test_child_partner_show_discounts(self):
        child = self.env["res.partner"].create(
            {"name": "Test partner", "parent_id": self.partner1.id}
        )
        self.assertEqual(
            child.show_discounts,
            self.partner1.show_discounts,
        )

    def test_invoice_creation(self):
        invoice = self._create_invoice(partner_id=self.partner1.id)
        self.assertEqual(invoice.show_discounts, self.partner1.show_discounts)

    def test_invoice_change_partner(self):
        invoice = self._create_invoice(partner_id=self.partner1.id)
        invoice.partner_id = self.partner2
        self.assertEqual(invoice.show_discounts, self.partner2.show_discounts)
