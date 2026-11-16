#!/usr/bin/env python3
"""Offline behavior checks. No external requests or real credentials."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

import bearblog as b

KEY = 'offline-test-secret-please-redact'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle_request(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length) if length else b''
        self.server.calls.append({'method': self.command, 'path': self.path,
                                  'auth': self.headers.get('Authorization'),
                                  'content_type': self.headers.get('Content-Type'),
                                  'body': json.loads(raw) if raw else None})
        if self.server.responses:
            status, headers, body = self.server.responses.pop(0)
        else:
            status, headers, body = 500, {}, {'error': 'unexpected call'}
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if body is not None:
            self.wfile.write(body if isinstance(body, bytes) else json.dumps(body).encode())

    do_GET = do_POST = do_PATCH = do_DELETE = handle_request


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.calls, self.server.responses = [], []
        self.client = b.Client('demo', KEY)
        # The production CLI deliberately exposes no arbitrary base-URL override.
        self.client.base = 'http://127.0.0.1:%d/demo/api/v1/' % self.server.server_port
        self.sleep = mock.patch.object(b.time, 'sleep').start()
        self.addCleanup(mock.patch.stopall)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def response(self, body, status=200, headers=None):
        self.server.responses.append((status, headers or {}, body))

    def args(self, *values):
        return b.parser().parse_args(list(values))

    def run_cli(self, *values):
        with mock.patch.object(b, 'credentials', return_value=('demo', KEY)), \
                mock.patch.object(b, 'Client', return_value=self.client):
            return b.execute(self.args(*values))

    def data(self, value):
        path = self.root / 'data.json'
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        return str(path)

    def test_all_seven_routes_and_partial_patch(self):
        commands = [
            (('list-posts',), 'GET', 'post/?page=1', {'posts': [], 'next_page': None}, None),
            (('create-post', '--data', self.data({'title': '你好', 'content': '**正文**'})), 'POST', 'post/', {'uid': 'x'}, {'title': '你好', 'content': '**正文**'}),
            (('get-post', 'x'), 'GET', 'post/x/', {'uid': 'x', 'content': 'body'}, None),
            # Each payload is written immediately before running to share one file safely.
            (('update-post', 'x', '--data', 'PATCHFILE'), 'PATCH', 'post/x/', {'uid': 'x'}, {'publish': True}),
            (('delete-post', 'x'), 'DELETE', 'post/x/', None, None),
            (('get-blog',), 'GET', 'blog/', {'title': 'Demo'}, None),
            (('update-blog', '--data', 'PATCHFILE'), 'PATCH', 'blog/', {'nav': 'new'}, {'nav': 'new'}),
        ]
        for command, method, path, response, expected in commands:
            with self.subTest(command=command[0]):
                if 'PATCHFILE' in command:
                    command = tuple(self.data(expected) if x == 'PATCHFILE' else x for x in command)
                self.response(response, 204 if method == 'DELETE' else 200)
                result = self.run_cli(*command)
                self.assertEqual(result, response)
                call = self.server.calls[-1]
                self.assertEqual(call['method'], method)
                self.assertEqual(call['path'], '/demo/api/v1/' + path)
                self.assertEqual(call['auth'], 'Bearer ' + KEY)
                self.assertEqual(call['body'], expected)
                if expected is not None:
                    self.assertEqual(call['content_type'], 'application/json')

    def test_all_writable_fields_pass_through(self):
        post = {'title': '标题', 'content': '**正文**', 'slug': 'a-page', 'publish': True,
                'published_date': '2026-12-01T09:00:00+08:00', 'tags': ['中文'],
                'is_page': True, 'discoverable': False, 'alias': ['raw-option'],
                'canonical_url': 'https://example.com/a/', 'meta_description': '描述',
                'meta_image': 'https://example.com/image.png', 'class_name': 'article', 'lang': 'zh'}
        self.assertEqual(b.payload(self.data(post), 'post', True), post)
        blog = {'title': 'Blog', 'content': '# Home', 'favicon': '/icon.png',
                'meta_description': '', 'meta_image': '/image.png', 'nav': '[首页](/)',
                'custom_styles': 'body{}', 'robots_txt': 'User-agent: *', 'date_format': 'd M, Y'}
        self.assertEqual(b.payload(self.data(blog), 'blog'), blog)

    def test_interactive_configuration_saves_private_file_without_key_in_result(self):
        config = self.root / 'nested' / 'config.json'
        with mock.patch.object(b.sys.stdin, 'isatty', return_value=True), \
                mock.patch('builtins.input', return_value='Demo'), \
                mock.patch.object(b.getpass, 'getpass', return_value=KEY):
            result = b.configure(config)
        self.assertNotIn(KEY, json.dumps(result))
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(config.read_text()), {'subdomain': 'demo', 'api_key': KEY})

    def test_cli_reports_json_failure_without_traceback(self):
        stderr = io.StringIO()
        with mock.patch.object(b.sys, 'argv', ['bearblog.py', 'get-blog']), \
                mock.patch.object(b, 'execute', side_effect=b.Failure('missing credentials')), \
                contextlib.redirect_stderr(stderr):
            self.assertEqual(b.main(), 1)
        self.assertEqual(json.loads(stderr.getvalue()), {'error': 'missing credentials'})

    def test_pagination_preserves_filters_and_gets_all_pages(self):
        self.response({'posts': [{'uid': 'a'}], 'count': 2, 'next_page': 2})
        self.response({'posts': [{'uid': 'b'}], 'count': 2, 'next_page': None})
        result = self.run_cli('list-posts', '--all', '--status', 'draft', '--is-page', 'false')
        self.assertEqual([p['uid'] for p in result['posts']], ['a', 'b'])
        self.assertEqual(result['fetched_count'], 2)
        self.assertEqual(self.server.calls[1]['path'], '/demo/api/v1/post/?page=2&status=draft&is_page=false')
        self.assertTrue(any(call.args[0] > 0 for call in self.sleep.call_args_list))

    def test_bad_pagination_stops(self):
        self.response({'posts': [], 'next_page': 1})
        with self.assertRaises(b.Failure):
            self.run_cli('list-posts', '--all')
        self.assertEqual(len(self.server.calls), 1)

    def test_bad_payloads_rejected_before_network(self):
        for data in ({'publish': 'true'}, {'published_date': '2026-12-01T09:00:00'},
                     {'published_date': None}, {'tags': 'tag'}, {'title': 'x' * 201},
                     {'uid': 'readonly'}, {}):
            with self.subTest(data=data), self.assertRaises(b.Failure):
                self.run_cli('update-post', 'x', '--data', self.data(data))
        with self.assertRaises(b.Failure):
            self.run_cli('create-post', '--data', self.data({'content': 'no title'}))
        with self.assertRaises(b.Failure):
            self.run_cli('list-posts', '--page', '0')
        self.assertEqual(self.server.calls, [])

    def test_nonfinite_json_and_path_injection_rejected(self):
        path = self.root / 'bad.json'
        path.write_text('{"alias":NaN}')
        with self.assertRaises(b.Failure):
            b.payload(str(path), 'post')
        for domain in ('https://evil.test', 'a/b', '../x', 'demo.bearblog.dev', ''):
            with self.subTest(domain=domain), self.assertRaises(b.Failure):
                b.Client(domain, KEY)
        for uid in ('../blog', 'https://evil.test', 'x?key=y'):
            with self.subTest(uid=uid), self.assertRaises(b.Failure):
                self.run_cli('get-post', uid)

    def test_stdin_json(self):
        with mock.patch.object(b.sys, 'stdin', io.StringIO('{"publish":false}')):
            self.assertEqual(b.payload('-', 'post'), {'publish': False})

    def test_429_retry_after_is_honored_and_bounded(self):
        self.response({'error': 'slow'}, 429, {'Retry-After': '3'})
        self.response({'title': 'ok'})
        self.assertEqual(self.client.request('GET', 'blog/'), {'title': 'ok'})
        self.sleep.assert_any_call(3.0)
        for _ in range(3):
            self.response({'error': 'slow'}, 429, {'Retry-After': '0'})
        with self.assertRaises(b.Failure) as caught:
            self.client.request('GET', 'blog/')
        self.assertEqual(caught.exception.details['status'], 429)
        self.assertEqual(len(self.server.calls), 5)

    def test_long_or_invalid_retry_after_returns_without_waiting(self):
        for delay in ('61', 'NaN', '-1', 'bad'):
            self.response({}, 429, {'Retry-After': delay})
            with self.subTest(delay=delay), self.assertRaises(b.Failure):
                self.client.request('GET', 'blog/')
        self.assertFalse(any(c.args[0] > 60 for c in self.sleep.call_args_list))

    def test_errors_do_not_replay_writes_or_leak_key(self):
        for status in (400, 401, 403, 404, 500):
            self.response({'error': 'secret=' + KEY}, status)
            with self.subTest(status=status), self.assertRaises(b.Failure) as caught:
                self.client.request('POST', 'post/', data={'title': 'x'})
            self.assertNotIn(KEY, json.dumps(caught.exception.details))
            self.assertEqual(caught.exception.details['result_unknown'], status >= 500)
        self.assertEqual(len(self.server.calls), 5)

    def test_redirect_refused_without_following(self):
        self.response(None, 302, {'Location': self.client.base + 'blog/'})
        with self.assertRaises(b.Failure) as caught:
            self.client.request('GET', 'blog/')
        self.assertEqual(caught.exception.details['status'], 302)
        self.assertEqual(len(self.server.calls), 1)

    def test_invalid_success_response_is_uncertain_for_write(self):
        self.response(b'<html>not JSON</html>')
        with self.assertRaises(b.Failure) as caught:
            self.client.request('POST', 'post/', data={'title': 'x'})
        self.assertTrue(caught.exception.details['result_unknown'])
        self.assertEqual(len(self.server.calls), 1)

    def test_network_failure_not_retried(self):
        with mock.patch.object(self.client.opener, 'open', side_effect=TimeoutError()) as opened:
            with self.assertRaises(b.Failure) as caught:
                self.client.request('PATCH', 'blog/', data={'title': 'x'})
        self.assertEqual(opened.call_count, 1)
        self.assertTrue(caught.exception.details['result_unknown'])

    def test_private_credentials_and_environment_pairing(self):
        config = self.root / 'config.json'
        b.private_json(config, {'subdomain': 'demo', 'api_key': KEY})
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(b.credentials(config), ('demo', KEY))
        with mock.patch.dict(os.environ, {'BEARBLOG_API_KEY': KEY}, clear=True):
            with self.assertRaises(b.Failure):
                b.credentials(config)
        with mock.patch.dict(os.environ, {'BEARBLOG_API_KEY': KEY, 'BEARBLOG_SUBDOMAIN': 'other'}, clear=True):
            self.assertEqual(b.credentials(config), ('other', KEY))
        with self.assertRaises(b.Failure):
            b.private_json(config, {'bad': True})
        self.assertEqual(json.loads(config.read_text())['api_key'], KEY)

    def test_export_gets_full_content_and_refuses_overwrite(self):
        output = self.root / 'export.json'
        self.response({'title': 'Blog', 'custom_styles': 'body{}'})
        self.response({'posts': [{'uid': 'a'}, {'uid': 'b'}], 'next_page': None})
        self.response({'uid': 'a', 'content': 'Full A'})
        self.response({'uid': 'b', 'content': 'Full B'})
        self.assertEqual(self.run_cli('export', '--output', str(output))['exported'], 2)
        data = json.loads(output.read_text())
        self.assertEqual([p['content'] for p in data['posts']], ['Full A', 'Full B'])
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(b.Failure):
            self.run_cli('export', '--output', str(output))
        self.assertEqual(len(self.server.calls), 4)

    def test_failed_export_leaves_no_completion_file(self):
        output = self.root / 'export.json'
        self.response({'title': 'Blog'})
        self.response({'posts': [{'uid': 'a'}], 'next_page': None})
        self.response({'error': 'deleted'}, 404)
        with self.assertRaises(b.Failure):
            self.run_cli('export', '--output', str(output))
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
