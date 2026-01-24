# Copyright (c) 2025, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TestDescription(Document):
    def before_save(self):
        if not self.is_default:
            return
        frappe.db.set_value(
            "Test Description",
            {
                "test_description": self.test_description,
                "test_method": self.test_method,
                "is_default": 1,
                "name": ["!=", self.name]
            },"is_default",0,
            update_modified=False
        )
        self.is_default = 1
