import frappe
from frappe import _
from frappe.model.document import Document


class DriveIntegrationSettings(Document):
    def validate(self):
        if self.enabled and not self.embed_in_sidebar and not self.show_attachments_in_drive:
            frappe.msgprint(
                _("Integration is enabled but no features are active. "
                  "Enable at least one of: Embed in Sidebar or Show in Drive."),
                indicator="orange",
                alert=True
            )

    def on_update(self):
        frappe.cache().delete_key("drive_integration_settings")
        
        # Get excluded doctypes list
        excluded = [d.doctype_name for d in self.excluded_doctypes] if self.excluded_doctypes else []
        
        frappe.publish_realtime(
            "drive_integration_settings_updated",
            {
                "enabled": self.enabled,
                "embed_in_sidebar": self.embed_in_sidebar,
                "show_attachments_in_drive": self.show_attachments_in_drive,
                "excluded_doctypes": excluded
            },
            after_commit=True
        )
        frappe.msgprint(
            _("Settings saved. Users may need to refresh their browser for changes to take effect."),
            indicator="green",
            alert=True
        )
