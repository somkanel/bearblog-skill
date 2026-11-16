<div align="center">
  <h1>🍯 Bear Blog Skill</h1>
  <p><b>Gestiona Bear Blog con un agente o una pequeña CLI de Python.</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <b>Español</b> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://docs.bearblog.dev/api/"><img src="https://img.shields.io/badge/API-official-green" alt="Official Bear Blog API"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

Un Agent Skill para **Codex, Claude Code y herramientas compatibles**, con un cliente Python independiente para la [API de Bear Blog](https://docs.bearblog.dev/api/).

Este proyecto utiliza únicamente la [API pública oficial de Bear Blog](https://docs.bearblog.dev/api/). No usa protocolos privados, endpoints no documentados ni funciones no oficiales de la plataforma. Las búsquedas y ediciones por lotes combinan llamadas documentadas.

- Crea, edita, publica, programa y elimina entradas o páginas.
- Actualiza la página de inicio, la navegación, el CSS y los ajustes admitidos.
- Consulta borradores y publicaciones programadas, obtén el texto completo y exporta los datos accesibles por la API.

## Requisitos

Se requieren Python 3.9+ y un **plan de pago de Bear Blog**. **Solo los blogs de pago pueden generar claves de API**, en **panel → Settings → API**. Usa el subdominio original de Bear, incluso con un dominio propio. Los scripts solo requieren la biblioteca estándar de Python; son compatibles con macOS y Linux.

## Instalación

Con [Skills CLI](https://github.com/vercel-labs/skills), usando Node.js/npm y Git:

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

Deja solo el agente que uses después de `-a`; omite `-g` para instalar en el proyecto. Abre una conversación nueva tras la instalación.

<details>
<summary>Instalación manual</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

Clona el repositorio y copia el directorio completo `skills/bearblog` en la ubicación correspondiente. Conserva tus personalizaciones antes de sustituir una instalación existente.

| Agente | Directorio de habilidades del usuario |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## Configuración

En una terminal, asigna a `SKILL_DIR` el directorio instalado. Para una instalación global predeterminada de Codex:

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Para Claude Code usa `~/.claude/skills/bearblog`; en un clon del repositorio usa `./skills/bearblog`. El comando solicita el subdominio y una clave con entrada oculta, y guarda `~/.config/bearblog/config.json` con permisos POSIX `0600`. `get-blog` comprueba el acceso sin modificar el blog.

Para automatizar, proporciona **ambas** variables `BEARBLOG_API_KEY` y `BEARBLOG_SUBDOMAIN` en el entorno. Tienen prioridad sobre el archivo de configuración. La opción global `--config PATH` selecciona otro archivo. No incluyas claves en instrucciones al agente, el historial del shell ni el repositorio.

## Uso

En Codex:

```text
$bearblog Lista todos los borradores y las entradas programadas.
$bearblog Crea un borrador a partir de ./article.md y añade la etiqueta notes.
$bearblog Programa el borrador titulado Hello para el 1 de diciembre de 2027 a las 09:00 Europe/Paris.
```

En Claude Code sustituye `$bearblog` por `/bearblog`. Indica el contenido, los cambios y la zona horaria al programar. El agente realiza las búsquedas y las ediciones por lotes mediante llamadas secuenciales a la API.

## Componentes

| Componente | Función |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | Instrucciones para el agente y selección de operaciones |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | Cliente de API y CLI sin dependencias externas |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | Pruebas sin conexión con un servidor HTTP local |
| [references/api.md](skills/bearblog/references/api.md) | Endpoints, campos, paginación y límites |
| [references/workflows.md](skills/bearblog/references/workflows.md) | Ejemplos de publicación, edición por lotes, exportación y recuperación |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Metadatos de presentación de Codex |

## CLI independiente

El mismo cliente funciona sin agente. Usa el `SKILL_DIR` configurado anteriormente.

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| Comando | Acción |
| --- | --- |
| `list-posts --all` | Lista entradas; admite `--status`, `--is-page`, `--page` y `--all` |
| `get-post UID` | Obtiene una entrada con su texto completo |
| `create-post --data draft.json` | Crea una entrada como borrador por defecto |
| `update-post UID --data patch.json` | Edita, publica o programa una entrada |
| `delete-post UID` | Elimina permanentemente una entrada o página |
| `get-blog` | Lee los ajustes del blog |
| `update-blog --data settings.json` | Actualiza solo los ajustes proporcionados |
| `export --output export.json` | Exporta los ajustes y todas las entradas completas |

Ejemplo de `draft.json`:

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

Al actualizar, envía solo los campos que quieras cambiar. `--data -` lee JSON desde la entrada estándar. `{"publish":true}` publica y `{"publish":false}` devuelve una entrada a borrador. Para programar se necesitan `publish:true` y un `published_date` futuro con zona horaria. Consulta todos los campos en la [referencia de la API](skills/bearblog/references/api.md).

## Comportamiento y límites

- Cubre los siete endpoints documentados. Las entradas nuevas son borradores por defecto; las ediciones y eliminaciones usan el `uid` estable.
- Las listas contienen 20 elementos por página sin texto completo. La exportación consulta cada entrada, omite los archivos multimedia y no es una instantánea consistente ni una restauración con un solo comando. No sobrescribe archivos existentes.
- El servicio permite 60 solicitudes por minuto. Cada cliente espacia las solicitudes y reintenta 429 como máximo dos veces, respetando `Retry-After` con un máximo de 60 segundos de espera total. Coordina la tasa entre procesos.
- Las escrituras no se reintentan automáticamente tras fallos de red o respuestas 5xx. Lee el resultado antes de repetir. Solo se usa el host oficial de la API y se rechazan las redirecciones.
- La API documentada no ofrece endpoints de subida de archivos multimedia, analítica ni suscriptores. La configuración local se guarda en texto plano protegido por permisos. Las exportaciones JSON pueden contener borradores privados.

## Desarrollo

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

Las pruebas no necesitan clave ni acceden a blogs reales. La ayuda y los errores de la CLI están en inglés. Se agradecen las mejoras de traducción y los informes de errores.

## Licencia

[MIT](LICENSE). Proyecto independiente, sin afiliación con Bear Blog.
