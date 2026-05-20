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
