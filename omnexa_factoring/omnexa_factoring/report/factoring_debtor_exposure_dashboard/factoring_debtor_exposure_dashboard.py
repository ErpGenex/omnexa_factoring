import frappe


def execute(filters=None):
	columns=[
		{"label":"Debtor","fieldname":"debtor_id","fieldtype":"Data","width":140},
		{"label":"Portfolio","fieldname":"portfolio_id","fieldtype":"Data","width":130},
		{"label":"Outstanding","fieldname":"outstanding_amount","fieldtype":"Currency","width":140},
		{"label":"Overdue","fieldname":"overdue_amount","fieldtype":"Currency","width":130},
		{"label":"Concentration","fieldname":"concentration_ratio","fieldtype":"Percent","width":120},
		{"label":"Risk","fieldname":"risk_band","fieldtype":"Data","width":100},
	]
	data=frappe.get_all("Factoring Debtor Exposure",fields=["debtor_id","portfolio_id","outstanding_amount","overdue_amount","concentration_ratio","risk_band"],order_by="outstanding_amount desc")
	return columns,data
