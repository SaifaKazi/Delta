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
    # def before_naming(self):
    #     self.mrn_no = make_autoname("DMLS/26-27/I/.####")
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
                "customer_requirement":test_row.customer_requirement,
                "sample_description":test_row.sample_description,
                "sample_id" : test_row.sample_id,
                "heat_number": test_row.heat_number,
                "test_id": test_row.test_id
            })
#**********************************************************************************************
    def on_submit(self):
        self.create_physical_tests()
        self.create_chemical_tests()
        self.create_corrosion_tests()
        self.create_metallography_tests()
        self.create_other_tests()
    def on_update_after_submit(self):
        self.create_physical_tests()
        self.create_chemical_tests()
        self.create_corrosion_tests()
        self.create_metallography_tests()
        self.create_other_tests()
#**************************************************Other Test**************************************
    def create_other_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Other":
                existing = frappe.db.exists("Other Test",{"child_table_id": row.name})
                if existing:
                    other_doc = frappe.get_doc("Other Test", existing)
                    other_doc.heat_number = row.heat_number
                    other_doc.test_method = row.test_method
                    other_doc.sample_description = row.sample_description
                    other_doc.save()
                else:
                    other_doc = frappe.new_doc("Other Test")   
                    other_doc.inward_number = self.name
                    other_doc.child_table_id = row.name
                    other_doc.test_group = row.test_group
                    other_doc.material_shape = row.material_shape
                    other_doc.heat_number = row.heat_number
                    other_doc.test_method = row.test_method
                    other_doc.test_description = row.test_description
                    other_doc.sample_description = row.sample_description
                    other_doc.material_specification = row.material_specification
                    other_doc.customer_requirement = row.customer_requirement
                    other_doc.challan_no = self.challan_no
                    other_doc.customer_name = self.customer
                    other_doc.document_id = row.sample_idtest_id
                    other_doc.material_description = row.material_specification
                    other_doc.challan_date = self.challan_date
                    other_doc.discipline = row.discipline
                    other_doc.group = row.group
                    other_doc.mrn_no = self.name

                    # Witness
                    if self.client:
                        other_doc.witness = "Yes"
                        other_doc.witness_name = self.client
                    else:
                        other_doc.witness = "No"
                    if existing:
                        other_doc.save(ignore_permissions=True, ignore_version=True)
                    else:
                        other_doc.save()   
#*****************************************metallography_tests************************************
    def create_metallography_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Metallography":
                existing = frappe.db.exists("Metallography Test",{"child_table_id": row.name})
                if existing:
                    meta_doc = frappe.get_doc("Metallography Test", existing)
                    meta_doc.heat_number = row.heat_number
                    meta_doc.test_method = row.test_method
                    meta_doc.sample_description = row.sample_description
                    meta_doc.save()
                else:
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
                    meta_doc.customer_requirement = row.customer_requirement
                    meta_doc.challan_no = self.challan_no
                    meta_doc.customer_name = self.customer
                    meta_doc.document_id = row.sample_idtest_id
                    meta_doc.material_description = row.material_specification
                    meta_doc.challan_date = self.challan_date
                    meta_doc.discipline = row.discipline
                    meta_doc.group = row.group
                    meta_doc.mrn_no = self.name

                    # Witness
                    if self.client:
                        meta_doc.witness = "Yes"
                        meta_doc.witness_name = self.client
                    else:
                        meta_doc.witness = "No"
                    if existing:
                        meta_doc.save(ignore_permissions=True, ignore_version=True)
                    else:
                        meta_doc.save()
#*******************************************Corrosion Test **********************************************
    def create_corrosion_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Corrosion":
                existing = frappe.db.exists("Corrosion Test",{"child_table_id": row.name})
                if existing:
                    corro_doc = frappe.get_doc("Corrosion Test", existing)
                    corro_doc.test_method = row.test_method
                    corro_doc.heat_number = row.heat_number
                    corro_doc.customer_requirement = row.customer_requirement
                    corro_doc.save()
                else:
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
                    corro_doc.customer_requirement = row.customer_requirement
                    corro_doc.challan_no = self.challan_no
                    corro_doc.customer_name = self.customer
                    corro_doc.document_id = row.sample_idtest_id
                    corro_doc.material_description = row.material_specification
                    corro_doc.challan_date = self.challan_date
                    corro_doc.discipline = row.discipline
                    corro_doc.group = row.group
                    corro_doc.mrn_no = self.name

                    # Witness
                    if self.client:
                        corro_doc.witness = "Yes"
                        corro_doc.witness_name = self.client
                    else:
                        corro_doc.witness = "No"
                    if existing:
                        corro_doc.save(ignore_permissions=True, ignore_version=True)
                    else:
                        corro_doc.save()

#******************************************Chemical Test*********************************************
    def create_chemical_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Chemical":
                existing = frappe.db.exists("Chemical Test",{"child_table_id": row.name})
                if existing:
                    chem_doc = frappe.get_doc("Chemical Test", existing)

                    chem_doc.heat_number = row.heat_number
                    chem_doc.sample_description = row.sample_description

                    # 🔥 CHECK IF TEST METHOD CHANGED
                    method_changed = chem_doc.test_method != row.test_method
                    chem_doc.test_method = row.test_method

                    if method_changed:
                        # 🔥 CLEAR OLD CHILD TABLE
                        chem_doc.set("test_details_chemical", [])

                        # 🔥 REBUILD CHILD TABLE
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
                    chem_doc.save(ignore_permissions=True, ignore_version=True)
                else:
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
                    chem_doc.customer_requirement = row.customer_requirement
                    chem_doc.challan_no = self.challan_no
                    chem_doc.customer_name = self.customer
                    chem_doc.document_id = row.sample_idtest_id
                    chem_doc.material_description = row.material_specification
                    chem_doc.challan_date = self.challan_date
                    chem_doc.discipline = row.discipline
                    chem_doc.group = row.group
                    chem_doc.mrn_no = self.name

                    # Witness
                    if self.client:
                        chem_doc.witness = "Yes"
                        chem_doc.witness_name = self.client
                    else:
                        chem_doc.witness = "No"

                    test_method_doc = frappe.get_doc("Test Method", row.test_method)
                    item_doc = frappe.get_doc("Item", row.material_specification)

                    # Item parameters dictionary
                    item_params = {d.parameter: d for d in item_doc.custom_chemical_detail}

                    added_params = set()

                    # 1️⃣ Add parameters from Test Method
                    for chem in test_method_doc.chemical_details:

                        td = chem_doc.append("test_details_chemical", {
                            "test_method": row.test_method,
                            "parameter": chem.parameter,
                            "method_min_range": chem.min_range,
                            "method_max_range": chem.max_range
                        })

                        if chem.parameter in item_params:
                            item_chem = item_params[chem.parameter]
                            td.min_range = item_chem.min_range
                            td.max_range = item_chem.max_range

                        added_params.add(chem.parameter)


                    # 2️⃣ Add extra parameters from Item (जो Test Method में नहीं हैं)
                    for item_chem in item_doc.custom_chemical_detail:
                        if item_chem.parameter not in added_params:
                            chem_doc.append("test_details_chemical", {
                                "test_method": row.test_method,
                                "parameter": item_chem.parameter,
                                "min_range": item_chem.min_range,
                                "max_range": item_chem.max_range
                            })

                                
                    if existing:
                        chem_doc.save(ignore_permissions=True, ignore_version=True)
                    else:
                        chem_doc.save()

#**************************************************Physical Test ****************************
    def create_physical_tests(self):
        for row in self.test_on_sample:
            if row.test_group == "Physical":
                existing = frappe.db.exists("Physical Test",{"child_table_id": row.name})
                if existing:
                    phys_doc = frappe.get_doc("Physical Test", existing)
                    phys_doc.sample_description = row.sample_description
                    phys_doc.heat_number = row.heat_number
                    phys_doc.test_method = row.test_method
                    phys_doc.save()
                else:
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
                    phys_doc.customer_requirement = row.customer_requirement
                    phys_doc.challan_no = self.challan_no
                    phys_doc.customer_name = self.customer
                    phys_doc.document_id = row.sample_idtest_id
                    phys_doc.material_description = row.material_specification
                    phys_doc.challan_date = self.challan_date
                    phys_doc.discipline = row.discipline
                    phys_doc.group = row.group
                    phys_doc.mrn_no = self.name

                    # Witness
                    if self.client:
                        phys_doc.witness = "Yes"
                        phys_doc.witness_name = self.client
                    else:
                        phys_doc.witness = "No"
                    if existing:
                        phys_doc.save(ignore_permissions=True, ignore_version=True)
                    else:
                        phys_doc.save()
#**************************************************************************************************           
    @frappe.whitelist()        
    def get_material_sample_details(self):
        # self.test_on_sample = []
        for mat_row in self.material_details:
            if mat_row.material_specification:
                item_doc = frappe.get_doc("Item", mat_row.material_specification)
                for sample_row in item_doc.custom_material_sample_details:
                    #**********************************************************
                    key = (
                        mat_row.material_specification,
                        sample_row.test_method,
                        # sample_row.test_description
                    )

                    existing_row = next((row for row in self.test_on_sample
                        if row.material_specification == key[0]
                        and row.test_method == key[1]),None
                        # and row.test_description == key[2]
                    )
                    if existing_row:
                        existing_row.heat_number = mat_row.heat_number
                        existing_row.sample_description = mat_row.sample_description
                        continue
                    #**************************************************************
                    test_method_doc = frappe.get_doc("Test Method", sample_row.test_method)
                    test_desc = None
                    if self.customer:
                        test_desc = frappe.db.get_value(
                            "Test Description",
                            {
                                "customer_name": self.customer,
                                "test_group": test_method_doc.test_group,
                                "test_method": sample_row.test_method,
                                "customer_specified": 1
                            },
                            ["name", "rate"],
                            as_dict=True
                        )
                    if not test_desc:
                        test_desc = frappe.db.get_value(
                            "Test Description",
                            {
                                "test_group": test_method_doc.test_group,
                                "test_method": sample_row.test_method,
                                "is_standard": 1
                            },
                            ["name", "rate"],
                            as_dict=True
                        )

                    if test_desc:
                        test_description_name = test_desc["name"]
                        des_price = test_desc["rate"]
                    else:
                        test_description_name = ""
                        des_price = 0

                    self.append("test_on_sample", {
                        "test_group": test_method_doc.test_group,
                        "test_method": sample_row.test_method,
                        "discipline": test_method_doc.discipline,
                        "group": sample_row.group,
                        "test_description": test_description_name,
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
        self.cutting_charge_table = []
        self.machining_charge_table = []

        def get_charge(material_type_doc, proc_name, dia):
            fix_charge = 0

            for r in material_type_doc.sample_preparation_charges:
                if r.processing_charges != proc_name:
                    continue
                if cint(r.is_fix) == 0 and r.from_range is not None and r.to_range is not None:
                    if r.from_range <= dia <= r.to_range:
                        return r.charges
                if cint(r.is_fix) == 1:
                    fix_charge = r.charges

            # Agar koi range match nahi mila to fix charge return karo
            return fix_charge


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
                    self.append("cutting_charge_table", {
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

            self.append("machining_charge_table", {
                "material_type": material_type,
                "materials": row.material_specification,
                "thik_dia": check_dia,
                "processing_charges": proc,
                "machining_charge": charge,
                "quantity": 0,
                "total": 0
            })
#************************************************************************************************_
 