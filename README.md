<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>Manage your Bear Blog with an agent or a small Python CLI.</b></p>
  <p><b>English</b> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

An Agent Skill for **Codex, Claude Code and compatible tools**, backed by a standalone Python client for the [Bear Blog API](https://docs.bearblog.dev/api/).

- Create, edit, publish, schedule and delete posts or pages.
- Update the homepage, navigation, CSS and supported blog settings.
- List drafts and scheduled posts, fetch full bodies and export API-readable content.

## Requirements

Python 3.9+, an upgraded Bear Blog, and an API key from **dashboard → Settings → API**. Use the original Bear subdomain, including when the blog has a custom domain. Runtime scripts use only the Python standard library; macOS and Linux are supported.

## Install

With [Skills CLI](https://github.com/vercel-labs/skills), using Node.js/npm and Git:

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

Keep only the agent you use after `-a`; omit `-g` for a project install. Open a new conversation after installation.

<details>
<summary>Manual installation</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

Clone this repository and copy the complete `skills/bearblog` directory to the appropriate location. Preserve any existing customizations before replacing an installed copy.

| Agent | User skill directory |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## Configure

In a terminal, set `SKILL_DIR` to the installed directory. For a default global Codex installation:

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

For Claude Code, use `~/.claude/skills/bearblog`; for a repository clone, use `./skills/bearblog`. The setup command prompts for the subdomain and a hidden API key, then saves `~/.config/bearblog/config.json` with POSIX mode `0600`. `get-blog` verifies access without changing the blog.

For automation, supply **both** `BEARBLOG_API_KEY` and `BEARBLOG_SUBDOMAIN` through the environment. They take precedence over the configuration file. A global `--config PATH` selects another file. Keep keys out of prompts, shell history and repositories.

## Use

In Codex:

```text
$bearblog List all drafts and scheduled posts.
$bearblog Create a draft from ./article.md and tag it notes.
$bearblog Publish the draft titled "Hello" on December 1, 2027 at 09:00 Europe/Paris.
```

In Claude Code, replace `$bearblog` with `/bearblog`. Tell the agent the target content, intended changes and timezone when scheduling. Search and bulk edits are agent workflows built from sequential API calls.

## Components

| Component | Purpose |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | Agent instructions and operation routing |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | Dependency-free API client and CLI |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | Offline tests using a local HTTP server |
| [references/api.md](skills/bearblog/references/api.md) | Endpoints, fields, pagination and limits |
| [references/workflows.md](skills/bearblog/references/workflows.md) | Publishing, bulk editing, export and recovery examples |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codex display metadata |

## Standalone CLI

Use the same client without an agent. Run commands with the `SKILL_DIR` configured above.

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| Command | Action |
| --- | --- |
| `list-posts --all` | List posts; supports `--status`, `--is-page`, `--page` and `--all` |
| `get-post UID` | Read one post including its body |
| `create-post --data draft.json` | Create a draft by default |
| `update-post UID --data patch.json` | Edit, publish or schedule a post |
| `delete-post UID` | Permanently delete a post or page |
| `get-blog` | Read blog settings |
| `update-blog --data settings.json` | Update only supplied settings |
| `export --output export.json` | Export settings and all posts with full bodies |

Example `draft.json`:

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

For updates, pass only the fields to change. `--data -` reads JSON from stdin. For example, `{"publish":true}` publishes and `{"publish":false}` returns a post to draft. Scheduling requires `publish:true` plus a future, timezone-aware `published_date`. See the [API reference](skills/bearblog/references/api.md) for all writable fields.

## Behavior and limits

- Covers all seven documented API endpoints. New posts default to drafts; use stable `uid` values for edits and deletion.
- Lists contain 20 items per page and omit bodies. Export fetches individual details; it omits media files and is not a consistent snapshot or a one-command restore. Existing export files are never overwritten.
- The service allows 60 requests per minute. Each client instance spaces requests and retries 429 at most twice, respecting `Retry-After` within a 60-second total wait budget. Coordinate rates across processes.
- Writes are not automatically retried after network failures or 5xx responses. Read back before retrying. Requests use the official API host; redirects are rejected.
- The documented API has no media-upload, analytics or subscriber endpoints. Local configuration is plaintext protected by file permissions. JSON exports can contain private drafts.

## Development

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

Tests require no API key and do not access real blogs. CLI help and error messages are in English. Translation contributions and bug reports are welcome.

## License

[MIT](LICENSE). This is an independent project, unaffiliated with Bear Blog.
