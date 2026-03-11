// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Print Test Report", {
    get_data(frm) {
        frappe.call({
            method: "get_data",
            doc: frm.doc,
            callback: function (r) {
                if (!r.exc) {
                    frm.refresh_field("items");
                }
            }
        });
    },
});