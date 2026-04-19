from frappe.tests.utils import FrappeTestCase

from omnexa_factoring.standards_profile import get_standards_profile


class TestFactoringStandardsProfile(FrappeTestCase):
	def test_standards_profile_minimum_baseline(self):
		profile = get_standards_profile()
		self.assertEqual(profile["app"], "omnexa_factoring")
		for s in ["IFRS", "BASEL_III_IV", "ISO_27001", "SOX"]:
			self.assertIn(s, profile["standards"])
		self.assertTrue(profile["multi_country_ready"])
		self.assertTrue(profile["activity_controls"])
