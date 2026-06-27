from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import flt, today

from omnexa_factoring.engine.lifecycle import FactoringCase, evaluate_lifecycle_case


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


def _build_case(principal: str, term_months: int, invoice_face_value: str | None, **kwargs) -> FactoringCase:
	return FactoringCase(
		principal=Decimal(str(principal)),
		term_months=int(term_months),
		invoice_face_value=Decimal(str(invoice_face_value or principal)),
		debtor_concentration=Decimal(str(kwargs.get("debtor_concentration") or 0)),
		recourse_type=str(kwargs.get("recourse_type") or "RECOURSE"),
		debtor_rating=str(kwargs.get("debtor_rating") or "B"),
		credit_risk_pd=Decimal(str(kwargs.get("credit_risk_pd") or kwargs.get("base_credit_score") or "0.03")),
	)


@frappe.whitelist()
def evaluate_lifecycle(
	principal: str,
	term_months: int = 12,
	invoice_face_value: str | None = None,
	debtor_concentration: str | None = None,
	**kwargs,
) -> dict:
	kwargs.setdefault("debtor_concentration", debtor_concentration)
	return evaluate_lifecycle_case(_build_case(principal, term_months, invoice_face_value, **kwargs)).to_dict()


@frappe.whitelist()
def upsert_factoring_case(
	customer_name: str,
	principal: str,
	invoice_face_value: str,
	term_months: int = 12,
	**kwargs,
) -> dict:
	result = evaluate_lifecycle_case(_build_case(principal, term_months, invoice_face_value, **kwargs))
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Case",
			"customer_name": customer_name,
			"portfolio_id": kwargs.get("portfolio_id"),
			"principal": principal,
			"invoice_face_value": invoice_face_value,
			"term_months": term_months,
			"debtor_id": kwargs.get("debtor_id") or "DEB-DEMO-001",
			"recourse_type": kwargs.get("recourse_type") or "RECOURSE",
			"debtor_rating": kwargs.get("debtor_rating") or "B",
			"debtor_concentration": flt(kwargs.get("debtor_concentration") or 0),
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
	return {"case_id": doc.name, "name": doc.name, "lifecycle": result.to_dict()}


@frappe.whitelist()
def register_factoring_invoice(
	case_id: str,
	invoice_no: str,
	debtor_id: str,
	invoice_amount: str,
	due_date: str,
) -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Invoice",
			"case_id": case_id,
			"invoice_no": invoice_no,
			"debtor_id": debtor_id,
			"invoice_amount": invoice_amount,
			"invoice_due_date": due_date,
			"invoice_status": "REGISTERED",
		}
	).insert(ignore_permissions=True)
	return {"invoice_id": doc.name, "invoice_no": invoice_no}


@frappe.whitelist()
def fund_invoice(invoice_id: str, funded_amount: str) -> dict:
	doc = frappe.get_doc("Factoring Invoice", invoice_id)
	doc.invoice_status = "FUNDED"
	doc.funded_amount = flt(funded_amount)
	doc.save(ignore_permissions=True)
	return {"invoice_id": doc.name, "invoice_status": doc.invoice_status}


@frappe.whitelist()
def record_collection_event(
	invoice_id: str,
	event_type: str,
	event_amount: str,
	notes: str = "",
) -> dict:
	evt = frappe.get_doc(
		{
			"doctype": "Factoring Collection Event",
			"invoice_id": invoice_id,
			"event_type": event_type,
			"event_amount": flt(event_amount),
			"notes": notes,
			"event_status": "CLOSED",
		}
	).insert(ignore_permissions=True)
	inv = frappe.get_doc("Factoring Invoice", invoice_id)
	inv.collected_amount = flt(inv.collected_amount) + flt(event_amount)
	if inv.collected_amount >= flt(inv.invoice_amount):
		inv.invoice_status = "COLLECTED"
	inv.save(ignore_permissions=True)
	return {"event_id": evt.name}


@frappe.whitelist()
def run_settlement(case_id: str, fees_amount: str) -> dict:
	fees = flt(fees_amount)
	invoices = frappe.get_all(
		"Factoring Invoice",
		filters={"case_id": case_id},
		fields=["collected_amount"],
	)
	gross = sum(flt(r.get("collected_amount")) for r in invoices)
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Settlement Run",
			"case_id": case_id,
			"settlement_date": today(),
			"gross_collections": gross,
			"fees_amount": fees,
			"net_settlement": gross - fees,
			"reconciliation_status": "MATCHED",
		}
	).insert(ignore_permissions=True)
	return {"settlement_run_id": doc.name}


@frappe.whitelist()
def refresh_debtor_exposure(debtor_id: str, portfolio_id: str) -> dict:
	outstanding = flt(
		frappe.db.sql(
			"""
			SELECT COALESCE(SUM(invoice_amount - COALESCE(collected_amount, 0)), 0)
			FROM `tabFactoring Invoice`
			WHERE debtor_id = %s AND invoice_status NOT IN ('WRITTEN_OFF')
			""",
			debtor_id,
		)[0][0]
	)
	ratio = min(1.0, outstanding / 500000.0) if outstanding else 0.0
	risk_band = "LOW" if ratio < 0.25 else ("MEDIUM" if ratio < 0.5 else "HIGH")
	name = frappe.db.get_value(
		"Factoring Debtor Exposure",
		{"debtor_id": debtor_id, "portfolio_id": portfolio_id},
		"name",
	)
	payload = {
		"debtor_id": debtor_id,
		"portfolio_id": portfolio_id,
		"outstanding_amount": outstanding,
		"concentration_ratio": ratio,
		"risk_band": risk_band,
	}
	if name:
		doc = frappe.get_doc("Factoring Debtor Exposure", name)
		doc.update(payload)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({"doctype": "Factoring Debtor Exposure", **payload}).insert(
			ignore_permissions=True
		)
	return {
		"debtor_id": debtor_id,
		"portfolio_id": portfolio_id,
		"outstanding_amount": outstanding,
		"risk_band": risk_band,
		"exposure_id": doc.name,
	}


@frappe.whitelist()
def get_debtor_exposure_dashboard() -> dict:
	rows = frappe.get_all(
		"Factoring Debtor Exposure",
		fields=["debtor_id", "portfolio_id", "outstanding_amount", "risk_band"],
		order_by="outstanding_amount desc",
		limit=20,
	)
	return {"top_debtors": rows, "count": len(rows)}


@frappe.whitelist()
def get_regulatory_dashboard() -> dict:
	from .governance import governance_overview
	from .standards_profile import get_standards_profile

	std = get_standards_profile()
	gov = governance_overview("omnexa_factoring")
	return {
		"app": "omnexa_factoring",
		"standards": std.get("standards", []),
		"activity_controls": std.get("activity_controls", []),
		"governance": gov,
		"compliance_score": min(100, 5 * len(std.get("standards", [])) + 3 * len(std.get("activity_controls", []))),
	}
