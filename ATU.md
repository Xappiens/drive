# Drive ATU

Fork interno de [Frappe Drive](https://github.com/frappe/drive) para desarrollo propio.

- **Repositorio:** https://gitlab.xappiens.es/atu/drive
- **Base:** rama `main` de frappe/drive (incluye wiki_integration, docs API, plantillas de email).

## Desarrollo local

1. Clonar (o ya tienes `drive-main/drive-main` con remote apuntando a ATU/drive).
2. Instalar en un bench de Frappe:
   ```bash
   bench get-app drive --branch main  # o clonar desde gitlab.xappiens.es/atu/drive
   bench install-app drive
   bench start
   ```
3. Para desarrollo del frontend: `npm run dev` (o `pnpm dev`) dentro de `frontend/`.

## Próximos pasos posibles

- Ajustar branding / textos para ATU.
- Añadir el patch `add_drive_user_role` desde develop si queréis asignar el rol "Drive User" a usuarios existentes.
- Configurar CI (por ejemplo linters como en develop) en GitLab.
