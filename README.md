# CTF Report Forge

CTF Report Forge es una herramienta web **local-first** para documentar máquinas de CTF, laboratorios de pentesting y hallazgos técnicos sin sacar tus datos de tu equipo. Está pensada para estudiantes, pentesters, jugadores de HackTheBox/TryHackMe/VulnHub/DockerLabs y personas que quieren convertir notas técnicas en reportes exportables.

> Estado actual: **beta local**. La app ya es usable para documentar y exportar reportes, pero todavía no debe tratarse como una plataforma multiusuario ni como una aplicación lista para internet.

## Aviso Local-First

Esta herramienta guarda la información en tu máquina:

- Base de datos SQLite local: `db.sqlite3`.
- Imágenes subidas: `media/`.
- Reportes generados: `exports/`.
- No incluye login, usuarios, permisos ni autenticación por diseño.
- No debe exponerse a internet ni ejecutarse en servidores públicos.
- No subas `db.sqlite3`, `media/`, `exports/`, flags reales, capturas sensibles ni reportes generados a repositorios públicos.

Recomendación: ejecútala escuchando en `127.0.0.1` y úsala únicamente para entornos autorizados, CTFs, laboratorios o reportes internos.

## Qué Ofrece en Beta

### Gestión de máquinas y reportes

- Dashboard de máquinas documentadas.
- Registro de nombre, plataforma, dificultad, sistema operativo, IP objetivo, autor y estado.
- Idioma del reporte: español o inglés.
- Tipo de reporte:
  - CTF / HackTheBox / TryHackMe.
  - Bug bounty.
  - Pentest corporativo.
- Campos extra para cliente, alcance y descripción ejecutiva en reportes no CTF.

### Flujo por fases

La documentación se organiza siguiendo un flujo técnico:

- Reconocimiento.
- Identificación de vulnerabilidades.
- Explotación.
- Reconocimiento interno.
- Movimiento de usuario.
- Escalada de privilegios.
- Notas.
- Flags capturadas.
- Galería de capturas.

Cada fase puede contener evidencias, comandos, outputs, explicaciones técnicas e imágenes asociadas.

### Evidencias

- Bloques de evidencia por fase.
- Campo para comando ejecutado.
- Campo para output bruto.
- Explicación técnica.
- Orden manual por número.
- Adjuntar múltiples capturas desde el formulario.
- Pegar capturas directamente desde el portapapeles.
- Previsualizar imágenes antes de guardar.
- Quitar imágenes pegadas o seleccionadas antes de enviar el formulario.

### Vulnerabilidades

- Registro de vulnerabilidades con:
  - título,
  - tipo,
  - severidad,
  - servicio/componente afectado,
  - puerto/protocolo,
  - CVE,
  - cómo fue identificada,
  - evidencia o PoC,
  - impacto,
  - recomendación.
- Adjuntar capturas a la vulnerabilidad.
- Las capturas adjuntas quedan marcadas automáticamente en la fase de identificación de vulnerabilidades.

### Exploits

- Registro de técnicas o exploits usados.
- Asociación opcional con una vulnerabilidad ya registrada.
- Tipo de exploit: técnica manual, exploit custom, GitHub, Searchsploit, Metasploit, PoC pública u otro.
- Objetivo: acceso inicial, RCE, credenciales, pivoting, escalada de privilegios o PoC.
- Campos para CVE, URL, ruta local, servicio/puerto afectado, comando usado, output, resultado y explicación.
- Capturas adjuntas marcadas automáticamente como explotación.

### Flags

- Registro de flags tipo `user.txt`, `root.txt`, `local.txt`, `proof.txt` u otras.
- Valor de la flag con opción de censura para el reporte.
- Ubicación o ruta donde se encontró.
- Usuario con el que se obtuvo.
- Fase en la que fue encontrada.
- Comando o comandos usados para obtenerla.
- Notas adicionales.

### Capturas de pantalla

- Subida de capturas PNG, JPG, JPEG y WEBP.
- Asociación opcional a evidencia, vulnerabilidad o exploit.
- Fase, título, caption, descripción y orden de galería.
- Galería global de capturas dentro de cada máquina.
- Limpieza automática de archivos cuando se elimina una captura.
- Limpieza de carpetas `media/` y `exports/` asociadas cuando se elimina una máquina.

### Reordenamiento

Desde el detalle de una máquina puedes reordenar elementos arrastrando el asa de cada tarjeta:

- Evidencias dentro de su fase.
- Vulnerabilidades dentro de la fase de identificación.
- Exploits dentro de la fase de explotación.

El orden se guarda automáticamente en la base de datos local.

### Exportación

La pantalla de exportación ofrece:

- Generar LaTeX solamente.
- Generar LaTeX y descargar el PDF desde la página.
- Exportar Markdown como ZIP.

El ZIP Markdown incluye:

- `report.md`.
- `assets/screenshots/` con las imágenes referenciadas desde el Markdown.

El PDF requiere que `latexmk` y una distribución LaTeX estén instalados en el sistema. Si no están disponibles, puedes generar el `main.tex` y compilarlo manualmente con tu herramienta preferida.

## Requisitos

- Python 3.11 o superior.
- Django 4.2.
- SQLite, incluido por defecto con Python.
- Pillow para validación de imágenes.
- Jinja2 para plantillas LaTeX.
- `latexmk` opcional para compilar PDF desde la interfaz.

Dependencias Python:

```bash
pip install -r requirements.txt
```

Para PDF automático instala una distribución LaTeX. En Debian/Ubuntu, por ejemplo:

```bash
sudo apt install texlive-latex-extra latexmk
```

## Instalación

1. Clona el proyecto:

```bash
git clone https://github.com/TomasGutierrezOrozco/ctf-report-forge.git
cd ctf-report-forge
```

2. Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Aplica migraciones:

```bash
python manage.py migrate
```

5. Levanta el servidor local:

```bash
python manage.py runserver 127.0.0.1:8000
```

6. Abre la app:

```text
http://127.0.0.1:8000/
```

## Flujo de Uso Recomendado

1. Crea una máquina desde el dashboard.
2. Completa datos básicos: plataforma, dificultad, OS, IP, autor, idioma y tipo de reporte.
3. Añade evidencias por fase mientras trabajas.
4. Registra vulnerabilidades cuando identifiques problemas concretos.
5. Registra exploits o técnicas usadas para validar impacto.
6. Guarda flags con fase y comandos usados.
7. Adjunta capturas pegándolas con `Ctrl + V` o seleccionándolas desde el formulario.
8. Reordena tarjetas arrastrándolas si necesitas corregir la narrativa.
9. Exporta a PDF o Markdown ZIP desde `Export Report`.

## Estructura del Proyecto

```text
ctf-report-forge/
├── manage.py
├── requirements.txt
├── README.md
├── ctf_report_forge/        # Configuración Django
├── reports/                 # App principal
│   ├── models.py            # Modelos de máquinas, evidencias, flags, etc.
│   ├── forms.py             # Formularios
│   ├── views.py             # Vistas y endpoints de exportación/reordenamiento
│   ├── services/            # Exportadores y utilidades
│   ├── templates/           # UI HTML/Bootstrap/HTMX
│   └── latex_templates/     # Plantillas Jinja2 para LaTeX
├── media/                   # Capturas locales, ignorado por Git
├── exports/                 # Reportes generados, ignorado por Git
└── db.sqlite3               # Base de datos local, ignorada por Git
```

## Carpetas y Datos Locales

La herramienta está diseñada para que los datos sensibles no salgan del equipo:

- `media/`: imágenes y capturas subidas.
- `exports/`: fuentes LaTeX, assets copiados y PDF generado.
- `db.sqlite3`: máquinas, evidencias, vulnerabilidades, exploits y flags.

Estas rutas deben permanecer fuera del control de versiones. El `.gitignore` ya las excluye.

## Exportación en Detalle

### LaTeX

Genera:

```text
exports/<nombre-maquina>/main.tex
exports/<nombre-maquina>/assets/screenshots/
```

### PDF

El botón de PDF:

1. Renderiza de nuevo el LaTeX con la información más reciente.
2. Ejecuta `latexmk`.
3. Devuelve el PDF como descarga del navegador si la compilación fue exitosa.

### Markdown ZIP

Genera y descarga un ZIP con:

```text
report.md
assets/screenshots/<imagenes>
```

Esto es útil para mover el reporte a repositorios privados, wikis internas o editores Markdown.

## Verificación Rápida

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python -m compileall reports ctf_report_forge
```

## Limitaciones Conocidas de la Beta

- No hay autenticación ni gestión multiusuario.
- No hay cifrado de la base de datos ni de las capturas.
- La app es local-first en datos, pero la UI todavía usa algunos assets por CDN en beta, como Bootstrap, HTMX, Highlight.js y fuentes externas.
- El drag-and-drop reordena dentro de listas concretas; no mueve evidencias entre fases.
- La compilación PDF depende de `latexmk` y de que el contenido generado sea válido para LaTeX.
- No reemplaza un sistema formal de reporting empresarial con control de acceso, auditoría y aprobaciones.

## Roadmap

- Empaquetar assets frontend localmente para modo offline real.
- Mejorar edición y reordenamiento de capturas.
- Importación automática desde carpeta de screenshots.
- Parsers para Nmap, Gobuster, Feroxbuster y herramientas comunes.
- Más plantillas de reporte.
- Opciones avanzadas de censura de secretos.
- Docker local opcional.
- Pruebas automatizadas de UI.

## Seguridad y Uso Responsable

Usa CTF Report Forge solo con sistemas propios, laboratorios, CTFs o entornos donde tengas permiso explícito. La herramienta ayuda a documentar trabajo técnico; no autoriza ni justifica actividad fuera de alcance.
