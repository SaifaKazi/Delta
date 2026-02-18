# Copyright (c) 2025, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe.model.naming import make_autoname

class SampleInward(Document):
    @frappe.whitelist()
    def validate_material_rows(self):
        qty = int(self.quantity or 0) 
        self.set("material_details", [])
        for i in range(qty):
            self.append("material_details", {})
        return qty
#**************************************************************************************************
    @frappe.whitelist()
    def update_material_rows(self):
        qty = int(self.quantity or 0)
        existing_rows = len(self.material_details)
        if qty > existing_rows:
            for i in range(existing_rows, qty):
                self.append("material_details", {})
        elif qty < existing_rows:
            for i in range(existing_rows - qty):
                self.material_details.pop()
        return qty
#**************************************************************************************************
    def before_save(self):
        self.get_material_details()
        self.set_sample_ids()
        self.set_test_ids()
        self.get_sample_id_and_test_id()
        self.set_sticker_print_from_test_on_sample()
    def before_naming(self):
        self.mrn_no = make_autoname("DMLS/26-27/I/.####")
    def get_material_details(self):
        company = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"
        last = int((frappe.db.get_value("Company", company, "custom_sample_counter") or "S0").replace("S", ""))
        updated = False
        spec_map = {t.material_specification: t.sample_id for t in self.test_on_sample if t.sample_id}
        for mat in self.material_details:
            sid = spec_map.get(mat.material_specification)            
            if not sid:
                last += 1
                sid = f"S{last}"
                spec_map[mat.material_specification] = sid
                updated = True
            mat.counter = sid
            for test in self.test_on_sample:
                if test.material_specification == mat.material_specification and not test.sample_id:
                    test.sample_id = sid
                    test.heat_number = mat.heat_number
                    test.material_shape = mat.material_shape
                    test.sample_description = mat.sample_description
        if updated:
            frappe.db.set_value("Company", company, "custom_sample_counter", f"S{last}")
#**************************************************************************************************
    def set_sample_ids(self):
        company_name = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"

        sample_ids = [row.sample_id for row in self.test_on_sample if row.sample_id]

        if sample_ids:
            max_num = max(int(s.replace("S", "")) for s in sample_ids if s.startswith("S"))
            frappe.db.set_value("Company", company_name, "custom_sample_counter", f"S{max_num}")
#**************************************************************************************************
    def set_test_ids(self):
        company_name = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"
        last = frappe.db.get_value("Company", company_name, "custom_test_counter") or "0"
        count = int(last) + 1 
        for row in self.test_on_sample:
            if not row.test_id:
                row.test_id = str(count)
                count += 1
        frappe.db.set_value("Company", company_name, "custom_test_counter", str(count -1))   
#**************************************************************************************************
    def get_sample_id_and_test_id(self):
        for row in self.test_on_sample:
            if row.sample_id and row.test_id:
                row.sample_idtest_id = f"{row.sample_id}/{row.test_id}"
                row.sample_id_heat_no = f"{row.sample_id}/{row.test_id} ({row.heat_number})"
            else:
                row.sample_idtest_id = row.test_id or row.sample_id or ""
                row.sample_id_heat_no = ""
#**************************************************************************************************
    def set_sticker_print_from_test_on_sample(self):
        self.sticker_print = []
        for test_row in self.test_on_sample:
            self.append("sticker_print", {
                "material_specification": test_row.material_specification,
                "test_method": test_row.test_method,
                "test_description": test_row.test_description,
                "customer_specification":test_row.customer_specification,
                "sample_description":test_row.sample_description,
            })
#**********************************************************************************************
    def on_submit(self):
        # self.create_lab_analyst()
        self.create_chemical_tests()
        self.create_physical_tests()
        self.create_metallography_tests()
        self.create_corrosion_tests()
        self.create_asme_section_ix_tests()
#**************************************************************************************************
    # def create_lab_analyst(self):
    #     for row in self.test_on_sample:
    #         new_doc = frappe.new_doc("Lab Analyst")
    #         new_doc.inward_number = self.name
    #         new_doc.test_group = row.test_group
    #         new_doc.material_shape = row.material_shape 
    #         new_doc.heat_number = row.heat_number
    #         new_doc.test_method = row.test_method
    #         new_doc.test_description = row.test_description
    #         new_doc.sample_description = row.sample_description
    #         new_doc.child_table_id = row.name
    #         new_doc.document_id = row.test_id 
    #         new_doc.material_specification = row.material_specification
    #         new_doc.customer_specification = row.customer_specification
    #         new_doc.discipline = row.discipline
    #         new_doc.challan_no = self.challan_no
    #         new_doc.customer_name = self.customer
    #         new_doc.material_description = row.material_specification

    #         if self.client :
    #             new_doc.witness = "Yes"
    #             new_doc.witness_name = self.client                
    #         else: 
    #             new_doc.witness = "No" 

    #         if row.sample_id and row.test_id:
    #             new_doc.document_id = f"{row.sample_id}/{row.test_id}"
    #         else:
    #             new_doc.document_id = row.test_id or row.sample_id or ""
            
    #         test_method_doc = frappe.get_doc("Test Method", row.test_method)
    #         item_doc = frappe.get_doc("Item", row.material_specification)

    #         for chem in test_method_doc.chemical_details:
    #             td = new_doc.append("test_details", {
    #                 "test_method": row.test_method,
    #                 "parameter": chem.parameter,
    #                 "method_min_range": chem.min_range,
    #                 "method_max_range": chem.max_range
    #             })
    #             for item_chem in item_doc.custom_chemical_detail:
    #                 if item_chem.parameter == chem.parameter:
    #                     td.min_range = item_chem.min_range
    #                     td.max_range = item_chem.max_range
    #         new_doc.save()
    def create_metallography_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Metallography":
                meta_doc = frappe.new_doc("Metallography Test")
                meta_doc.inward_number = self.name
                meta_doc.child_table_id = row.name
                meta_doc.test_group = row.test_group
                meta_doc.material_shape = row.material_shape
                meta_doc.heat_number = row.heat_number
                meta_doc.test_method = row.test_method
                meta_doc.test_description = row.test_description
                meta_doc.sample_description = row.sample_description
                meta_doc.material_specification = row.material_specification
                meta_doc.customer_specification = row.customer_specification
                meta_doc.challan_no = self.challan_no
                meta_doc.customer_name = self.customer
                meta_doc.document_id = row.sample_idtest_id
                meta_doc.material_description = row.material_specification
                meta_doc.challan_date = self.challan_date
                meta_doc.mrn = self.mrn_no

                # Witness
                if self.client:
                    meta_doc.witness = "Yes"
                    meta_doc.witness_name = self.client
                else:
                    meta_doc.witness = "No"
                meta_doc.save()
#**************************************************************************************************
    def create_corrosion_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Corrosion":
                corro_doc = frappe.new_doc("Corrosion Test")
                corro_doc.inward_number = self.name
                corro_doc.child_table_id = row.name
                corro_doc.test_group = row.test_group
                corro_doc.material_shape = row.material_shape
                corro_doc.heat_number = row.heat_number
                corro_doc.test_method = row.test_method
                corro_doc.test_description = row.test_description
                corro_doc.sample_description = row.sample_description
                corro_doc.material_specification = row.material_specification
                corro_doc.customer_specification = row.customer_specification
                corro_doc.challan_no = self.challan_no
                corro_doc.customer_name = self.customer
                corro_doc.document_id = row.sample_idtest_id
                corro_doc.material_description = row.material_specification
                corro_doc.challan_date = self.challan_date
                corro_doc.mrn = self.mrn_no

                # Witness
                if self.client:
                    corro_doc.witness = "Yes"
                    corro_doc.witness_name = self.client
                else:
                    corro_doc.witness = "No"
                corro_doc.save()
#**************************************************************************************************
    def create_asme_section_ix_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "ASME Section IX":
                asme_doc = frappe.new_doc("ASME Section IX Test")
                asme_doc.inward_number = self.name
                asme_doc.child_table_id = row.name
                asme_doc.test_group = row.test_group
                asme_doc.material_shape = row.material_shape
                asme_doc.heat_number = row.heat_number
                asme_doc.test_method = row.test_method
                asme_doc.test_description = row.test_description
                asme_doc.sample_description = row.sample_description
                asme_doc.material_specification = row.material_specification
                asme_doc.customer_specification = row.customer_specification
                asme_doc.challan_no = self.challan_no
                asme_doc.customer_name = self.customer
                asme_doc.document_id = row.sample_idtest_id
                asme_doc.material_description = row.material_specification
                asme_doc.challan_date = self.challan_date

                # Witness
                if self.client:
                    asme_doc.witness = "Yes"
                    asme_doc.witness_name = self.client
                else:
                    asme_doc.witness = "No"
                asme_doc.save()
#***********************************Chemical Test*********************************************
    def create_chemical_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Chemical":
                chem_doc = frappe.new_doc("Chemical Test")
                chem_doc.inward_number = self.name
                chem_doc.child_table_id = row.name
                chem_doc.test_group = row.test_group
                chem_doc.material_shape = row.material_shape
                chem_doc.heat_number = row.heat_number
                chem_doc.test_method = row.test_method
                chem_doc.test_description = row.test_description
                chem_doc.sample_description = row.sample_description
                chem_doc.material_specification = row.material_specification
                chem_doc.customer_specification = row.customer_specification
                chem_doc.challan_no = self.challan_no
                chem_doc.customer_name = self.customer
                chem_doc.document_id = row.sample_idtest_id
                chem_doc.material_description = row.material_specification
                chem_doc.challan_date = self.challan_date
                chem_doc.mrn = self.mrn_no

                # Witness
                if self.client:
                    chem_doc.witness = "Yes"
                    chem_doc.witness_name = self.client
                else:
                    chem_doc.witness = "No"

                test_method_doc = frappe.get_doc("Test Method", row.test_method)
                item_doc = frappe.get_doc("Item", row.material_specification)

                for chem in test_method_doc.chemical_details:
                    td = chem_doc.append("test_details_chemical", {
                        "test_method": row.test_method,
                        "parameter": chem.parameter,
                        "method_min_range": chem.min_range,
                        "method_max_range": chem.max_range
                    })
                    for item_chem in item_doc.custom_chemical_detail:
                        if item_chem.parameter == chem.parameter:
                            td.min_range = item_chem.min_range
                            td.max_range = item_chem.max_range
                chem_doc.save()
#**********************************************************************************************
    def create_physical_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Physical":
                phys_doc = frappe.new_doc("Physical Test")
                phys_doc.inward_number = self.name
                phys_doc.child_table_id = row.name
                phys_doc.test_group = row.test_group
                phys_doc.material_shape = row.material_shape
                phys_doc.heat_number = row.heat_number
                phys_doc.test_method = row.test_method
                phys_doc.test_description = row.test_description
                phys_doc.sample_description = row.sample_description
                phys_doc.material_specification = row.material_specification
                phys_doc.customer_specification = row.customer_specification
                phys_doc.challan_no = self.challan_no
                phys_doc.customer_name = self.customer
                phys_doc.document_id = row.sample_idtest_id
                phys_doc.material_description = row.material_specification
                phys_doc.challan_date = self.challan_date
                phys_doc.mrn = self.mrn_no

                # Witness
                if self.client:
                    phys_doc.witness = "Yes"
                    phys_doc.witness_name = self.client
                else:
                    phys_doc.witness = "No"
                phys_doc.save()
#**************************************************************************************************           
    @frappe.whitelist()        
    def get_material_sample_details(self):
        self.test_on_sample = []
        for mat_row in self.material_details:
            if mat_row.material_specification:
                item_doc = frappe.get_doc("Item", mat_row.material_specification)
                for sample_row in item_doc.custom_material_sample_details:
                    # frappe.msgprint(str(sample_row.test_method)) 
                    des_price=frappe.get_value("Test Description", sample_row.test_description, "rate")
                    test_method_doc = frappe.get_doc("Test Method", sample_row.test_method)
                    self.append("test_on_sample", {
                        "test_group": test_method_doc.test_group,
                        "test_method": sample_row.test_method,
                        "test_description": sample_row.test_description,   
                        "discipline": test_method_doc.discipline,
                        "group": sample_row.group,
                        "price":des_price,
                        "material_specification": mat_row.material_specification,
                        "material_shape": mat_row.material_shape,
                        "heat_number": mat_row.heat_number,
                        "sample_description":mat_row.sample_description,
                    })
        return self
#*************************************************************************************************
    @frappe.whitelist()
    def update_cutting_rows(self):
        self.cutting_charge = []
        self.machining_charge = []

        def get_charge(material_type_doc, proc_name, dia):
            for r in material_type_doc.sample_preparation_charges:
                if r.processing_charges != proc_name:
                    continue
                if cint(r.is_fix) == 1:
                    return r.charges
                if r.from_range <= dia <= r.to_range:
                    return r.charges
            return 0

        for row in self.material_details:
            if not row.material_dimension:
                continue

            dia = float(row.material_dimension)
            item = frappe.get_doc("Item", row.material_specification)
            material_type = item.custom_material_types
            if not material_type:
                continue

            material_type_doc = frappe.get_doc("Material Type", material_type)

            # CUTTING CHARGE
            if dia >= 50:
                for d in [dia, dia / 2]:
                    charge = get_charge(material_type_doc, "Cutting Charges", d)
                    self.append("cutting_charge", {
                        "material": row.material_specification,
                        "material_type": material_type,
                        "thik_dia": d,
                        "processing_charges": "Cutting Charges",
                        "total": charge
                    })

            # MACHINING CHARGE
            check_dia = dia / 2 if dia >= 50 else dia
            proc = ""
            charge = 0

            for r in material_type_doc.sample_preparation_charges:
                if r.processing_charges == "Cutting Charges":
                    continue
                if cint(r.is_fix) == 1 or (r.from_range <= check_dia <= r.to_range):
                    proc = r.processing_charges
                    charge = r.charges
                    break

            self.append("machining_charge", {
                "material_type": material_type,
                "materials": row.material_specification,
                "thik_dia": check_dia,
                "processing_charges": proc,
                "charge": charge
            })
#*************************************************************************************************
 