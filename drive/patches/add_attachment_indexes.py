import frappe


def execute():
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
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to create attachment index: {e}")
