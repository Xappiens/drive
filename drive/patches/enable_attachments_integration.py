import frappe


def execute():
    """
    Patch for existing installations.
    Creates the integration settings document if it doesn't exist.
    Does NOT enable automatically - admin must do it manually.
    """
    if not frappe.db.exists("DocType", "Drive Integration Settings"):
        return
    
    if frappe.db.exists("Drive Integration Settings", "Drive Integration Settings"):
        return
    
    try:
        doc = frappe.new_doc("Drive Integration Settings")
        doc.enabled = 0
        doc.embed_in_sidebar = 1
        doc.show_attachments_in_drive = 1
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to create Drive Integration Settings: {e}")
