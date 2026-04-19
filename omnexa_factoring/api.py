# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe

from .standards_profile import get_standards_profile as _get_standards_profile


@frappe.whitelist()
def get_standards_profile() -> dict:
	"""Expose standards profile for governance dashboards and audits."""
	return _get_standards_profile()


from decimal import Decimal
from datetime import date

from .engine import FactoringCase, evaluate_lifecycle_case


@frappe.whitelist()
def evaluate_lifecycle(principal: str, term_months: int, invoice_face_value: str, debtor_concentration: str = "0") -> dict:
	c = FactoringCase(
		principal=Decimal(str(principal)),
		term_months=int(term_months),
		invoice_face_value=Decimal(str(invoice_face_value)),
		debtor_concentration=Decimal(str(debtor_concentration)),
	)
	return evaluate_lifecycle_case(c).to_dict()


@frappe.whitelist()
def get_debtor_pd_from_credit_risk(debtor_id: str, base_score: str = "700") -> dict:
	"""Bridge point to credit risk/decision systems."""
	score = Decimal(str(base_score))
	pd = max(Decimal("0.01"), min(Decimal("0.25"), (Decimal("850") - score) / Decimal("3000")))
	return {"debtor_id": debtor_id, "pd": str(pd), "source": "credit_risk_bridge"}


@frappe.whitelist()
def upsert_factoring_case(
	case_id: str | None = None,
	customer_name: str | None = None,
	portfolio_id: str | None = None,
	principal: str = "0",
	term_months: int = 0,
	invoice_face_value: str = "0",
	debtor_id: str = "DEBTOR-UNKNOWN",
	debtor_concentration: str = "0",
	recourse_type: str = "RECOURSE",
	debtor_rating: str = "B",
	base_credit_score: str = "700",
	invoice_count: int = 1,
) -> dict:
	pd_payload = get_debtor_pd_from_credit_risk(debtor_id=debtor_id, base_score=base_credit_score)
	assessment = evaluate_lifecycle_case(
		FactoringCase(
			principal=Decimal(str(principal)),
			term_months=int(term_months),
			invoice_face_value=Decimal(str(invoice_face_value)),
			debtor_concentration=Decimal(str(debtor_concentration)),
			recourse_type=recourse_type,
			debtor_rating=debtor_rating,
			credit_risk_pd=Decimal(str(pd_payload.get("pd", "0.03"))),
			invoice_count=int(invoice_count),
		)
	).to_dict()
	doc = (
		frappe.get_doc("Factoring Case", case_id)
		if case_id and frappe.db.exists("Factoring Case", case_id)
		else frappe.new_doc("Factoring Case")
	)
	doc.customer_name = customer_name or "Unknown Customer"
	doc.portfolio_id = portfolio_id
	doc.principal = Decimal(str(principal))
	doc.term_months = int(term_months)
	doc.invoice_face_value = Decimal(str(invoice_face_value))
	doc.debtor_id = debtor_id
	doc.debtor_concentration = float(Decimal(str(debtor_concentration)))
	doc.recourse_type = recourse_type
	doc.debtor_rating = debtor_rating
	doc.credit_risk_pd = float(Decimal(str(pd_payload.get("pd", "0.03"))))
	doc.advance_rate = float(Decimal(str(assessment.get("advance_rate", "0"))))
	doc.funding_amount = float(Decimal(str(assessment.get("funding_amount", "0"))))
	doc.reserve_amount = float(Decimal(str(assessment.get("reserve_amount", "0"))))
	doc.lifecycle_stage = assessment.get("recommended_stage")
	doc.ifrs9_stage = assessment.get("ifrs9_stage")
	doc.risk_score = float(Decimal(str(assessment.get("risk_score", "0"))))
	doc.pricing_spread = float(Decimal(str(assessment.get("pricing_spread", "0"))))
	doc.decision_reason_codes = ",".join(assessment.get("reason_codes", []))
	doc.required_controls = ",".join(assessment.get("required_controls", []))
	doc.save(ignore_permissions=True)
	return {"case_id": doc.name, "assessment": assessment}


@frappe.whitelist()
def register_factoring_invoice(case_id: str, invoice_no: str, debtor_id: str, invoice_amount: str, invoice_due_date: str) -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Invoice",
			"case_id": case_id,
			"invoice_no": invoice_no,
			"debtor_id": debtor_id,
			"invoice_amount": Decimal(str(invoice_amount)),
			"invoice_due_date": invoice_due_date,
			"invoice_status": "VERIFIED",
		}
	)
	doc.insert(ignore_permissions=True)
	return {"invoice_id": doc.name}


@frappe.whitelist()
def fund_invoice(invoice_id: str, funded_amount: str) -> dict:
	doc = frappe.get_doc("Factoring Invoice", invoice_id)
	doc.funded_amount = Decimal(str(funded_amount))
	doc.invoice_status = "FUNDED"
	doc.save(ignore_permissions=True)
	return {"invoice_id": doc.name, "invoice_status": doc.invoice_status}


@frappe.whitelist()
def record_collection_event(invoice_id: str, event_type: str, event_amount: str = "0", notes: str = "") -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Collection Event",
			"invoice_id": invoice_id,
			"event_type": event_type,
			"event_status": "CLOSED" if event_type == "PAYMENT" else "OPEN",
			"event_amount": Decimal(str(event_amount)),
			"notes": notes,
		}
	)
	doc.insert(ignore_permissions=True)
	if event_type == "PAYMENT":
		inv = frappe.get_doc("Factoring Invoice", invoice_id)
		inv.collected_amount = (Decimal(str(inv.collected_amount or 0)) + Decimal(str(event_amount)))
		inv.invoice_status = "COLLECTED"
		inv.save(ignore_permissions=True)
	return {"event_id": doc.name}


@frappe.whitelist()
def run_settlement(case_id: str, fees_amount: str = "0") -> dict:
	invoices = frappe.get_all("Factoring Invoice", filters={"case_id": case_id}, fields=["funded_amount", "collected_amount"])
	gross = sum(Decimal(str(i.collected_amount or 0)) for i in invoices)
	fees = Decimal(str(fees_amount))
	net = gross - fees
	doc = frappe.get_doc(
		{
			"doctype": "Factoring Settlement Run",
			"case_id": case_id,
			"settlement_date": str(date.today()),
			"gross_collections": gross,
			"fees_amount": fees,
			"net_settlement": net,
			"reconciliation_status": "MATCHED" if net >= 0 else "EXCEPTION",
		}
	)
	doc.insert(ignore_permissions=True)
	return {"settlement_run_id": doc.name, "net_settlement": str(net)}


@frappe.whitelist()
def refresh_debtor_exposure(debtor_id: str, portfolio_id: str | None = None) -> dict:
	rows = frappe.db.sql(
		"""
		select
			sum(ifnull(i.invoice_amount,0) - ifnull(i.collected_amount,0)) as outstanding,
			sum(case when i.invoice_due_date < curdate() then (ifnull(i.invoice_amount,0) - ifnull(i.collected_amount,0)) else 0 end) as overdue
		from `tabFactoring Invoice` i
		where i.debtor_id = %(debtor_id)s
		""",
		{"debtor_id": debtor_id},
		as_dict=True,
	)
	outstanding = Decimal(str((rows[0].outstanding if rows else 0) or 0))
	overdue = Decimal(str((rows[0].overdue if rows else 0) or 0))
	total = frappe.db.sql("select sum(ifnull(invoice_amount,0)) as t from `tabFactoring Invoice`", as_dict=True)
	total_invoice = Decimal(str((total[0].t if total else 0) or 0))
	ratio = Decimal("0") if total_invoice <= 0 else (outstanding / total_invoice)
	risk_band = "HIGH" if ratio > Decimal("0.35") else ("MEDIUM" if ratio > Decimal("0.2") else "LOW")
	existing = frappe.db.exists("Factoring Debtor Exposure", {"debtor_id": debtor_id})
	doc = frappe.get_doc("Factoring Debtor Exposure", existing) if existing else frappe.new_doc("Factoring Debtor Exposure")
	doc.debtor_id = debtor_id
	doc.portfolio_id = portfolio_id
	doc.outstanding_amount = outstanding
	doc.overdue_amount = overdue
	doc.concentration_ratio = ratio
	doc.risk_band = risk_band
	doc.save(ignore_permissions=True)
	return {"exposure_id": doc.name, "risk_band": risk_band}


@frappe.whitelist()
def get_debtor_exposure_dashboard() -> dict:
	by_debtor = frappe.db.sql(
		"""
		select debtor_id, outstanding_amount, overdue_amount, concentration_ratio, risk_band
		from `tabFactoring Debtor Exposure`
		order by outstanding_amount desc
		limit 20
		""",
		as_dict=True,
	)
	portfolio = frappe.db.sql(
		"""
		select portfolio_id, sum(ifnull(outstanding_amount,0)) as outstanding
		from `tabFactoring Debtor Exposure`
		group by portfolio_id
		order by outstanding desc
		""",
		as_dict=True,
	)
	return {"top_debtors": by_debtor, "portfolio_outstanding": portfolio}


@frappe.whitelist()
def submit_policy_version(policy_name: str, version: str, payload: str, effective_from: str | None = None) -> dict:
	import json
	from .governance import submit_policy_version as _submit
	obj = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(obj, dict):
		frappe.throw(frappe._("payload must be a JSON object"))
	return _submit("omnexa_factoring", policy_name=policy_name, version=version, payload=obj, effective_from=effective_from)


@frappe.whitelist()
def approve_policy_version(policy_name: str, version: str) -> dict:
	from .governance import approve_policy_version as _approve
	return _approve("omnexa_factoring", policy_name=policy_name, version=version)


@frappe.whitelist()
def create_audit_snapshot(process_name: str, inputs: str, outputs: str, policy_ref: str | None = None) -> dict:
	import json
	from .governance import create_audit_snapshot as _snap
	in_obj = json.loads(inputs) if isinstance(inputs, str) else inputs
	out_obj = json.loads(outputs) if isinstance(outputs, str) else outputs
	if not isinstance(in_obj, dict) or not isinstance(out_obj, dict):
		frappe.throw(frappe._("inputs/outputs must be JSON objects"))
	return _snap("omnexa_factoring", process_name=process_name, inputs=in_obj, outputs=out_obj, policy_ref=policy_ref)


@frappe.whitelist()
def get_governance_overview() -> dict:
	from .governance import governance_overview as _overview
	return _overview("omnexa_factoring")


@frappe.whitelist()
def reject_policy_version(policy_name: str, version: str, reason: str = "") -> dict:
	from .governance import reject_policy_version as _reject
	return _reject("omnexa_factoring", policy_name=policy_name, version=version, reason=reason)


@frappe.whitelist()
def list_policy_versions(policy_name: str | None = None) -> list[dict]:
	from .governance import list_policy_versions as _list
	return _list("omnexa_factoring", policy_name=policy_name)


@frappe.whitelist()
def list_audit_snapshots(process_name: str | None = None, limit: int = 100) -> list[dict]:
	from .governance import list_audit_snapshots as _list
	return _list("omnexa_factoring", process_name=process_name, limit=int(limit))


@frappe.whitelist()
def get_regulatory_dashboard() -> dict:
	"""Unified compliance dashboard payload for this app."""
	from .governance import governance_overview
	from .standards_profile import get_standards_profile
	std = get_standards_profile()
	gov = governance_overview("omnexa_factoring")
	return {
		"app": "omnexa_factoring",
		"standards": std.get("standards", []),
		"activity_controls": std.get("activity_controls", []),
		"governance": gov,
		"compliance_score": _compute_compliance_score(std=std, gov=gov),
	}


def _compute_compliance_score(std: dict, gov: dict) -> int:
	"""Simple normalized readiness score (0..100) for executive monitoring."""
	base = min(50, 5 * len(std.get("standards", [])))
	controls = min(30, 3 * len(std.get("activity_controls", [])))
	approved = int(gov.get("policies_approved", 0) or 0)
	pending = int(gov.get("policies_pending", 0) or 0)
	governance = min(20, approved * 2)
	if pending > 0:
		governance = max(0, governance - min(10, pending))
	return int(base + controls + governance)
