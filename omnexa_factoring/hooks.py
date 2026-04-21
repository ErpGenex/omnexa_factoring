app_name = "omnexa_factoring"
app_title = "ErpGenEx — Factoring"
app_publisher = "Omnexa"
app_description = "Factoring and discounting vertical"
app_email = "dev@omnexa.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "omnexa_factoring",
# 		"logo": "/assets/omnexa_factoring/logo.png",
# 		"title": "Omnexa Factoring",
# 		"route": "/omnexa_factoring",
# 		"has_permission": "omnexa_factoring.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_factoring/css/omnexa_factoring.css"
# app_include_js = "/assets/omnexa_factoring/js/omnexa_factoring.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_factoring/css/omnexa_factoring.css"
# web_include_js = "/assets/omnexa_factoring/js/omnexa_factoring.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_factoring/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_factoring/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_factoring.utils.jinja_methods",
# 	"filters": "omnexa_factoring.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "omnexa_factoring.install.enforce_supported_frappe_version"
before_migrate = "omnexa_factoring.install.enforce_supported_frappe_version"

# Uninstallation
# ------------

# before_uninstall = "omnexa_factoring.uninstall.before_uninstall"
# after_uninstall = "omnexa_factoring.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_factoring.utils.before_app_install"
# after_app_install = "omnexa_factoring.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_factoring.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_factoring.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_factoring.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"omnexa_factoring.tasks.all"
# 	],
# 	"daily": [
# 		"omnexa_factoring.tasks.daily"
# 	],
# 	"hourly": [
# 		"omnexa_factoring.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omnexa_factoring.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omnexa_factoring.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "omnexa_factoring.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_factoring.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_factoring.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["omnexa_factoring.license_gate.before_request"]
# after_request = ["omnexa_factoring.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_factoring.utils.before_job"]
# after_job = ["omnexa_factoring.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_factoring.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


after_migrate = [
	"omnexa_factoring.governance_setup.after_migrate",
	"omnexa_factoring.workspace_enhancer.after_migrate",
]

permission_query_conditions = {
	"Factoring Policy Version": "omnexa_factoring.governance_permissions.policy_query_conditions",
	"Factoring Audit Snapshot": "omnexa_factoring.governance_permissions.snapshot_query_conditions",
}

has_permission = {
	"Factoring Policy Version": "omnexa_factoring.governance_permissions.policy_has_permission",
	"Factoring Audit Snapshot": "omnexa_factoring.governance_permissions.snapshot_has_permission",
}
