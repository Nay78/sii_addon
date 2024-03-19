# Copyright (c) 2024, NM and contributors
# For license information, please see license.txt

from datetime import datetime
import re
import frappe
from frappe.model.document import Document


class DTE(Document):
	def before_save(self):
		if not frappe.db.exists("Supplier", self.rutemisor):
			# CREATE SUPPLIER
			supplier_doc = frappe.new_doc("Supplier")
			# supplier_doc.name = self.rutemisor
			supplier_doc.supplier_name = self.rutemisor
			supplier_doc.website = self.rznsoc

			supplier_info = [self.rutemisor, self.rznsoc, self.acteco, self.giroemis, self.dirorigen, self.cmnaorigen, self.ciudadorigen, self.cdgvendedor]
			supplier_info = [i if i else "" for i in supplier_info]
			supplier_doc.supplier_details = "\n".join(supplier_info)

			supplier_doc.insert()
			supplier_doc.supplier_name = self.rznsoc
			supplier_doc.save()

			frappe.db.commit()

		# CREATE DTE ITEM DEFINITION
		if not frappe.db.exists("DTE Item Definitions", self.rutemisor):
			dte_item_doc = frappe.new_doc("DTE Item Definitions")
			print("NEW DTE ITEM DEFINITION: ", self.rutemisor)
			dte_item_doc.name = self.rutemisor
			dte_item_doc.supplier = self.rutemisor
			dte_item_doc.rznsoc = self.rznsoc
			dte_item_doc.cuenta_sii = self.cuenta_sii
			dte_item_doc.insert()
		else:  # doc exists
			dte_item_doc = frappe.get_doc("DTE Item Definitions", self.rutemisor)

		# CREATE DTE ITEMS ON DTE ITEM DEFINITION
		dte_def_detalle = [i.name for i in dte_item_doc.detalle]
		# print("dte_def_dealle", dte_def_detalle)
		for item in self.detalle:
			nombreitem = str(item.nmbitem).strip()
			if nombreitem not in dte_def_detalle:
				dte_item_doc.append("detalle", {
					"nmbitem": nombreitem,
				})

		dte_item_doc.save()

	def before_submit(self):
		# check if item definition exists
		if not frappe.db.exists("DTE Item Definitions", self.rutemisor):
			frappe.throw("DTE Item Definition for this supplier does not exist")
		
		# get items from item definition
		def_doc = frappe.get_doc("DTE Item Definitions", self.rutemisor)
		
		if all([i.ignore for i in def_doc.detalle]):
			frappe.throw("All items are ignored")

		def determine_product(detalle_nmb):
			for definition in def_doc.detalle:
				if not definition.ignore and not definition.item:
					frappe.throw(f"Item {detalle_nmb} does not have a DTE Item Definition")
					
				if definition.isregex:
					if re.compile(definition.nmbitem).match(detalle_nmb):
						if definition.ignore:
							return 0
						return definition
				else:
					if detalle_nmb == definition.nmbitem:
						if definition.ignore:
							return 0
						return definition

		
		# añadir orden de compra PAGADA
		orden_compra = frappe.new_doc("Purchase Order")
		orden_compra.supplier = self.rutemisor
		orden_compra.transaction_date = self.tmstfirma
		# orden_compra.set_warehouse = self.tmstfirma
		orden_compra.schedule_date = datetime.now()

		# check if all items from DTE coincide with the item definitions
		count = 0
		for detalle in self.detalle:
			product_definition = determine_product(detalle.nmbitem)

			if product_definition != 0:
				orden_compra.append("items", {
					"item_code": product_definition.item,
					"item_name": detalle.nmbitem,
					"qty": detalle.qtyitem * product_definition.qty_multiplier,
					"rate": detalle.prcitem / product_definition.qty_multiplier,
					"warehouse": product_definition.default_warehouse,
				})
				count += 1
		
		if count:
			orden_compra.insert()

