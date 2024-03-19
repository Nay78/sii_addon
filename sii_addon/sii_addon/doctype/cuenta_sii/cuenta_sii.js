// Copyright (c) 2024, NM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cuenta SII", {
  refresh(frm) {
    frm.add_custom_button(
      __("Run scrappe method"),
      function () {
        frappe.call({
          method: "sii_addon.sii_addon.doctype.cuenta_sii.cuenta_sii.scrappe",
        });
      },
      __("Utilities")
    );
  },
});
