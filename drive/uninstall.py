import frappe


def before_uninstall():
    """Cleanup before uninstalling Drive.
    
    Note: We do NOT touch Frappe's File documents.
    All attachments remain intact after Drive is uninstalled.
    """
    frappe.cache().delete_key("drive_integration_settings")
    frappe.cache().delete_key("drive_doctypes_with_attachments")
    
    frappe.log("Drive uninstalled. Frappe attachments (File documents) remain unchanged.")
