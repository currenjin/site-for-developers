"""Offline maintenance checks; every network boundary is injected."""
import importlib.util
import socket
import ssl
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('catalog_audit'), 'audit CLI is not implemented')
        import catalog_audit
        self.audit = catalog_audit
        self.calls = []

    def probe(self, url='https://example.org/start', replies=None, addresses=None, **kw):
        replies = iter(replies or [(200, {})])
        def transport(url, address, timeout):
            self.calls.append((url, address, timeout))
            response = next(replies)
            if isinstance(response, Exception):
                raise response
            return response
        return self.audit.probe_url(url, transport=transport,
            resolver=lambda host, port, timeout: addresses or ['93.184.216.34'], **kw)

    def test_success_is_reachability_not_quality(self):
        result = self.probe()
        self.assertEqual(result['outcome'], 'reachable')
        self.assertEqual(result['status'], 200)
        self.assertNotIn('quality', result)
        self.assertEqual(self.calls[0][1], '93.184.216.34')

    def test_follows_relative_redirect_and_records_final_url(self):
        result = self.probe(replies=[(301, {'location': '/end'}), (200, {})])
        self.assertEqual(result['final_url'], 'https://example.org/end')
        self.assertEqual(result['redirects'], ['https://example.org/end'])

    def test_rejects_nonpublic_destinations_before_transport(self):
        urls = ['file:///etc/passwd', 'ftp://example.org', 'http://localhost',
                'http://example.local', 'http://user:pass@example.org',
                'http://127.0.0.1', 'http://[::1]', 'http://169.254.169.254',
                'http://example.org/\nsecret', 'http://example.org\\evil']
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.probe(url)['outcome'], 'unsafe_destination')
        self.assertEqual(self.calls, [])

    def test_blocks_private_mixed_dns_and_private_redirects(self):
        self.assertEqual(self.probe(addresses=['93.184.216.34', '10.0.0.1'])['outcome'], 'unsafe_destination')
        result = self.probe(replies=[(302, {'location': 'http://192.168.1.1/private'})])
        self.assertEqual(result['outcome'], 'unsafe_destination')
        self.assertEqual(len(self.calls), 1)

    def test_redirect_budget_is_bounded(self):
        result = self.probe(replies=[(302, {'location': '/again'})] * 3, max_redirects=2)
        self.assertEqual(result['outcome'], 'redirect_limit')
        self.assertEqual(len(self.calls), 3)

    def test_http_failures_are_differentiated(self):
        for code, expected in [(403, 'blocked'), (401, 'blocked'), (429, 'rate_limited'),
                               (503, 'transient'), (404, 'http_error'), (302, 'http_error')]:
            with self.subTest(code=code):
                self.assertEqual(self.probe(replies=[(code, {})])['outcome'], expected)

    def test_transport_failures_are_nonfatal_and_differentiated(self):
        for error, expected in [(socket.gaierror('dns'), 'dns_error'),
                                (ssl.SSLError('tls'), 'tls_error'),
                                (TimeoutError('timeout'), 'timeout'),
                                (ConnectionResetError('reset'), 'transient')]:
            with self.subTest(expected=expected):
                self.assertEqual(self.probe(replies=[error])['outcome'], expected)

    def test_overdeadline_transport_result_is_not_reachability(self):
        import time
        def slow_transport(*args):
            time.sleep(0.03)
            return 200, {}
        result = self.audit.probe_url('https://example.org', timeout=0.01,
            resolver=lambda *args: ['93.184.216.34'], transport=slow_transport)
        self.assertEqual(result['outcome'], 'timeout')

    def test_dns_failure_is_reported(self):
        def resolver(*args):
            raise socket.gaierror('no address')
        result = self.audit.probe_url('https://example.org', resolver=resolver,
                                      transport=lambda *args: self.fail('unexpected transport'))
        self.assertEqual(result['outcome'], 'dns_error')


    def test_transport_closes_response_without_reading_body(self):
        from unittest.mock import MagicMock, patch
        conn = MagicMock()
        response = conn.getresponse.return_value
        response.status = 200
        response.getheaders.return_value = []
        with patch.object(self.audit.http.client, 'HTTPConnection', return_value=conn), \
             patch.object(self.audit.socket, 'create_connection', return_value=MagicMock()):
            self.audit.head_transport('http://example.org', '93.184.216.34', 1)
        response.close.assert_called_once()
        response.read.assert_not_called()
        conn.close.assert_called_once()

    def test_transport_uses_head_pinned_socket_without_body_reads(self):
        from unittest.mock import patch
        client, server = socket.socketpair()
        server.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 1000000000\r\n\r\n')
        try:
            with patch.object(self.audit.socket, 'create_connection', return_value=client) as connect:
                status, _ = self.audit.head_transport('http://example.org/path?q=1', '93.184.216.34', 1)
            self.assertEqual(status, 200)
            self.assertEqual(connect.call_args.args[0], ('93.184.216.34', 80))
            request = server.recv(4096)
            self.assertIn(b'HEAD /path?q=1 HTTP/1.1', request)
            self.assertIn(b'Host: example.org', request)
            self.assertNotIn(b'Authorization:', request)
            self.assertEqual(client.fileno(), -1)
        finally:
            client.close()
            server.close()

    def test_transport_deadline_bounds_slow_header_trickle(self):
        import threading
        import time
        from unittest.mock import patch
        client, server = socket.socketpair()
        def trickle():
            try:
                server.recv(4096)
                server.sendall(b'HTTP/1.1 200 OK\r\nX-Test: ')
                for byte in b'a' * 100 + b'\r\n\r\n':
                    server.sendall(bytes([byte]))
                    time.sleep(0.01)
            except OSError:
                pass
            finally:
                server.close()
        worker = threading.Thread(target=trickle)
        worker.start()
        started = time.monotonic()
        try:
            with patch.object(self.audit.socket, 'create_connection', return_value=client):
                try:
                    self.audit.head_transport('http://example.org', '93.184.216.34', 0.4)
                except (TimeoutError, OSError):
                    pass
            self.assertLess(time.monotonic() - started, 0.8, 'total deadline must stop header trickles')
        finally:
            client.close()
            worker.join(timeout=2)

    def test_dns_subprocess_is_bounded_and_classifies_resolution_errors(self):
        import subprocess
        from types import SimpleNamespace
        from unittest.mock import patch
        with patch.object(self.audit.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='["93.184.216.34"]')) as run:
            self.assertEqual(self.audit.resolve_public('example.org', 443, 0.5), ['93.184.216.34'])
            self.assertEqual(run.call_args.kwargs['timeout'], 0.5)
        with patch.object(self.audit.subprocess, 'run', side_effect=subprocess.TimeoutExpired('resolver', 0.5)):
            with self.assertRaises(TimeoutError):
                self.audit.resolve_public('example.org', 443, 0.5)
        with patch.object(self.audit.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(socket.gaierror):
                self.audit.resolve_public('example.org', 443, 0.5)


class ReportTests(unittest.TestCase):
    def setUp(self):
        import catalog_audit
        self.audit = catalog_audit
        self.catalog = {'resources': [
            {'id': 'a', 'name': 'A', 'url': 'https://example.org', 'categoryPath': ['recommend'], 'description': 'Description A'},
            {'id': 'b', 'name': 'A', 'url': 'https://example.org', 'categoryPath': ['tool'], 'description': 'Description A'},
            {'id': 'c', 'name': 'B', 'url': 'https://other.example', 'categoryPath': ['recommend'], 'description': 'Description B'}]}
        self.review = {'url': 'https://example.org', 'name': 'A',
                       'reviewed_description': 'Description A',
                       'checked_at': '2026-01-01', 'method': 'document-review',
                       'rationale': 'Useful documentation', 'scope': 'Public manual only',
                       'limitations': 'Not installed or run', 'evidence': ['https://example.org/docs']}

    def build(self, reviews=None, **kwargs):
        self.assertTrue(hasattr(self.audit, 'build_report'), 'report builder is not implemented')
        from datetime import date
        def probe(url, **options):
            return {'url': url, 'final_url': url + '/new', 'outcome': 'reachable', 'status': 200, 'redirects': [url + '/new']}
        return self.audit.build_report(self.catalog, reviews or {'reviews': [self.review]},
                                       today=date(2026, 5, 1), probe=probe, **kwargs)

    def test_preserves_occurrences_deduplicates_probes_and_flags_stale_missing(self):
        report = self.build()
        self.assertEqual(report['resource_occurrences'], 3)
        self.assertEqual(len(report['links']), 2)
        self.assertEqual(len(report['links'][0]['occurrences']), 2)
        self.assertEqual([r['state'] for r in report['recommendations']], ['expired', 'missing'])
        self.assertEqual(report['recommendations'][0]['method'], 'document-review')
        self.assertEqual(report['recommendations'][0]['limitations'], 'Not installed or run')

    def test_review_expiry_is_configurable_at_threshold(self):
        self.assertEqual(self.build(max_age_days=121)['recommendations'][0]['state'], 'current')
        self.assertEqual(self.build(max_age_days=120)['recommendations'][0]['state'], 'expired')

    def test_bad_future_duplicate_or_incomplete_review_is_never_current(self):
        for change in [{'checked_at': '2027-01-01'}, {'checked_at': 'not-a-date'},
                       {'method': 'human-verified'}, {'evidence': []}, {'limitations': ''}]:
            with self.subTest(change=change):
                data = dict(self.review, **change)
                self.assertEqual(self.build({'reviews': [data]})['recommendations'][0]['state'], 'invalid')
        self.assertEqual(self.build({'reviews': [self.review, self.review]})['recommendations'][0]['state'], 'invalid')
        self.assertTrue(self.build({'reviews': 'bad'})['errors'])

    def test_changed_or_missing_reviewed_description_requires_review(self):
        for description in [None, 'Old recommendation']:
            record = dict(self.review)
            if description is None:
                record.pop('reviewed_description')
            else:
                record['reviewed_description'] = description
            finding = self.build({'reviews': [record]}, max_age_days=200)['recommendations'][0]
            self.assertEqual(finding['state'], 'review-needed')
            self.assertIn('reviewed_description', ' '.join(finding['problems']))

    def test_changed_redirect_target_compares_previous_snapshot(self):
        previous = {'links': {'https://example.org': {'final_url': 'https://example.org/old', 'outcome': 'reachable'}}}
        report = self.build(previous=previous)
        self.assertTrue(report['links'][0]['redirect_target_changed'])
        self.assertEqual(report['links'][0]['previous_final_url'], 'https://example.org/old')
        self.assertIsNone(report['links'][1]['redirect_target_changed'])
        self.assertEqual(self.audit.link_snapshot(report)['links']['https://example.org']['final_url'], 'https://example.org/new')

    def test_limit_is_explicit_and_does_not_hide_unprobed_recommendations(self):
        report = self.build(limit=1)
        self.assertEqual(len(report['links']), 1)
        self.assertEqual(report['unprobed_urls'], 1)
        self.assertEqual(len(report['recommendations']), 2)

    def test_markdown_contains_caveat_and_review_details(self):
        report = self.build()
        self.assertTrue(hasattr(self.audit, 'render_markdown'), 'Markdown renderer is not implemented')
        text = self.audit.render_markdown(report)
        for value in ['HTTP 200', 'quality', 'document-review', 'Not installed or run', 'expired', 'missing', 'https://example.org']:
            self.assertIn(value, text)

    def test_cli_writes_reports_and_snapshot_with_offline_transport(self):
        import json
        import tempfile
        from unittest.mock import patch
        self.assertTrue(hasattr(self.audit, 'main'), 'CLI is not implemented')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / 'README.md'
            readme.write_text('## 링크\n- <span id="recommend">추천</span>\n  - [A](https://example.org)\n')
            reviews = root / 'reviews.json'
            reviews.write_text(json.dumps({'reviews': [self.review]}))
            previous = root / 'previous.json'
            previous.write_text(json.dumps({'links': {'https://example.org': {'final_url': 'https://example.org/old'}}}))
            output = root / 'out'
            with patch.object(self.audit, 'resolve_public', return_value=['93.184.216.34']), \
                 patch.object(self.audit, 'head_transport', return_value=(200, {})):
                code = self.audit.main(['--readme', str(readme), '--reviews', str(reviews),
                                        '--previous', str(previous), '--output-dir', str(output),
                                        '--max-workers', '2', '--timeout', '1', '--limit', '1'])
            self.assertEqual(code, 0)
            report = json.loads((output / 'report.json').read_text())
            self.assertTrue(report['links'][0]['redirect_target_changed'])
            self.assertTrue((output / 'report.md').is_file())
            self.assertIn('https://example.org', json.loads((output / 'link-snapshot.json').read_text())['links'])
            with patch.object(self.audit, 'resolve_public', side_effect=socket.gaierror('offline')):
                self.assertEqual(self.audit.main(['--readme', str(readme), '--reviews', str(root/'missing.json'), '--output-dir', str(output)]), 0)
            report = json.loads((output / 'report.json').read_text())
            self.assertEqual(report['links'][0]['outcome'], 'dns_error')
            self.assertTrue(report['errors'])

    def test_workflow_has_real_previous_persistence_and_always_uploads(self):
        path = ROOT / '.github/workflows/catalog-audit.yml'
        self.assertTrue(path.is_file(), 'weekly workflow is not implemented')
        text = path.read_text()
        for required in ['schedule:', 'workflow_dispatch:', 'contents: read',
                         'actions/cache/restore@', 'actions/cache/save@', '--previous',
                         'test_catalog_audit.py', 'if: always()', 'actions/upload-artifact@',
                         'persist-credentials: false', 'shell: bash']:
            self.assertIn(required, text)
        for forbidden in ['secrets.', 'GH_TOKEN', 'GITHUB_TOKEN', 'contents: write', 'pull_request_target']:
            self.assertNotIn(forbidden, text)


if __name__ == '__main__':
    unittest.main()
