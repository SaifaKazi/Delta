// Copyright (c) 2025, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Test Description", {
	// refresh(frm) {

	// },
    test_group: function(frm) {
        if (frm.doc.test_group) {
            frm.set_query("test_method", function() {
                return {
                    filters: {
                        test_group: frm.doc.test_group
                    }
                };
            });

        }
        frm.set_value("test_method", "");
    }
});
