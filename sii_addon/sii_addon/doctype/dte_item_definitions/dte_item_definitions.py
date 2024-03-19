# Copyright (c) 2024, NM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DTEItemDefinitions(Document):
    pass
	# def before_save(self):
	# 	if not self.is_new:
	# 		# todo: parse only the file from the corresponding account (using cuenta_sii field)
	# 		# ex: frappe.call("sii_addon.sii_addon.doctype.cuenta_sii.cuenta_sii.parse_single", self.cuenta_sii)
	# 		frappe.call("sii_addon.sii_addon.doctype.cuenta_sii.cuenta_sii.parse_all")
	# 		# "apps/sii_addon/sii_addon/sii_addon/doctype/cuenta_sii/cuenta_sii.py"
