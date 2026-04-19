import frappe


def execute(filters=None):
	columns=[
		{"label":"Event","fieldname":"name","fieldtype":"Link","options":"Factoring Collection Event","width":160},
		{"label":"Invoice","fieldname":"invoice_id","fieldtype":"Link","options":"Factoring Invoice","width":180},
		{"label":"Type","fieldname":"event_type","fieldtype":"Data","width":120},
		{"label":"Status","fieldname":"event_status","fieldtype":"Data","width":110},
		{"label":"Amount","fieldname":"event_amount","fieldtype":"Currency","width":130},
	]
	data=frappe.get_all("Factoring Collection Event",fields=["name","invoice_id","event_type","event_status","event_amount"],order_by="modified desc")
	return columns,data
