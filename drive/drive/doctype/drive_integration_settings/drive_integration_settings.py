import frappe
from frappe.model.document import Document


class DriveIntegrationSettings(Document):
    def validate(self):
        if self.enabled and not self.embed_in_sidebar and not self.show_attachments_in_drive:
            frappe.msgprint(
                "Integration is enabled but no features are active. "
                "Enable at least one of: Embed in Sidebar or Show in Drive.",
                indicator="orange",
                alert=True
            )

    def on_update(self):
        frappe.cache().delete_key("drive_integration_settings")
