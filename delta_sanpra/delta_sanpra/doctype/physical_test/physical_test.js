// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Physical Test", {
	refresh(frm) {
        // frappe.msgprint("Refresh called");
        set_test_method_filter(frm);
        if (!frm.is_new()) {
            frm.add_custom_button("Generate ULR", function () {
                frm.call({
                    method: "set_ulr_counter",
                    doc: frm.doc,
                    callback: function (r) {
                        if (r.message) {
                            let count = r.message.toString().padStart(9, '0');
                            let prefix = "TC1384426";
                            let suffix = "F";
                            let newCode = prefix + count + suffix;
                            frm.set_value("ulr_no", newCode).then(() => {
                                frappe.msgprint("ULR No Generated Successfully");
                            });
                        }
                    }
                });
            });
        }
        frm.set_query("parameter", "test_details", function () {
            return {
                filters: [
                    ["Chemical Parameter", "name", "in", items]
                ]
            }
        })
	},
    onload(frm) {
        let original_print = frm.print_doc || frm.print_preview;
        frm.print_doc = function () {
            frm.set_value("is_print", 1);
            frm.save_or_update();
            original_print.call(frm);
        };
    },
    test_group(frm){
        frm.set_value('test_method',null),
        set_test_method_filter(frm);
    },
    add_data(frm) {
        frappe.call({
            method: "add_data",
            doc: frm.doc,
            callback: function (r) {
                frm.refresh_field("brinell_hardness_child")
            }
        })
    },
    range1: calculate_avg,
    range2: calculate_avg,
    range3: calculate_avg,
    range4: calculate_avg,
    range5: calculate_avg,
    range6: calculate_avg
});
function set_test_method_filter(frm) {
    frm.set_query('test_method', function () {
        return {
            filters: {
                test_group: frm.doc.test_group || ''
            }
        };
    });
}
function calculate_avg(frm) {
    let total = 0;
    let count = 0;
    let ranges = [
        frm.doc.range1,
        frm.doc.range2,
        frm.doc.range3,
        frm.doc.range4,
        frm.doc.range5,
        frm.doc.range6
    ];
    ranges.forEach(value => {
        if (value) {  
            total += value;
            count++;
        }
    });
    frm.set_value(
        "average_aboserbed_energy_of_one_set",
        count ? total / count : 0
    );
}