import click


@click.command("load-demo-files")
@click.option("--user", "-u", default=None, help="Usuario para el que cargar los archivos (por defecto: sesión actual)")
@click.pass_context
def load_demo_files_cmd(ctx, user=None):
    """
    Carga la carpeta "Archivos de ejemplo" en Drive con los ficheros de demo.
    Ejemplo: bench --site sitename load-demo-files
             bench --site sitename load-demo-files --user user@example.com
    """
    import frappe
    sites = (ctx.parent and ctx.parent.obj and ctx.parent.obj.get("sites")) or []
    site = sites[0] if sites else None
    if site:
        frappe.init(site=site)
    frappe.connect()
    if user:
        frappe.set_user(user)
    else:
        frappe.set_user("Administrator")
    try:
        out = frappe.call("drive.api.demo.load_demo_files")
        who = frappe.session.user
        click.echo(out.get("message", "Listo."))
        click.echo(f"Usuario: {who}")
        if who != "Administrator":
            click.echo("Para otro usuario: bench --site <site> load-demo-files --user email@ejemplo.com")
        if out.get("files_created"):
            for f in out["files_created"]:
                click.echo(f"  - {f}")
    finally:
        frappe.destroy()


commands = [load_demo_files_cmd]
