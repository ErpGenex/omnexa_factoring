from decimal import Decimal

from frappe.tests.utils import FrappeTestCase

from omnexa_factoring.engine import FactoringCase, evaluate_lifecycle_case


class TestFactoringLifecycleEngine(FrappeTestCase):
	def test_evaluate_lifecycle_case(self):
		c = FactoringCase(principal=Decimal("100000"), term_months=36, invoice_face_value=Decimal("130000"), debtor_concentration=Decimal("0.20"))
		out = evaluate_lifecycle_case(c)
		self.assertIn(out.recommended_stage, ("ORIGINATION", "APPROVAL", "SERVICING", "WATCHLIST"))
		self.assertGreaterEqual(out.risk_score, Decimal("0"))

	def test_non_recourse_high_pd_case(self):
		c = FactoringCase(
			principal=Decimal("180000"),
			term_months=8,
			invoice_face_value=Decimal("200000"),
			debtor_concentration=Decimal("0.40"),
			recourse_type="NON_RECOURSE",
			debtor_rating="C",
			credit_risk_pd=Decimal("0.09"),
			invoice_count=80,
		)
		out = evaluate_lifecycle_case(c)
		self.assertGreater(out.funding_amount, Decimal("0"))
		self.assertIn("NON_RECOURSE_STRUCTURE", out.reason_codes)
		self.assertIn("CREDIT_RISK_ESCALATION", out.required_controls)
