from __future__ import annotations

import frappe


@frappe.whitelist()
def preview_gl_posting(
	scenario: str | None = None,
	rou_asset: str = "0",
	lease_liability: str = "0",
	principal: str = "0",
	settlement_cash: str = "0",
) -> dict:
	"""SAP parity — GL preview (finance_engine bridge, no JE)."""
	from omnexa_finance_engine.fs_parity_bridge import preview_gl_for_vertical

	return preview_gl_for_vertical(
		"factoring",
		scenario=scenario,
		rou_asset=rou_asset,
		lease_liability=lease_liability,
		principal=principal,
		settlement_cash=settlement_cash,
	)


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("factoring", scenario=scenario, params=params)


@frappe.whitelist()
def evaluate_lifecycle(principal: str, term_months: int = 12, invoice_face_value: str | None = None) -> dict:
	from decimal import Decimal

	from omnexa_factoring.engine.lifecycle import FactoringCase, evaluate_lifecycle_case

	case = FactoringCase(
		principal=Decimal(str(principal)),
		term_months=int(term_months),
		invoice_face_value=Decimal(str(invoice_face_value or principal)),
	)
	return evaluate_lifecycle_case(case).to_dict()


@frappe.whitelist()
def upsert_factoring_case(customer_name: str, principal: str, invoice_face_value: str, term_months: int = 12) -> dict:
	from decimal import Decimal

	from omnexa_factoring.engine.lifecycle import FactoringCase, evaluate_lifecycle_case

	result = evaluate_lifecycle_case(
		FactoringCase(
			principal=Decimal(str(principal)),
			term_months=int(term_months),
			invoice_face_value=Decimal(str(invoice_face_value)),
		)
	)
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Case",
			"customer_name": customer_name,
			"principal": principal,
			"invoice_face_value": invoice_face_value,
			"term_months": term_months,
			"debtor_id": "DEB-DEMO-001",
			"advance_rate": float(result.advance_rate),
			"lifecycle_stage": result.recommended_stage,
			"ifrs9_stage": result.ifrs9_stage,
			"risk_score": float(result.risk_score),
			"pricing_spread": float(result.pricing_spread),
			"funding_amount": float(result.funding_amount),
			"reserve_amount": float(result.reserve_amount),
			"decision_reason_codes": ",".join(result.reason_codes),
			"required_controls": ",".join(result.required_controls),
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name, "lifecycle": result.to_dict()}
