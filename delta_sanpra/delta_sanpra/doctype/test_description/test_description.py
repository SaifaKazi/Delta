# Copyright (c) 2025, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form
class TestDescription(Document):
    def before_save(self):
        if self.is_default == 1 and self.is_standard == 1:
            frappe.throw("A record cannot be both 'Default' and 'Standard' at the same time.")
        if self.is_default == 0 and self.is_standard == 0:
            frappe.throw("A record must be either 'Default' or 'Standard'.")
            
        if self.is_default == 1 and self.is_standard == 0:
            existing = frappe.db.get_value("Test Description",
                {
                    "test_description": self.test_description,
                    "test_method": self.test_method,
                    "test_group": self.test_group,
                    "customer_name": self.customer_name,
                    "is_default": 1,    
                    "name": ["!=", self.name],          
                },
            )
            # Agar aisa record mil gaya to error throw
            if existing:
                    frappe.throw(
                        f"'Is Default' is already enabled in {get_link_to_form('Test Description', existing)}."
                    )

#***************************************************************************************************
        if self.is_standard == 1 and self.is_default == 0:
            existing = frappe.db.get_value(
                "Test Description",
                {
                    "test_description": self.test_description,
                    "test_method": self.test_method,
                    "test_group": self.test_group,
                    "customer_name": self.customer_name,
                    "is_standard": 1,
                    # already checkmark hai to ignore karne ke liye.
                    "name": ["!=", self.name],             
                },
            )
            if existing:
                frappe.throw(
                    f"'Is Standard' is already enabled in {get_link_to_form('Test Description', existing)}."
                )