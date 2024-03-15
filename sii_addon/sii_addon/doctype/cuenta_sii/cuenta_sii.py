# Copyright (c) 2024, NM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from nodejs import node
from nodejs import node
import time
import xml.etree.ElementTree as ET
from lxml import etree


pup_path = "../../../services/index.js"
fields = [
  "rutrecep",
  "cdgintrecep",
  "rznsocrecep",
  "girorecep",
  "dirrecep",
  "cmnarecep",
  "ciudadrecep",
  "dirpostal",
  "cmnapostal",
  "ciudadpostal",
  "rutemisor",
  "rznsoc",
  "giroemis",
  "acteco",
  "dirorigen",
  "cmnaorigen",
  "ciudadorigen",
  "cdgvendedor",
  "tipodte",
  "folio",
  "fchemis",
  "tipodespacho",
  "fmapago",
  "fchvenc",
  "mntneto",
  "tasaiva",
  "iva",
  "mnttotal",
  "tsted",
  "tmstfirma",
  "signature_section",
  "digestvalue",
  "signaturevalue",
  "rsakeyvalue",
  "x509certificate",
 ]

detalle_fields = [
  "nrolindet",
  "tpocodigo",
  "vlrcodigo",
  "nmbitem",
  "qtyitem",
  "unmditem",
  "prcitem",
  "montoitem"
 ]

# @frappe.whitelist()
def scrappe():
	for cuenta in frappe.get_all('Cuenta SII', fields=['name', 'rut', 'clave_tributaria']):
		rut = cuenta.rut
		clave_tributaria = cuenta.clave_tributaria

		# start puppeteer process
		process = node.Popen([pup_path, rut, clave_tributaria])
		timeout = 60 
		start_time = time.time()
		while time.time() - start_time < timeout:
			if process.poll() is not None:  # if the process has finished
				break
			time.sleep(0.1) 

		if process.poll() is None:  # If the process has not finished after the timeout
			process.terminate()  # Terminate the process
			continue

		result = process.stdout.flush()
		frappe.set_value('Cuenta SII', cuenta.name, 'response', result)

		# parse xml result
		if result:
			# parse xml
			# set values
			root = etree.fromstring(result.encode('utf-8'))
			
			for dte in root:
				document = dte[0]
				id = document[0][1]
				if frappe.db.exists('DTE', id):
					continue

				# create dte
				dte_doc = frappe.new_doc('DTE')
				dte_doc.name = id

				# set field values
				for field in fields:
					field_value = dte.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
					dte_doc.set(field, field_value[0].text)

				# detalle
				lista_detalle = document.findall(".//Detalle")

				for detalle in lista_detalle:
					tbl = {}
					for field in detalle_fields:
						field_value = detalle.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
						tbl[field] = field_value[0].text

					dte_doc.append("detalle", tbl)
				
				dte_doc.insert()
				dte_doc.save()

	frappe.db.commit()
	

class CuentaSII(Document):
	pass
