<h1 align="center">whythis</h1>
<p align="center">
  🇺🇸 <a href="README.md"><b>English</b></a> |
  🇪🇸 <b>Español</b>
</p>
<h3 align="center">whythis es una pequeña herramienta CLI que te permite adjuntar explicaciones humanas a archivos de tu sistema, de forma rápida y eficiente ;)</h3>

---

Responde a una pregunta muy simple:

> **¿Por qué existe este archivo?**

En lugar de adivinar meses después por qué existe `fix_final_v2_REAL.sh` o `temp_patch.py`, puedes preguntarle a `whythis`.

---

## Qué hace

* Guarda explicaciones **fuera** de tus proyectos (no modifica archivos)
* Rastrea archivos mediante **ruta absoluta + hash SHA256**
* Detecta cuando los archivos son **movidos**, **eliminados** o **modificados**
* Funciona con cualquier tipo de archivo
* Ligero, local y sin dependencias

Todos los metadatos se almacenan localmente en:

```
~/.whythis/db.json
```

---

## Instalación

Clona el repositorio y ejecuta el instalador:

```bash
git clone https://github.com/URDev4ever/whythis.git
cd whythis
chmod +x installer.sh
sudo ./installer.sh install
```

Esto instala `whythis` de forma global (por defecto en `/usr/local/bin`).

Para desinstalar:

```bash
sudo ./installer.sh uninstall
```

> La base de datos en `~/.whythis/` se conserva por defecto.

---

## Uso básico

### Agregar una explicación

```bash
whythis add script.sh "Solución temporal para un problema en producción"
```

> [ ! ] Asegúrate de usar comillas (" ") para que funcione.

Con etiquetas:

```bash
whythis add script.sh "Hotfix para un bug de la API" --tags prod,hotfix
```

> [ ! ] SIN espacios ("--tags tag1 tag2" no funciona, formato correcto: "--tags tag1,tag2").

---

### Preguntar por qué existe un archivo

```bash
whythis why script.sh
```

Salida de ejemplo:

```
📄 script.sh
❓ Por qué: Solución temporal para un problema en producción
👤 Por: TuUsuario
🕒 Agregado: 2025-12-25 18:40
📁 Ubicación original: /home/user/project
🔒 Verificación de hash: OK
```

---

### Listar todos los archivos explicados

```bash
whythis list
```

Filtrar por etiquetas:

```bash
whythis list --tags prod
```

---

### Buscar explicaciones

```bash
whythis search prod
```

Busca en:

* explicaciones
* rutas de archivos
* etiquetas

---

### Editar una explicación

```bash
whythis edit script.sh --explanation "Arreglo permanente después del refactor"
```

Actualizar etiquetas:

```bash
whythis edit script.sh --tags refactor,cleanup
```

---

### Eliminar una explicación

```bash
whythis rm script.sh
```

Funciona incluso si el archivo fue movido (coincidencia basada en hash).

---

## Cómo funciona (visión técnica)

* Los archivos se indexan por **ruta absoluta**
* Cada entrada guarda un **hash SHA256**
* Si un archivo se mueve, `whythis` lo encuentra mediante comparación de hash
* Si un archivo se modifica, se muestra una advertencia
* Si un archivo se elimina, la explicación sigue siendo accesible

Sin metadatos del sistema de archivos, sin hooks de git, sin modificar archivos.

---

## Formato de datos

Ejemplo de entrada en `~/.whythis/db.json`:

```json
{
  "/home/user/project/script.sh": {
    "why": "Solución temporal para un problema en producción",
    "created_at": "2025-12-25T18:40:00",
    "author": "TuUsuario",
    "hash": "sha256:abcd1234...",
    "cwd": "/home/user/project",
    "tags": ["prod", "hotfix"]
  }
}
```

---

## Requisitos

* Python 3.8+
* Linux / macOS (Windows vía WSL o instalación manual)

Sin dependencias externas de Python.

---

## Estado

Versión temprana.
La herramienta es funcional pero intencionalmente minimalista.

Ideas futuras:

* contexto de git (commit / branch)
* comando de relink para archivos movidos
* modos de salida JSON / texto plano

---

Hecho con <3 por URDev.
