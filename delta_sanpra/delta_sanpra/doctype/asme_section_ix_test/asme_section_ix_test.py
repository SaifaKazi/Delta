# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re
from PyPDF2 import PdfReader

class ASMESectionIXTest(Document):
	def before_save(self):
		self.read_pdf()
		
	@frappe.whitelist()
	def read_pdf(self):
		if not self.pdf_file:
			return
		self.test_details_physical = []

		file_doc = frappe.get_doc("File", {"file_url": self.pdf_file})
		pdf_path = file_doc.get_full_path()

		reader = PdfReader(pdf_path)
		text = ""

		for page in reader.pages:
			page_text = page.extract_text()
			if page_text:
				text += page_text + "\n"

		skip_params = [
			"input data","output data","tested by","stress rate","stress vs. strain","tensile test report","machine model",
			"machine serial no","customer name","order no.","lot no.","customer address","test type","heat no.","date & time"
		]
		skip_value_keywords = [
			"output data",
			"input data",
			"tensile test report"
		]
		added_params = set()
		for line in text.split("\n"):
			if ":" not in line:
				continue
			param, val = line.split(":", 1)
			param = param.strip()
			val = val.strip() 
			lower_val = val.lower()
			for word in skip_value_keywords:
				if word in lower_val:
					val = val[:lower_val.index(word)].strip()
					break
				# blank allowed
			if not param:
				continue
			# skip headings / junk
			normalized_param = param.lower().replace(".", "").strip()
			if normalized_param in [p.replace(".", "").strip() for p in skip_params]:
				continue
			# avoid duplicate parameters
			if param.lower() in added_params:
				continue
			uom = ""
			if val:
				match = re.match(r"^\s*([-+]?\d*\.?\d+)\s*([a-zA-Z/%²³]*)", val)
				if match:
					val = match.group(1)
					uom = match.group(2).strip()
			self.append("test_details_physical", {
				"parameter": param,
				"value": val,
				"uom": uom
			})
			added_params.add(normalized_param)
#**************************************************************************
	@frappe.whitelist()
	def add_data(self):
		readings = [self.row1, self.row2, self.row3, self.row4, self.row5, self.row6]
		valid_readings = [r for r in readings if r not in (None, "", 0)]
		avg = sum(valid_readings) / len(valid_readings) if valid_readings else 0
		for row in self.brinell_hardness_child:
			if (
				row.location == self.location and
				row.test == self.test and
				row.scale == self.scale and
				row.load == self.load and
				row.dial == self.dial and
				row.indentor == self.indentor and
				row.min == self.min and
				row.max == self.max and
				row.r1 == self.row1 and
				row.r2 == self.row2 and
				row.r3 == self.row3 and
				row.r4 == self.row4 and
				row.r5 == self.row5 and
				row.r6 == self.row6 and
				row.avg == avg
			):
				frappe.throw("Same data already exists in table. No changes detected.")
		self.append("brinell_hardness_child", {
			"location": self.location,
			"test": self.test,
			"scale": self.scale,
			"load": self.load,
			"dial": self.dial,
			"indentor": self.indentor,
			"min": self.min,
			"max": self.max,
			"r1": self.row1,
			"r2": self.row2,
			"r3": self.row3,
			"r4": self.row4,
			"r5": self.row5,
			"r6": self.row6,
			"avg": avg
		})
