from frappe.tests.utils import FrappeTestCase

from omnexa_factoring.api import get_regulatory_dashboard


class TestFactoringRegulatoryDashboard(FrappeTestCase):
	def test_get_regulatory_dashboard(self):
		out = get_regulatory_dashboard()
		self.assertEqual(out["app"], "omnexa_factoring")
		self.assertIn("standards", out)
		self.assertIn("governance", out)
		self.assertIn("compliance_score", out)
		self.assertGreaterEqual(out["compliance_score"], 0)
