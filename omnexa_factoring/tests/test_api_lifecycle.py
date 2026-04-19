from frappe.tests.utils import FrappeTestCase

from omnexa_factoring.api import (
	evaluate_lifecycle,
	fund_invoice,
	get_debtor_exposure_dashboard,
	record_collection_event,
	refresh_debtor_exposure,
	register_factoring_invoice,
	run_settlement,
	upsert_factoring_case,
)


class TestFactoringLifecycleApi(FrappeTestCase):
	def test_evaluate_lifecycle_api(self):
		out = evaluate_lifecycle(principal="100000", term_months=6, invoice_face_value="130000", debtor_concentration="0.20")
		self.assertIn("risk_score", out)
		self.assertIn("pricing_spread", out)
		self.assertIn("recommended_stage", out)

	def test_factoring_end_to_end(self):
		case = upsert_factoring_case(
			customer_name="Factoring Test",
			portfolio_id="PORT-A",
			principal="90000",
			term_months=6,
			invoice_face_value="120000",
			debtor_id="DEBTOR-1",
			debtor_concentration="0.22",
			recourse_type="NON_RECOURSE",
			debtor_rating="B",
			base_credit_score="680",
		)
		case_id = case["case_id"]
		self.assertTrue(case_id)
		invoice = register_factoring_invoice(case_id, "INV-001", "DEBTOR-1", "120000", "2030-12-31")
		self.assertTrue(invoice["invoice_id"])
		funding = fund_invoice(invoice["invoice_id"], "84000")
		self.assertEqual(funding["invoice_status"], "FUNDED")
		evt = record_collection_event(invoice["invoice_id"], "PAYMENT", "85000", "customer paid")
		self.assertTrue(evt["event_id"])
		st = run_settlement(case_id, "1000")
		self.assertTrue(st["settlement_run_id"])
		exp = refresh_debtor_exposure("DEBTOR-1", "PORT-A")
		self.assertIn(exp["risk_band"], ("LOW", "MEDIUM", "HIGH"))
		dash = get_debtor_exposure_dashboard()
		self.assertIn("top_debtors", dash)
