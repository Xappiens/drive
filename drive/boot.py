import frappe


def get_boot_info(boot_info):
    """Add Drive integration settings to Frappe boot info.
    
    This allows the frontend to know if Drive attachments integration
    is enabled without making additional API calls.
    """
    try:
        settings = get_integration_settings()
        boot_info.drive_integration = settings
    except Exception:
        boot_info.drive_integration = {
            "enabled": False,
            "embed_in_sidebar": False,
            "show_attachments_in_drive": False,
            "excluded_doctypes": []
        }


def get_integration_settings():
    """Get Drive integration settings with caching."""
    cache_key = "drive_integration_settings"
    cached = frappe.cache().get_value(cache_key)
    
    if cached:
        return cached
    
    if not frappe.db.exists("DocType", "Drive Integration Settings"):
        return {
            "enabled": False,
            "embed_in_sidebar": False,
            "show_attachments_in_drive": False,
            "excluded_doctypes": []
        }
    
    try:
        doc = frappe.get_single("Drive Integration Settings")
        settings = {
            "enabled": bool(doc.enabled),
            "embed_in_sidebar": bool(doc.embed_in_sidebar),
            "show_attachments_in_drive": bool(doc.show_attachments_in_drive),
            "excluded_doctypes": [
                d.doctype_name for d in (doc.excluded_doctypes or [])
            ]
        }
    except Exception:
        settings = {
            "enabled": False,
            "embed_in_sidebar": False,
            "show_attachments_in_drive": False,
            "excluded_doctypes": []
        }
    
    frappe.cache().set_value(cache_key, settings, expires_in_sec=300)
    return settings
