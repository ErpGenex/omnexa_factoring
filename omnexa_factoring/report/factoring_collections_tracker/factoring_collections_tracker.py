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
	filters_dict = get_all_filters(filters, "Factoring Collection Event", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Factoring Collection Event",
		fields=['name', 'invoice_id', 'event_type', 'event_status', 'event_amount'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label":"Event","fieldname":"name","fieldtype":"Link","options":"Factoring Collection Event","width":160},
		{"label":"Invoice","fieldname":"invoice_id","fieldtype":"Link","options":"Factoring Invoice","width":180},
		{"label":"Type","fieldname":"event_type","fieldtype":"Data","width":120},
		{"label":"Status","fieldname":"event_status","fieldtype":"Data","width":110},
		{"label":"Amount","fieldname":"event_amount","fieldtype":"Currency","width":130},
	], data
