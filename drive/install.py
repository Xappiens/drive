import frappe


def after_install():
    create_fulltext_index()
    setup_integration_settings()


def after_migrate():
    """Run after bench migrate to ensure settings exist."""
    setup_integration_settings()
    add_file_attachment_indexes()


def create_fulltext_index():
    """Create fulltext index for Drive File title search."""
    index_check = frappe.db.sql(
        """SHOW INDEX FROM `tabDrive File` WHERE Key_name = 'drive_file_title_fts_idx'"""
    )
    if not index_check:
        frappe.db.sql(
            """ALTER TABLE `tabDrive File` ADD FULLTEXT INDEX drive_file_title_fts_idx (title)"""
        )


def setup_integration_settings():
    """Create Drive Integration Settings document if it doesn't exist."""
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


def add_file_attachment_indexes():
    """Add indexes to File table for faster attachment queries."""
    try:
        existing_indexes = frappe.db.sql(
            """SHOW INDEX FROM `tabFile` WHERE Key_name = 'idx_file_attached_doctype'""",
            as_dict=True
        )
        if not existing_indexes:
            frappe.db.sql(
                """CREATE INDEX idx_file_attached_doctype ON `tabFile` (attached_to_doctype)"""
            )
    except Exception:
        pass
