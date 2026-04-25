import frappe


def execute(filters=None):
	columns=[
		{"label":"Run","fieldname":"name","fieldtype":"Link","options":"Factoring Settlement Run","width":170},
		{"label":"Case","fieldname":"case_id","fieldtype":"Link","options":"Factoring Case","width":170},
		{"label":"Gross","fieldname":"gross_collections","fieldtype":"Currency","width":130},
		{"label":"Fees","fieldname":"fees_amount","fieldtype":"Currency","width":120},
		{"label":"Net","fieldname":"net_settlement","fieldtype":"Currency","width":130},
		{"label":"Recon","fieldname":"reconciliation_status","fieldtype":"Data","width":120},
	]
	data=frappe.get_all("Factoring Settlement Run",fields=["name","case_id","gross_collections","fees_amount","net_settlement","reconciliation_status"],order_by="modified desc")
	return columns,data
