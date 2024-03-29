# Copyright (c) 2024, NM and contributors
# For license information, please see license.txt

import subprocess
import frappe
from frappe.model.document import Document
# from nodejs import node
from nodejs import node
import time
import xml.etree.ElementTree as ET
from lxml import etree
from frappe import _
from datetime import datetime, timedelta


# pup_path = "services/index.js"
pup_path = "../apps/sii_addon/services/index.js"
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

@frappe.whitelist()
def scrappe():
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	print("SCRAPINGGGGGGGGGGGGG")
	for cuenta in frappe.get_all('Cuenta SII', fields=['name', 'rut', 'clave_tributaria', 'active']):
		if not cuenta.active:
			continue
		cuenta_doc = frappe.get_doc('Cuenta SII', cuenta.name)
		print("OBTENIENDO CUENTA DOC:", cuenta_doc.name)

		# DON'T SCRAPE IF LATEST FILE DATE IS LESS THAN 1 HOUR
		if not cuenta_doc.latest_file_date or (datetime.now() - cuenta_doc.latest_file_date) > timedelta(hours=0):
			print("SCRAPING NEEDED")
			rut = cuenta.rut
			clave_tributaria = cuenta_doc.get_password('clave_tributaria')

			# start puppeteer process
			print("PROCESO:", [pup_path, rut, clave_tributaria])
			process = node.Popen([pup_path, rut, clave_tributaria], stdout=subprocess.PIPE)
			timeout = 60 
			start_time = time.time()
			while time.time() - start_time < timeout:
				if process.poll() is not None:  # if the process has finished
					break
				time.sleep(0.1) 

			if process.poll() is None:  # If the process has not finished after the timeout
				process.terminate()  # Terminate the process
				continue

			# frappe.msgprint(_("This is a toast message"), title=("Information"), indicator='green')

			result = process.stdout.read().strip()  # path
			print("SII RESULT:", result)

			if result:
				cuenta_doc.latest_file = result
				cuenta_doc.latest_file_date = datetime.now()
			cuenta_doc.save()
			frappe.db.commit()
		
		else:
			print("NO SCRAPING NEEDED")
			result = cuenta_doc.latest_file
		# result = "/opt/bench/frappe-bench/sites/downloads/DTE_DOWN778327462024-03-16.xml"
		
		# cuenta_doc.respuesta = str(result)
		# cuenta_doc.save()
		# frappe.set_value('Cuenta SII', cuenta.name, 'respuesta', result)

		# parse xml result
		if result:
			parse_result(result, cuenta.name)
			# print("PARSING:", result)
			# root = etree.parse(result, parser=etree.XMLParser(encoding="iso-8859-1"))
			# root = root.getroot()

			# for dte in root:
			# 	document = dte[0]
			# 	id = document.items()[0][1]
			# 	if frappe.db.exists('DTE', id):
			# 		continue

			# 	# create dte
			# 	print("CREANDO DTE:", id)
			# 	dte_doc = frappe.new_doc('DTE')
			# 	dte_doc.set("name", id)
			# 	dte_doc.set("id", id)
			# 	dte_doc.name = id
			# 	# dte_doc.name = id

			# 	# set field values
			# 	for field in fields:
			# 		field_value = dte.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
			# 		try:
			# 			# print("FIELD VALUE:", field_value[0].text)
			# 			dte_doc.set(field, field_value[0].text)
			# 		except:
			# 			pass

			# 	# detalle
			# 	lista_detalle = document.findall(".//Detalle")

			# 	# tbl = []
			# 	for detalle in lista_detalle:
			# 		row = {}
			# 		for field in detalle_fields:
			# 			field_value = detalle.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
			# 			try:
			# 				# print("FIELD VALUE:", field_value[0].text)
			# 				row[field] = field_value[0].text
			# 			except:
			# 				pass
			# 			# tbl[field] = field_value[0].text
			# 		# tbl.append(row)
			# 		dte_doc.append("detalle", row)

			# 	print("INSERTANDO DTE DOC:", dte_doc)
			# 	# dte_doc.save()
			# 	dte_doc.insert()
			# 	# frappe.throw("X")
			# 	frappe.db.commit()

@frappe.whitelist()
def parse_all():
	for cuenta in frappe.get_all('Cuenta SII', fields=['name', 'rut', 'clave_tributaria', 'active']):
		if not cuenta.active:
			continue
		cuenta_doc = frappe.get_doc('Cuenta SII', cuenta.name)
		result = cuenta_doc.latest_file

		# parse xml result
		if result:
			parse_result(result, cuenta.name)


def parse_result(result, cuenta_sii):
	print("PARSING:", result)
	root = etree.parse(result, parser=etree.XMLParser(encoding="iso-8859-1"))
	root = root.getroot()

	for dte in root:
		document = dte[0]
		id = document.items()[0][1]
		if frappe.db.exists('DTE', id):
			continue

		# create dte
		print("CREANDO DTE:", id)
		dte_doc = frappe.new_doc('DTE')
		dte_doc.set("name", id)
		dte_doc.set("id", id)
		dte_doc.set("cuenta_sii", cuenta_sii)
		dte_doc.name = id
		# dte_doc.name = id

		# set field values
		for field in fields:
			field_value = dte.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
			try:
				# print("FIELD VALUE:", field_value[0].text)
				dte_doc.set(field, field_value[0].text)
			except:
				pass

		# detalle
		lista_detalle = document.findall(".//Detalle")

		# tbl = []
		for detalle in lista_detalle:
			row = {}
			for field in detalle_fields:
				field_value = detalle.xpath(f".//*[translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field}']")
				try:
					# print("FIELD VALUE:", field_value[0].text)
					row[field] = field_value[0].text
				except:
					pass
				# tbl[field] = field_value[0].text
			# tbl.append(row)
			dte_doc.append("detalle", row)

		print("INSERTANDO DTE DOC:", dte_doc)
		# dte_doc.save()
		dte_doc.insert()
		# frappe.throw("X")
		frappe.db.commit()

class CuentaSII(Document):
	pass
