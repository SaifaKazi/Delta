// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Other Test", {
	refresh(frm) {
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
	},
    onload(frm) {
        let original_print = frm.print_doc || frm.print_preview;
        frm.print_doc = function () {
            frm.set_value("is_print", 1);
            frm.save_or_update();
            original_print.call(frm);
        };
    },
});
