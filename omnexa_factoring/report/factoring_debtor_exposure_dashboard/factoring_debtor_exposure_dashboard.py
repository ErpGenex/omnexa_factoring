# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Factoring Debtor Exposure", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Factoring Debtor Exposure",
		fields=['debtor_id', 'portfolio_id', 'outstanding_amount', 'overdue_amount', 'concentration_ratio', 'risk_band'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label":_("Debtor"),"fieldname":"debtor_id","fieldtype":"Data","width":140},
		{"label":_("Portfolio"),"fieldname":"portfolio_id","fieldtype":"Data","width":130},
		{"label":_("Outstanding"),"fieldname":"outstanding_amount","fieldtype":"Currency","width":140},
		{"label":_("Overdue"),"fieldname":"overdue_amount","fieldtype":"Currency","width":130},
		{"label":_("Concentration"),"fieldname":"concentration_ratio","fieldtype":"Percent","width":120},
		{"label":_("Risk"),"fieldname":"risk_band","fieldtype":"Data","width":100},
	], data
