"""
Carga archivos de ejemplo (demo) en Drive para demostraciones.
Los archivos se leen desde drive/demo_files/ y se crean en un equipo compartido
"Archivos de ejemplo" visible para todos los usuarios con Drive.
"""
import os
from pathlib import Path

import frappe
from werkzeug.utils import secure_filename

from drive.utils import (
    create_drive_file,
    get_home_folder,
    update_file_size,
)
from drive.utils.files import FileManager

from .files import create_folder, get_upload_path


# Títulos traducibles: en .po (es, en, etc.) con msgid "Sample files"
def _demo_folder_title():
    return frappe._("Sample files")


def _demo_team_title():
    return frappe._("Sample files")


def get_demo_files_path():
    """Ruta a la carpeta demo_files dentro de la app."""
    return Path(frappe.get_app_path("drive", "demo_files"))


def _users_with_drive():
    """Usuarios que tienen Drive (Settings o pertenecen a algún equipo)."""
    users = set(frappe.get_all("Drive Settings", pluck="user"))
    users |= set(frappe.get_all("Drive Team Member", pluck="user"))
    users.discard("Guest")
    return users


def get_or_create_demo_team():
    """
    Obtiene o crea el equipo "Archivos de ejemplo" y asegura que todos
    los usuarios con Drive sean miembros. Así los archivos demo son públicos.
    """
    demo_team_title = _demo_team_title()
    existing = frappe.db.exists(
        "Drive Team",
        {"title": demo_team_title, "owner": "Administrator", "personal": 0},
    )
    if existing:
        team_name = existing
    else:
        # Crear equipo como Administrator para que sea el dueño
        prev = frappe.session.user
        frappe.set_user("Administrator")
        try:
            team = frappe.get_doc(
                {
                    "doctype": "Drive Team",
                    "title": demo_team_title,
                    "personal": 0,
                }
            )
            team.insert()
            team_name = team.name
        finally:
            frappe.set_user(prev)

    team_doc = frappe.get_doc("Drive Team", team_name)
    current_users = {m.user for m in team_doc.users}
    added = False
    for user in _users_with_drive():
        if user not in current_users:
            team_doc.append("users", {"user": user, "access_level": 1})
            added = True
    if added:
        team_doc.save(ignore_permissions=True)
    return team_name


@frappe.whitelist()
def load_demo_files(team=None):
    """
    Crea la carpeta "Archivos de ejemplo" en un equipo compartido y copia
    los archivos de demo_files. Visible para todos los usuarios con Drive.
    Idempotente: si la carpeta ya existe, añade solo los archivos que falten.
    """
    if team is None or team == "home":
        team = get_or_create_demo_team()

    home_folder = get_home_folder(team)
    if not home_folder:
        frappe.throw("No se encontró la carpeta inicial del equipo.")

    demo_path = get_demo_files_path()
    if not demo_path.exists():
        frappe.throw(f"No existe la carpeta de archivos de ejemplo: {demo_path}")

    demo_folder_title = _demo_folder_title()
    # Obtener o crear carpeta de ejemplo (título traducido al idioma actual)
    existing = frappe.db.exists(
        "Drive File",
        {
            "parent_entity": home_folder["name"],
            "is_group": 1,
            "title": demo_folder_title,
            "is_active": 1,
            "team": team,
        },
    )
    if existing:
        demo_folder_name = existing
    else:
        folder_doc = create_folder(team, demo_folder_title, parent=home_folder["name"])
        demo_folder_name = folder_doc.name

    manager = FileManager()
    created = []

    for path in sorted(demo_path.iterdir()):
        if path.is_dir() or path.name.startswith("."):
            continue
        title = path.name
        # Evitar duplicados por nombre
        if frappe.db.exists(
            "Drive File",
            {"parent_entity": demo_folder_name, "title": title, "is_active": 1},
        ):
            continue

        file_size = path.stat().st_size
        last_modified = path.stat().st_mtime
        mime_type = _get_mime_type(path)

        temp_name = f"demo_{secure_filename(title)}"
        temp_path = get_upload_path(home_folder["path"], temp_name)
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(path.read_bytes())

        try:
            drive_file = create_drive_file(
                team,
                title=title,
                parent=demo_folder_name,
                mime_type=mime_type,
                entity_path=lambda e: manager.get_disk_path(e, home_folder),
                file_size=file_size,
                last_modified=last_modified,
            )
            manager.upload_file(temp_path, drive_file, create_thumbnail=True)
            update_file_size(demo_folder_name, file_size)
            created.append(title)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    return {
        "folder": demo_folder_title,
        "folder_entity": demo_folder_name,
        "demo_team": team,
        "files_created": created,
        "message": f"Se crearon {len(created)} archivo(s) de ejemplo en '{demo_folder_title}'.",
    }


def _get_mime_type(path):
    """Mime type simple por extensión para los archivos de demo."""
    ext = path.suffix.lower()
    if ext in (".txt",):
        return "text/plain"
    if ext in (".md",):
        return "text/markdown"
    if ext in (".html",):
        return "text/html"
    if ext in (".json",):
        return "application/json"
    return "application/octet-stream"
