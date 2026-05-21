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
	filters_dict = get_all_filters(filters, "Factoring Invoice", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Factoring Invoice",
		fields=['invoice_no', 'case_id', 'debtor_id', 'invoice_amount', 'invoice_status'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label":_("Invoice"),"fieldname":"invoice_no","fieldtype":"Data","width":140},
		{"label":_("Case"),"fieldname":"case_id","fieldtype":"Link","options":"Factoring Case","width":180},
		{"label":_("Debtor"),"fieldname":"debtor_id","fieldtype":"Data","width":130},
		{"label":_("Amount"),"fieldname":"invoice_amount","fieldtype":"Currency","width":130},
		{"label":_("Status"),"fieldname":"invoice_status","fieldtype":"Data","width":120},
	], data
