// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("ASME Section IX Test", {
	refresh(frm) {
        set_test_method_filter(frm);
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
    }
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
