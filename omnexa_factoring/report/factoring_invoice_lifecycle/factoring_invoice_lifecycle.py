import frappe


def execute(filters=None):
	columns=[
		{"label":"Invoice","fieldname":"invoice_no","fieldtype":"Data","width":140},
		{"label":"Case","fieldname":"case_id","fieldtype":"Link","options":"Factoring Case","width":180},
		{"label":"Debtor","fieldname":"debtor_id","fieldtype":"Data","width":130},
		{"label":"Amount","fieldname":"invoice_amount","fieldtype":"Currency","width":130},
		{"label":"Status","fieldname":"invoice_status","fieldtype":"Data","width":120},
	]
	data=frappe.get_all("Factoring Invoice",fields=["invoice_no","case_id","debtor_id","invoice_amount","invoice_status"],order_by="modified desc")
	return columns,data
