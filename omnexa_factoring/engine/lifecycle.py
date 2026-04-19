# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FactoringCase:
	principal: Decimal
	term_months: int
	invoice_face_value: Decimal
	debtor_concentration: Decimal = Decimal("0")
	recourse_type: str = "RECOURSE"
	debtor_rating: str = "B"
	credit_risk_pd: Decimal = Decimal("0.03")
	invoice_count: int = 1


@dataclass(frozen=True)
class LifecycleResult:
	risk_score: Decimal
	pricing_spread: Decimal
	recommended_stage: str  # ORIGINATION | APPROVAL | SERVICING | WATCHLIST
	ifrs9_stage: str
	advance_rate: Decimal
	funding_amount: Decimal
	reserve_amount: Decimal
	reason_codes: list[str]
	required_controls: list[str]

	def to_dict(self) -> dict:
		return {
			"risk_score": str(self.risk_score),
			"pricing_spread": str(self.pricing_spread),
			"recommended_stage": self.recommended_stage,
			"ifrs9_stage": self.ifrs9_stage,
			"advance_rate": str(self.advance_rate),
			"funding_amount": str(self.funding_amount),
			"reserve_amount": str(self.reserve_amount),
			"reason_codes": self.reason_codes,
			"required_controls": self.required_controls,
		}


def evaluate_lifecycle_case(c: FactoringCase) -> LifecycleResult:
	risk = Decimal("0.05")
	reasons: list[str] = []
	controls = ["INVOICE_AUTHENTICITY_CHECK", "DEBTOR_KYC", "ASSIGNMENT_NOTICE"]
	advance_rate = c.principal / c.invoice_face_value if c.invoice_face_value > 0 else Decimal("9")
	if advance_rate > Decimal("0.85"):
		risk += Decimal("0.10")
		reasons.append("HIGH_ADVANCE_RATE")
		controls.append("SENIOR_APPROVAL")
	if c.debtor_concentration > Decimal("0.35"):
		risk += Decimal("0.07")
		reasons.append("DEBTOR_CONCENTRATION_HIGH")
		controls.append("CONCENTRATION_LIMIT_EXCEPTION")
	if c.recourse_type == "NON_RECOURSE":
		risk += Decimal("0.04")
		reasons.append("NON_RECOURSE_STRUCTURE")
		controls.append("CREDIT_INSURANCE_REVIEW")
	if c.debtor_rating in ("C", "D"):
		risk += Decimal("0.06")
		reasons.append("LOW_DEBTOR_RATING")
	if c.credit_risk_pd > Decimal("0.06"):
		risk += Decimal("0.05")
		reasons.append("HIGH_PD_SIGNAL")
		controls.append("CREDIT_RISK_ESCALATION")
	if c.invoice_count > 50:
		controls.append("BULK_INVOICE_QC")
	return _result(c, risk, reasons, controls)


def _result(c: FactoringCase, risk: Decimal, reasons: list[str], controls: list[str]) -> LifecycleResult:
	spread = Decimal("0.02") + risk
	stage = "ORIGINATION"
	ifrs9_stage = "STAGE_1"
	if risk >= Decimal("0.18"):
		stage = "WATCHLIST"
		ifrs9_stage = "STAGE_3"
	elif risk >= Decimal("0.10"):
		stage = "SERVICING"
		ifrs9_stage = "STAGE_2"
	elif c.term_months > 84:
		stage = "APPROVAL"
	advance_rate = _clamp_advance_rate(base=Decimal("0.85") - (risk / Decimal("2")))
	funding_amount = c.invoice_face_value * advance_rate
	reserve_amount = c.invoice_face_value - funding_amount
	if not reasons:
		reasons.append("BASE_POLICY")
	return LifecycleResult(
		risk_score=risk,
		pricing_spread=spread,
		recommended_stage=stage,
		ifrs9_stage=ifrs9_stage,
		advance_rate=advance_rate,
		funding_amount=funding_amount,
		reserve_amount=reserve_amount,
		reason_codes=reasons,
		required_controls=sorted(set(controls)),
	)


def _clamp_advance_rate(base: Decimal) -> Decimal:
	if base < Decimal("0.50"):
		return Decimal("0.50")
	if base > Decimal("0.90"):
		return Decimal("0.90")
	return base
