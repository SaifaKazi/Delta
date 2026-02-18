	# Copyright (c) 2026, Sanpra Software Solution and contributors
	# For license information, please see license.txt

import io
import frappe
from openpyxl import load_workbook
from frappe.utils import nowdate, nowtime
from frappe.model.document import Document
from frappe.utils import cint
import pdfplumber
import re

class ChemicalTest(Document):
	@frappe.whitelist()
	def get_highlight_colors(self):
		tables = ["test_details_chemical"]
		colors = {}
		for table in tables:
			if not hasattr(self, table):
				continue
			for row in getattr(self, table):
				try:
					value = float(row.value) if row.value not in (None, "") else None
					min_range = float(row.min_range) if row.min_range not in (None, "") else None
					max_range = float(row.max_range) if row.max_range not in (None, "") else None

					# Highlight if value < min_range OR value > max_range
					if value is not None and min_range is not None and max_range is not None:
						if value < min_range or value > max_range:
							colors[row.name] = "#FF7A7A"     # RED
						else:
							colors[row.name] = "#7CFF7C"     # GREEN
					else:
						colors[row.name] = ""
				except:
					colors[row.name] = ""
		return colors
	#***************************************************************************
	@frappe.whitelist()
	def get_test_method(self, test_method):
		test_method_doc = frappe.get_doc("Test Method", test_method)
		parameters = [row.parameter for row in test_method_doc.chemical_details]
		# frappe.msgprint(str(parameters))
		return parameters
	#*************************************************************************************
	@frappe.whitelist()
	def get_minmax_range(self, test_method, parameter, material_specification):
		data = {}
		test_method_doc = frappe.get_doc("Test Method", test_method)
		for row in test_method_doc.chemical_details:
			if row.parameter == parameter:
				data["method_min_range"] = row.min_range
				data["method_max_range"] = row.max_range
				break
		material_spec_doc = frappe.get_doc("Item", material_specification)
		for row in material_spec_doc.custom_chemical_detail:
			if row.parameter == parameter:
				data["min_range"] = row.min_range
				data["max_range"] = row.max_range
				break

		return [data] 
#**************************************************************************
	# @frappe.whitelist()
	# def set_ulr_counter(self):
	# 	# frappe.msgprint("Setting ULR Counter")
	# 	last = frappe.db.get_value("Company", company_name, "custom_ulr_counter") or "0"
	# 	count = int(last) + 1 
	# 	frappe.db.set_value("Company", company_name, "custom_ulr_counter", str(count))  
  
	@frappe.whitelist()
	def set_ulr_counter(self):
     	# frappe.msgprint("Setting ULR Counter")
		company_name = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"
		last = frappe.db.get_value("Company", company_name, "custom_ulr_counter") or 0
		count = int(last) + 1
		frappe.db.set_value("Company", company_name, "custom_ulr_counter", count)
		return count
