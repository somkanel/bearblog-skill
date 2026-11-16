# Workflows

Replace `SKILL_DIR` with the installed skill directory. Python 3.9+ is the only runtime dependency.

## Configure and connect

Run in an interactive terminal:

```bash
python3 SKILL_DIR/scripts/bearblog.py configure
python3 SKILL_DIR/scripts/bearblog.py get-blog
```

configure asks for a subdomain and a hidden key. For noninteractive use, supply both BEARBLOG_API_KEY and BEARBLOG_SUBDOMAIN in the environment. The default `~/.config/bearblog/config.json` contains subdomain and api_key; global `--config /absolute/path/config.json` selects another file. Environment variables take precedence. Keep credentials out of skill distributions.

## Draft, publish and schedule

Use file tools to create a UTF-8 JSON payload, for example:

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

```bash
python3 SKILL_DIR/scripts/bearblog.py create-post --data /absolute/path/draft.json
```

Use the returned uid. Publish with `{"publish":true}`, return to draft with `{"publish":false}`, or schedule with `{"publish":true,"published_date":"2026-12-01T09:00:00+08:00"}`. Replace the example date with the user's intended future time and timezone.

```bash
python3 SKILL_DIR/scripts/bearblog.py get-post UID
python3 SKILL_DIR/scripts/bearblog.py update-post UID --data /absolute/path/patch.json
```

Add is_page:true to create a page. PATCH only is_page to convert an existing post. Publishing a page still requires publish:true.

## Homepage, navigation and CSS

Read get-blog, then submit only the intended fields. Example:

```json
{"nav":"[Home](/) [About](/about/)","custom_styles":"body { max-width: 720px; }"}
```

```bash
python3 SKILL_DIR/scripts/bearblog.py update-blog --data /absolute/path/blog-patch.json
```

custom_styles replaces the entire field. Merge existing CSS before making additions or partial edits. tags also replaces the entire array; merge and deduplicate when appending tags.

## Search and bulk edits

Use list-posts --all with status and is-page filters, then filter titles or tags locally. Fetch each detail for body searches. Resolve uids and the authorized scope, save original full records to a private file, then PATCH sequentially. Stop at the first failure and report successful uids, the failed item and remaining count. There is no transaction. Restoring originals is a new write that must remain within the user's authorization.

Avoid concurrent processes. Rate limiting is per client instance; callers must coordinate aggregate request rates across processes.

## Export

```bash
python3 SKILL_DIR/scripts/bearblog.py export --output /absolute/path/bearblog-export.json
```

Output contains exported_at, subdomain, blog and posts, with full details for each post. The parent directory must exist. The file refuses overwrites and uses POSIX mode 0600. A failed export leaves no completed output. Media binaries are omitted; reads do not form a consistent snapshot.

There is no one-command restore. Select writable fields before recreating posts, omit read-only fields, and perform each creation within the authorized scope. The server may adjust slugs; original uids cannot be restored.

## Recovery

429 receives at most two retries. A single automatic wait and the total automatic wait are each limited to 60 seconds. On exceeding the budget, the error reports retry_after_seconds; wait that long before continuing.

Timeouts, disconnects, 5xx and malformed success responses are not automatically retried. A write may have succeeded. Read the post or blog before retrying; after POST, inspect recent posts and details. Report uncertainty if the result cannot be determined.
