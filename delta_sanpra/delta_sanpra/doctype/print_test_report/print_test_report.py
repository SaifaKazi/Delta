# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class PrintTestReport(Document):
    @frappe.whitelist()
    def get_data(self):
        if not self.sample_inward:
            frappe.throw("Please select Sample Inward")
        self.set("items", [])
        test_doctypes = [
            "Chemical Test",
            "Physical Test",
            "Corrosion Test",
            "Metallography Test",
            "Other Test"
        ]
        for dt in test_doctypes:
            records = frappe.get_all(
                dt,
                filters={"inward_number": self.sample_inward},
                fields=[
                    "name",
                    "test_group",
                    "test_method",
                    "test_description",
                    "heat_number",
                    "material_specification",
                    "customer_name",
                    "document_id",
                    "challan_no",
                    "status",
                    "witness_name"
                ]
            )
            for d in records:
                self.append("items", {
                    "test_group": d.test_group,
                    "test_method": d.test_method,
                    "test_group_id": d.name,   
                    "status": d.status,
                    "customer_name": d.customer_name,
                    "challan_no": d.challan_no,
                    "test_description": d.test_description,
                    "heat_number": d.heat_number,
                    "material_specification": d.material_specification,
                    "sample_id__test_id": d.document_id,
                    "witness": d.witness_name
                })
        return
