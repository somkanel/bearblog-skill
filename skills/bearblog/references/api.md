# Bear Blog API reference

Source: [official API documentation](https://docs.bearblog.dev/api/).

## Protocol and endpoints

Base URL: `https://bearblog.dev/{subdomain}/api/v1/`. Use the Bear subdomain even with a custom domain. Send `Authorization: Bearer API_KEY` on every request; POST and PATCH use JSON with `Content-Type: application/json`. Keep trailing slashes. Each key belongs to one upgraded blog; key generation and revocation are dashboard operations.

| HTTP | Relative path | CLI command |
| --- | --- | --- |
| GET | `post/` | `list-posts` |
| POST | `post/` | `create-post` |
| GET | `post/{uid}/` | `get-post UID` |
| PATCH | `post/{uid}/` | `update-post UID` |
| DELETE | `post/{uid}/` | `delete-post UID` |
| GET | `blog/` | `get-blog` |
| PATCH | `blog/` | `update-blog` |

PATCH changes only supplied fields. DELETE is permanent.

## Post fields

| Writable field | Documented behavior |
| --- | --- |
| `title` | Required on creation, at most 200 characters |
| `content` | Markdown, HTML or LaTeX |
| `slug` | Generated from title when omitted; normalized and deduplicated by the server |
| `publish` | Boolean; new posts are drafts by default |
| `published_date` | Datetime with timezone, e.g. `2026-12-01T09:00:00+08:00` |
| `tags` | Array of strings |
| `is_page` | Boolean; distinguishes pages from posts |
| `discoverable` | Boolean, false by default; opts into the discovery feed |
| `alias`, `canonical_url`, `meta_description`, `meta_image`, `class_name`, `lang` | Same as the editor's header options |

The last six fields have no detailed type, format or nullability specification in the API page. The client passes their JSON values through for server validation. An image-related field does not imply a file-upload endpoint.

Responses also include read-only `uid`, `url` and `last_modified`. uid remains stable when slug changes. Dates return in UTC. Use the actual slug and URL returned by the server.

`publish:false` makes a draft. `publish:true` publishes; a future published_date on a published post schedules it. A draft without a date receives one when published. Clearing a date with null is undocumented and is not treated as an established capability.

## Listing

Query parameters: `page` starts at 1; `status` accepts draft, published or scheduled; `is_page` accepts true or false. Omit status to include all statuses, or is_page to include posts and pages.

Lists have 20 records per page, newest first, without content. Responses contain posts, count, page, page_size and next_page. The final next_page is null. `--all` merges pages starting at the requested page and preserves filters. Changes to a blog during pagination can change results.

## Blog fields

Writable: `title`, `content`, `favicon`, `meta_description`, `meta_image`, `nav`, `custom_styles`, `robots_txt`, `date_format`.

content supports Markdown, HTML and LaTeX; nav is Markdown; custom_styles is CSS; a date_format example is `d M, Y`. Unspecified formats are left to server validation. Responses also include read-only last_modified.

## Errors and limits

Errors look like `{"error":"title is required"}`. The documentation states that nothing is saved on an error.

| HTTP | Meaning |
| --- | --- |
| 400 | Invalid request; use the message to correct it |
| 401 | Missing or invalid key |
| 403 | Blog is not upgraded |
| 404 | Post or path does not exist |
| 429 | Limit of 60 requests per minute; Retry-After gives seconds to wait |

The API documents no search, bulk-write, media-upload, subscriber, analytics, comment, custom-domain-management or webhook endpoints. It also provides no complete success-status list, response examples, concurrency controls, idempotency keys or field-clearing specification. Verify unspecified behavior using reads or a minimal authorized write.
