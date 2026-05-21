# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Factoring Settlement Run", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Factoring Settlement Run",
		fields=['name', 'case_id', 'gross_collections', 'fees_amount', 'net_settlement', 'reconciliation_status'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label":_("Run"),"fieldname":"name","fieldtype":"Link","options":"Factoring Settlement Run","width":170},
		{"label":_("Case"),"fieldname":"case_id","fieldtype":"Link","options":"Factoring Case","width":170},
		{"label":_("Gross"),"fieldname":"gross_collections","fieldtype":"Currency","width":130},
		{"label":_("Fees"),"fieldname":"fees_amount","fieldtype":"Currency","width":120},
		{"label":_("Net"),"fieldname":"net_settlement","fieldtype":"Currency","width":130},
		{"label":_("Recon"),"fieldname":"reconciliation_status","fieldtype":"Data","width":120},
	], data
