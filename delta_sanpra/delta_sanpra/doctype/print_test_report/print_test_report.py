# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form
class PrintTestReport(Document):
    def before_save(self):
        self.check_non_enbl_status_chemical()
        self.check_non_enbl_status_physical()
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
                filters={
                    "inward_number": self.sample_inward
                },
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

                # 🔥 Skip if test_group empty
                if not d.test_group:
                    continue

                self.append("items", {
                    "form_name": dt,
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
    
    @frappe.whitelist()
    def check_non_enbl_status_chemical(self):
        for item in self.items:
            if item.form_name == "Chemical Test":
                chemical_test_doc = frappe.get_doc("Chemical Test", item.test_group_id)
                for row in chemical_test_doc.test_details_chemical:
                    if row.status == "NON NABL":
                        item.status = "NON NABL"
                        frappe.throw(f"In {item.form_name} {item.test_group_id} has NON NABL status")
                
        return
    @frappe.whitelist()
    def check_non_enbl_status_physical(self):
        for item in self.items:
            if item.form_name == "Physical Test":
                physical_test_doc = frappe.get_doc("Physical Test", item.test_group_id)
                for row in physical_test_doc.test_details_physical:
                    if row.parameter == "YS/UTS":
                        item.parameter = "YS/UTS"
                        frappe.throw(f"In {item.form_name} {item.test_group_id} has YS/UTS parameter")
                
        return
