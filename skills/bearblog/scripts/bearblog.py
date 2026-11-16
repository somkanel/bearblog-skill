#!/usr/bin/env python3
"""Bear Blog API CLI. Python 3.9+, standard library only."""
import argparse
import datetime as dt
import getpass
import http.client
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

POST_FIELDS = set('title content slug publish published_date tags is_page discoverable alias canonical_url meta_description meta_image class_name lang'.split())
BLOG_FIELDS = set('title content favicon meta_description meta_image nav custom_styles robots_txt date_format'.split())
CONFIG = Path.home() / '.config/bearblog/config.json'


class Failure(Exception):
    def __init__(self, message, **details):
        super().__init__(message)
        self.details = {'error': message, **details}


def clean(value, key):
    if isinstance(value, str):
        return value.replace(key, '[REDACTED]') if key else value
    if isinstance(value, list):
        return [clean(v, key) for v in value]
    if isinstance(value, dict):
        return {clean(k, key): clean(v, key) for k, v in value.items()}
    return value


def subdomain(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', value):
        raise Failure('Use the Bear subdomain label, not a URL or custom domain')
    return value.lower()


def api_key(value):
    if not isinstance(value, str) or not value.strip() or any(c.isspace() or ord(c) < 32 or ord(c) > 126 for c in value):
        raise Failure('API key must be nonempty printable ASCII without whitespace')
    return value


def credentials(path):
    key, domain = os.environ.get('BEARBLOG_API_KEY'), os.environ.get('BEARBLOG_SUBDOMAIN')
    if key is not None or domain is not None:
        if not key or not domain:
            raise Failure('Set both BEARBLOG_API_KEY and BEARBLOG_SUBDOMAIN together')
        return subdomain(domain), api_key(key)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError()
        return subdomain(data.get('subdomain')), api_key(data.get('api_key'))
    except FileNotFoundError:
        raise Failure('No credentials: run configure or set both BEARBLOG environment variables') from None
    except (ValueError, OSError):
        raise Failure('Cannot read configuration or configuration is not a valid JSON object') from None


def private_json(path, value, replace=False):
    """Write completely, then atomically publish with private permissions."""
    name = None
    try:
        fd, name = tempfile.mkstemp(prefix='.bearblog-', dir=path.parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(name, path)
        else:
            os.link(name, path)  # Atomic no-overwrite, unlike exists() + rename().
    except FileExistsError:
        raise Failure('Output file already exists; refusing to overwrite') from None
    except OSError:
        raise Failure('Cannot write file; check the directory and permissions') from None
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def configure(path):
    if not sys.stdin.isatty():
        raise Failure('configure requires an interactive terminal; use environment variables for noninteractive use')
    domain = subdomain(input('Bear subdomain: ').strip())
    key = api_key(getpass.getpass('API key (hidden input): ').strip())
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_json(path, {'subdomain': domain, 'api_key': key}, replace=True)
    return {'configured': True, 'subdomain': domain, 'config_path': str(path)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, domain, key):
        self.domain, self.key = subdomain(domain), api_key(key)
        self.base = 'https://bearblog.dev/' + self.domain + '/api/v1/'
        self.opener = urllib.request.build_opener(NoRedirect())
        self.last_request = None

    def request(self, method, path, query=None, data=None):
        # Only internal resource routes are accepted; never accept an arbitrary URL.
        if not re.fullmatch(r'(?:blog/|post/(?:[A-Za-z0-9_-]+/)?)', path):
            raise Failure('Invalid API path or UID')
        url = self.base + path
        if query:
            url += '?' + urllib.parse.urlencode(query)
        headers = {'Authorization': 'Bearer ' + self.key, 'Accept': 'application/json'}
        body = None
        if data is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
        waited = 0.0
        for attempt in range(3):
            if self.last_request is not None:
                time.sleep(max(0, 1.05 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with self.opener.open(req, timeout=30) as response:
                    raw = response.read()
                if not raw.strip():
                    return None
                try:
                    return clean(json.loads(raw), self.key)
                except (ValueError, UnicodeError):
                    raise Failure('Success response is not valid JSON; a write may have succeeded, so read back before retrying', result_unknown=method != 'GET') from None
            except urllib.error.HTTPError as exc:
                status = exc.code
                retry = exc.headers.get('Retry-After')
                try:
                    error_body = clean(json.loads(exc.read()), self.key)
                except (ValueError, UnicodeError):
                    error_body = None  # Never echo HTML, headers or raw network errors.
                finally:
                    exc.close()
                if status == 429:
                    try:
                        seconds = float(retry)
                        if not math.isfinite(seconds) or seconds < 0:
                            raise ValueError()
                    except (TypeError, ValueError):
                        raise Failure('429: missing or invalid Retry-After; try again later', status=429) from None
                    if attempt < 2 and seconds <= 60 and waited + seconds <= 60:
                        time.sleep(seconds)
                        waited += seconds
                        continue
                    raise Failure('429: automatic retry or wait limit reached', status=429, retry_after_seconds=seconds) from None
                messages = {400: 'Invalid request parameters', 401: 'Missing or invalid API key', 403: 'Blog is not upgraded', 404: 'Post or path does not exist'}
                raise Failure(messages.get(status, 'HTTP request failed; not retried automatically'), status=status,
                              server_error=error_body, result_unknown=method != 'GET' and status >= 500) from None
            except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
                raise Failure('Network request failed; not retried automatically. Verify whether a write took effect', result_unknown=method != 'GET') from None

    def listing(self, page=1, status=None, is_page=None, all_pages=False):
        query = {'page': page}
        if status is not None:
            query['status'] = status
        if is_page is not None:
            query['is_page'] = is_page
        posts, seen = [], set()
        while True:
            if query['page'] in seen:
                raise Failure('Pagination loop detected; stopped')
            seen.add(query['page'])
            result = self.request('GET', 'post/', query=query)
            if not isinstance(result, dict) or not isinstance(result.get('posts'), list) or 'next_page' not in result:
                raise Failure('List response does not match the documented structure')
            if not all_pages:
                return result
            posts.extend(result['posts'])
            following = result['next_page']
            if following is None:
                return {'posts': posts, 'count': result.get('count'), 'fetched_count': len(posts),
                        'start_page': page, 'next_page': None}
            if type(following) is not int or following <= query['page']:
                raise Failure('Invalid next_page; stopped')
            query['page'] = following


def payload(path, target, create=False):
    try:
        raw = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
        data = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError()))
    except (OSError, ValueError, UnicodeError):
        raise Failure('Data must be a readable UTF-8 JSON object') from None
    if not isinstance(data, dict) or not data:
        raise Failure('Data must be a nonempty JSON object')
    allowed = POST_FIELDS if target == 'post' else BLOG_FIELDS
    if set(data) - allowed:
        raise Failure('Unknown or read-only fields', fields=sorted(set(data) - allowed))
    if create and not data.get('title'):
        raise Failure('Creating a post requires title')
    if target == 'post':
        if 'title' in data and (not isinstance(data['title'], str) or len(data['title']) > 200):
            raise Failure('title must be a string of at most 200 characters')
        for field in ('publish', 'is_page', 'discoverable'):
            if field in data and type(data[field]) is not bool:
                raise Failure(field + ' must be a JSON boolean')
        for field in ('content', 'slug'):
            if field in data and not isinstance(data[field], str):
                raise Failure(field + ' must be a string')
        if 'tags' in data and (not isinstance(data['tags'], list) or any(not isinstance(t, str) for t in data['tags'])):
            raise Failure('tags must be an array of strings')
        if 'published_date' in data:
            try:
                value = data['published_date']
                if not isinstance(value, str) or 'T' not in value:
                    raise ValueError()
                parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    raise ValueError()
            except (TypeError, ValueError):
                raise Failure('published_date must be an ISO 8601 datetime with a timezone') from None
    return data


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=CONFIG, help='Credential file; environment variables take precedence')
    commands = p.add_subparsers(dest='command', required=True)
    commands.add_parser('configure', help='Save subdomain and API key interactively (0600)')
    commands.add_parser('get-blog')
    listing = commands.add_parser('list-posts')
    listing.add_argument('--page', type=int, default=1)
    listing.add_argument('--status', choices=['draft', 'published', 'scheduled'])
    listing.add_argument('--is-page', choices=['true', 'false'])
    listing.add_argument('--all', action='store_true', dest='all_pages')
    for command in ('get-post', 'delete-post', 'update-post', 'create-post', 'update-blog'):
        sub = commands.add_parser(command)
        if command in ('get-post', 'delete-post', 'update-post'):
            sub.add_argument('uid')
        if command in ('create-post', 'update-post', 'update-blog'):
            sub.add_argument('--data', required=True, help='UTF-8 JSON object file, or - to read from stdin')
    export = commands.add_parser('export')
    export.add_argument('--output', required=True, type=Path)
    return p


def execute(args):
    if args.command == 'configure':
        return configure(args.config.expanduser())
    # Validate user input before making any network request.
    if getattr(args, 'page', 1) < 1:
        raise Failure('page must be >= 1')
    if hasattr(args, 'uid') and not re.fullmatch(r'[A-Za-z0-9_-]+', args.uid):
        raise Failure('Invalid UID')
    data = None
    if hasattr(args, 'data'):
        data = payload(args.data, 'blog' if args.command == 'update-blog' else 'post', args.command == 'create-post')
    if args.command == 'export':
        args.output = args.output.expanduser()
        if args.output.exists() or args.output.is_symlink():
            raise Failure('Output file already exists; refusing to overwrite')
        if not args.output.parent.is_dir():
            raise Failure('Output directory does not exist')
    domain, key = credentials(args.config.expanduser())
    client = Client(domain, key)
    if args.command == 'list-posts':
        return client.listing(args.page, args.status, args.is_page, args.all_pages)
    if args.command == 'export':
        blog = client.request('GET', 'blog/')
        if not isinstance(blog, dict):
            raise Failure('Blog response is not a JSON object')
        summaries = client.listing(all_pages=True)['posts']
        posts, seen = [], set()
        for summary in summaries:
            uid = summary.get('uid') if isinstance(summary, dict) else None
            if not isinstance(uid, str) or uid in seen:
                raise Failure('Export found a missing or duplicate uid; retry reading')
            seen.add(uid)
            post = client.request('GET', 'post/' + uid + '/')
            if not isinstance(post, dict) or post.get('uid') != uid or 'content' not in post:
                raise Failure('Post details missing uid or content; export not completed')
            posts.append(post)
        private_json(args.output, {'exported_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                                  'subdomain': domain, 'blog': blog, 'posts': posts})
        return {'exported': len(posts), 'output': str(args.output.resolve())}
    routes = {'get-blog': ('GET', 'blog/'), 'update-blog': ('PATCH', 'blog/'),
              'create-post': ('POST', 'post/')}
    if args.command in routes:
        method, path = routes[args.command]
    else:
        method = {'get-post': 'GET', 'update-post': 'PATCH', 'delete-post': 'DELETE'}[args.command]
        path = 'post/' + args.uid + '/'
    return client.request(method, path, data=data)


def main():
    args = parser().parse_args()
    try:
        result = execute(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except Failure as exc:
        print(json.dumps(exc.details, ensure_ascii=False), file=sys.stderr)
        return 1
    except (OSError, ValueError, UnicodeError):
        print(json.dumps({'error': 'Local operation failed; check files, configuration and input'}, ensure_ascii=False), file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print(json.dumps({'error': 'Interrupted; if a write was sent, verify the result before retrying'}, ensure_ascii=False), file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main())
