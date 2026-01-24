// Copyright (c) 2025, Sanpra Software Solution and contributors
// For license information, please see license.txt

// let items = []
let item1 = []
let description = []
function validate_challan_date(frm) {
    if (frm.doc.challan_date && frm.doc.date &&
        frm.doc.challan_date > frm.doc.date) {

        frappe.msgprint("Challan Date cannot be greater than date");
    }
}
frappe.ui.form.on("Sample Inward", {
    date(frm) {
        validate_challan_date(frm);
    },

    challan_date(frm) {
        validate_challan_date(frm);
    },
    quantity(frm) {
        if (!frm.doc.quantity) return;
        frm.call({
            method: "update_material_rows",
            doc: frm.doc,
            callback: function () {
                frm.refresh_field("material_details");
            }
        });
    },
    refresh: function (frm) {
        frm.set_query("material_specification", "test_on_sample", function () {
            return {
                filters: {
                    name: ["in", (frm.doc.material_details || [])
                        .map(d => d.material_specification)
                        .filter(Boolean)
                    ]
                }
            };
        });
        frm.set_query("test_method", "test_on_sample", function () {
            return {
                filters: [
                    ["Test Method", "name", "in", item1]
                ]
            }
        });
        frm.set_query("test_description", "test_on_sample", function () {
            return {
                filters: [
                    ["Test Description", "name", "in", description]
                ]
            }
        });
    },
    onload(frm) {
        frm.page.sidebar.hide();
        // frm.doc.material_details.forEach(row => {
        //     if (row.material_specification) {
        //         items.push(row.material_specification);
        //     }
        // })
    },
    get_sample(frm) {
        frappe.call({
            method: "get_material_sample_details",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("test_on_sample");
                // frm.reload_doc(); 
            }
        });
    }

});
// **************************************************************************************************
frappe.ui.form.on("Material Details", {
    // material_specification(frm, cdt, cdn) {
    //     update_items_array(frm);
    // },
    // material_details_remove(frm, cdt, cdn) {
    //     update_items_array(frm);
    // },
    // onload(frm) {
    //     update_items_array(frm);
    // },
    material_details_remove(frm, cdt, cdn) {
        // update_items_array(frm);
        call_cutting_row_update(frm);
        frm.refresh_field("test_on_sample");
    },
    material_dimension(frm, cdt, cdn) {
        call_cutting_row_update(frm);
    },
    material_specification(frm, cdt, cdn) {
        call_cutting_row_update(frm);
        frm.refresh_field("test_on_sample");
    },
    material_details_add: function (frm, cdt, cdn) {
        let qty = frm.doc.quantity || 0;
        let rows = frm.doc.material_details.length;
        if (rows > qty) {
            frappe.msgprint(
                __("You cannot add more than {0} Material Details rows because Quantity is {0}", [qty])
            );
            frm.doc.material_details.pop();
            frm.refresh_field("material_details");
            return false;
        }
    }
});
// **************************************************************************************************
// function update_items_array(frm) {
//     items = []; // clear first
//     (frm.doc.material_details || []).forEach(row => {
//         if (row.material_specification) {
//             items.push(row.material_specification);
//         }
//     });
//     console.log("Updated items:", items);
// }
// **************************************************************************************************
function call_cutting_row_update(frm) {
    frm.call({
        method: "update_cutting_rows",
        doc: frm.doc,
        callback: function () {
            frm.refresh_field("cutting_charge");
            frm.refresh_field("machining_charge");
        }
    });
}
// **************************************************************************************************

frappe.ui.form.on("Test On sample", {
    material_specification(frm, cdt, cdn) {
        let c = locals[cdt][cdn];

        let m = (frm.doc.material_details || []).find(
            r => r.material_specification === c.material_specification
        );

        if (m) {
            frappe.model.set_value(cdt, cdn, "heat_number", m.heat_number);
        }
    },
    test_group(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "test_method", "");
        if (!child.test_group) {
            return;
        }
        item1 = [];
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Test Method",
                filters: { test_group: child.test_group },
                fields: ["name"]
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    r.message.forEach(row => {
                        item1.push(row.name);
                    });
                    frappe.meta.get_docfield("Test On Sample", "test_method", frm.doc.name).options = item1;
                    frm.refresh_field("test_on_sample");
                }
            }
        });
    },
    test_method(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "test_description", "");

        if (child.test_method) {
            frappe.db.get_value("Test Method", child.test_method, "group", (r) => {
                if (r && r.group) {
                    frappe.model.set_value(cdt, cdn, "group", r.group);
                } else {
                    frappe.model.set_value(cdt, cdn, "group", 0);
                }
            });
        }
        else {
            frappe.model.set_value(cdt, cdn, "price", 0);
        }
        description = [];

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Test Description",
                filters: { test_method: child.test_method },
                fields: ["name"]
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    r.message.forEach(row => {
                        description.push(row.name);
                    });
                    frappe.meta.get_docfield("Test On Sample", "test_description", frm.doc.name).options = description;
                    frm.refresh_field("test_on_sample");
                }
            }
        });

    },
  test_description: function (frm, cdt, cdn) {
     let child = locals[cdt][cdn]; is_default == true; 
     if (child.test_description) {
         frappe.db.get_value("Test Description", child.test_description, "rate", (r) => { 
            if (r && r.rate) { 
                frappe.model.set_value(cdt, cdn, "price", r.rate); 
            } else { 
                frappe.model.set_value(cdt, cdn, "price", 0); 
            } 
        }); 
    } else {
         frappe.model.set_value(cdt, cdn, "price", 0); 
        } 
    }
});
// **************************************************************************************************
frappe.ui.form.on("Machining Charge", {
    processing_charges(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.processing_charges || !row.material_type || !row.thik_dia) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Material Type",
                name: row.material_type
            },
            callback(r) {
                if (!r.message) return;

                let charge = 0;

                (r.message.sample_preparation_charges || []).some(d => {
                    if (d.processing_charges !== row.processing_charges) {
                        return false;
                    }

                    // IF-ELSE Structure
                    if (d.is_fix) {
                        charge = d.charges;
                        return true;
                    } else if (row.thik_dia >= d.from_range && row.thik_dia <= d.to_range) {
                        charge = d.charges;
                        return true;
                    } else {
                        return false;
                    }
                });

                frappe.model.set_value(cdt, cdn, "charge", charge);
                calculate_total(cdt, cdn);
            }
        });
    },
    charge(frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    },

    quantity(frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    },

    materials(frm, cdt, cdn) {
        let cur = locals[cdt][cdn];
        if (!cur.materials) return;

        (frm.doc.machining_charge || []).forEach(r => {
            if (r.name === cur.name) return;

            if (r.materials === cur.materials) {
                cur.material_type = r.material_type;
                cur.description = r.description;
                cur.processing_charges = r.processing_charges;
                cur.thik_dia = r.thik_dia;
                cur.charge = r.charge;
                calculate_total(cdt, cdn);
                frm.refresh_field("machining_charge");
            }
        });
    }
});

function calculate_total(cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.model.set_value(
        cdt,
        cdn,
        "total",
        (row.charge || 0) * (row.quantity || 1)
    );
}




