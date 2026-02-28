"""
Attachments API for Drive Integration

This module provides endpoints to browse Frappe attachments (File documents)
through Drive's interface, treating DocTypes and Documents as virtual folders.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_doctypes_with_attachments(search=None, limit=50, offset=0):
    """
    Get list of DocTypes that have attachments.
    
    Args:
        search: Optional search term to filter DocTypes
        limit: Maximum number of results
        offset: Pagination offset
    
    Returns:
        List of dicts with doctype name and file count
    """
    cache_key = f"drive_doctypes_attachments_{search or 'all'}_{limit}_{offset}"
    cached = frappe.cache().get_value(cache_key)
    
    if cached and not search:
        return cached
    
    conditions = "WHERE attached_to_doctype IS NOT NULL AND attached_to_doctype != ''"
    
    if search:
        conditions += f" AND attached_to_doctype LIKE '%{frappe.db.escape(search, percent=False)}%'"
    
    result = frappe.db.sql(f"""
        SELECT 
            attached_to_doctype as doctype,
            COUNT(*) as file_count,
            MAX(modified) as last_modified
        FROM `tabFile`
        {conditions}
        GROUP BY attached_to_doctype
        ORDER BY file_count DESC
        LIMIT %s OFFSET %s
    """, (limit, offset), as_dict=True)
    
    filtered_result = []
    for row in result:
        if frappe.has_permission(row.doctype, "read"):
            try:
                meta = frappe.get_meta(row.doctype)
                row["doctype_label"] = meta.get("name") or row.doctype
                row["icon"] = meta.get("icon") or "file"
                filtered_result.append(row)
            except Exception:
                pass
    
    if not search:
        frappe.cache().set_value(cache_key, filtered_result, expires_in_sec=300)
    
    return filtered_result


@frappe.whitelist()
def get_documents_with_attachments(doctype, search=None, limit=50, offset=0):
    """
    Get list of documents of a DocType that have attachments.
    
    Args:
        doctype: The DocType to query
        search: Optional search term to filter documents
        limit: Maximum number of results
        offset: Pagination offset
    
    Returns:
        List of dicts with document name and attachment count
    """
    if not frappe.has_permission(doctype, "read"):
        frappe.throw(_("No permission to access {0}").format(doctype), frappe.PermissionError)
    
    conditions = "WHERE attached_to_doctype = %s"
    params = [doctype]
    
    if search:
        conditions += " AND attached_to_name LIKE %s"
        params.append(f"%{search}%")
    
    params.extend([limit, offset])
    
    result = frappe.db.sql(f"""
        SELECT 
            attached_to_name as document_name,
            COUNT(*) as file_count,
            SUM(file_size) as total_size,
            MAX(modified) as last_modified
        FROM `tabFile`
        {conditions}
        GROUP BY attached_to_name
        ORDER BY last_modified DESC
        LIMIT %s OFFSET %s
    """, params, as_dict=True)
    
    meta = frappe.get_meta(doctype)
    title_field = meta.get_title_field() or "name"
    
    for row in result:
        if not frappe.has_permission(doctype, "read", row.document_name):
            continue
        
        if title_field != "name":
            try:
                row["title"] = frappe.db.get_value(doctype, row.document_name, title_field)
            except Exception:
                row["title"] = row.document_name
        else:
            row["title"] = row.document_name
    
    return [r for r in result if frappe.has_permission(doctype, "read", r.document_name)]


@frappe.whitelist()
def get_document_files(doctype, docname, include_referenced=True):
    """
    Get all files associated with a specific document.
    
    Args:
        doctype: The DocType
        docname: The document name
        include_referenced: If True, also include files referenced in Attach/Image fields
    
    Returns:
        List of file documents with metadata
    """
    if not frappe.has_permission(doctype, "read", docname):
        frappe.throw(_("No permission to access this document"), frappe.PermissionError)
    
    attachments = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": doctype,
            "attached_to_name": docname
        },
        fields=[
            "name", "file_name", "file_url", "file_size", 
            "is_private", "file_type", "modified", "owner"
        ],
        order_by="modified desc"
    )
    
    for att in attachments:
        att["source"] = "attachment"
        att["mime_type"] = get_mime_type(att.get("file_name", ""))
    
    if include_referenced:
        referenced = get_referenced_files(doctype, docname)
        for ref in referenced:
            if not any(a["name"] == ref["name"] for a in attachments):
                ref["source"] = "field"
                attachments.append(ref)
    
    return attachments


def get_referenced_files(doctype, docname):
    """Get files referenced in Attach and Image fields of a document."""
    meta = frappe.get_meta(doctype)
    attach_fields = [
        f.fieldname for f in meta.fields 
        if f.fieldtype in ("Attach", "Attach Image", "Image")
    ]
    
    if not attach_fields:
        return []
    
    doc = frappe.get_doc(doctype, docname)
    referenced_files = []
    
    for fieldname in attach_fields:
        file_url = doc.get(fieldname)
        if not file_url:
            continue
        
        file_doc = frappe.db.get_value(
            "File",
            {"file_url": file_url},
            ["name", "file_name", "file_url", "file_size", "is_private", "file_type", "modified", "owner"],
            as_dict=True
        )
        
        if file_doc:
            file_doc["field"] = fieldname
            file_doc["mime_type"] = get_mime_type(file_doc.get("file_name", ""))
            referenced_files.append(file_doc)
    
    return referenced_files


@frappe.whitelist()
def get_attachment_counts():
    """Get total counts for attachments summary."""
    if not frappe.has_permission("File", "read"):
        return {"total_files": 0, "total_doctypes": 0}
    
    result = frappe.db.sql("""
        SELECT 
            COUNT(DISTINCT attached_to_doctype) as total_doctypes,
            COUNT(*) as total_files,
            SUM(file_size) as total_size
        FROM `tabFile`
        WHERE attached_to_doctype IS NOT NULL 
          AND attached_to_doctype != ''
    """, as_dict=True)
    
    return result[0] if result else {"total_files": 0, "total_doctypes": 0, "total_size": 0}


def get_mime_type(filename):
    """Get MIME type from filename."""
    import mimetypes
    if not filename:
        return "application/octet-stream"
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


@frappe.whitelist()
def check_document_access(doctype, docname):
    """Check if current user has access to a document's attachments."""
    try:
        has_access = frappe.has_permission(doctype, "read", docname)
        return {"has_access": has_access}
    except Exception:
        return {"has_access": False}
