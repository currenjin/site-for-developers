"""Read-only catalogue reachability audit, not a resource quality assessment.

DNS results are validated and pinned to the socket to prevent DNS rebinding.
HEAD requests download no response bodies and never forward credentials or cookies.
"""
import argparse
import http.client
import ipaddress
import json
import socket
import ssl
import subprocess
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from readme_catalog import parse_readme


class UnsafeDestination(ValueError):
    pass


def public_address(value):
    address = ipaddress.ip_address(value)
    mapped = getattr(address, 'ipv4_mapped', None)
    return (address.is_global and not address.is_multicast
            and not address.is_reserved and not address.is_unspecified
            and not (mapped and not public_address(str(mapped))))


def destination(url):
    if any(ord(c) < 33 or ord(c) == 127 for c in url) or '\\' in url:
        raise UnsafeDestination('Control characters or backslash in URL')
    parts = urlsplit(url)
    host = parts.hostname
    if (parts.scheme not in ('http', 'https') or not host
            or parts.username is not None or parts.password is not None):
        raise UnsafeDestination('Only public HTTP(S) without credentials is allowed')
    port = parts.port or (443 if parts.scheme == 'https' else 80)
    if host.rstrip('.').lower().endswith(('.localhost', '.local', '.internal', '.home', '.lan')) or host.rstrip('.').lower() == 'localhost':
        raise UnsafeDestination('Local hostname')
    try:
        if not public_address(host):
            raise UnsafeDestination('Nonpublic IP address')
    except ValueError as exc:
        if isinstance(exc, UnsafeDestination):
            raise
    return parts, host, port


def resolve_public(host, port, timeout):
    # A subprocess gives even a stuck platform resolver a hard wall-clock bound.
    code = ('import json,socket,sys; print(json.dumps(sorted(set('
            'x[4][0] for x in socket.getaddrinfo(sys.argv[1],int(sys.argv[2]),'
            'type=socket.SOCK_STREAM)))))')
    try:
        proc = subprocess.run([sys.executable, '-c', code, host, str(port)],
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError('DNS resolution timed out') from exc
    if proc.returncode:
        raise socket.gaierror('DNS resolution failed')
    return json.loads(proc.stdout)


def head_transport(url, address, timeout):
    parts, host, port = destination(url)
    deadline = time.monotonic() + timeout
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    timer = None
    expired = threading.Event()

    def interrupt():
        expired.set()
        try:
            if conn.sock is not None:
                conn.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    try:
        conn.sock = socket.create_connection((address, port), timeout=timeout)
        if parts.scheme == 'https':
            conn.sock.settimeout(max(0.001, deadline - time.monotonic()))
            conn.sock = ssl.create_default_context().wrap_socket(conn.sock, server_hostname=host)
        conn.sock.settimeout(max(0.001, deadline - time.monotonic()))
        # Socket timeouts alone reset on every receive; stop slow header trickles.
        timer = threading.Timer(max(0, deadline - time.monotonic()), interrupt)
        timer.daemon = True
        timer.start()
        target = urlunsplit(('', '', parts.path or '/', parts.query, ''))
        conn.request('HEAD', target, headers={'User-Agent': 'SFD-Catalog-Audit/1.0',
                                            'Connection': 'close', 'Accept': '*/*'})
        response = conn.getresponse()
        try:
            if expired.is_set() or time.monotonic() >= deadline:
                raise TimeoutError('HTTP probe deadline exceeded')
            return response.status, {key.lower(): value for key, value in response.getheaders()}
        finally:
            response.close()
    except (OSError, http.client.HTTPException) as exc:
        if expired.is_set():
            raise TimeoutError('HTTP probe deadline exceeded') from exc
        raise
    finally:
        if timer is not None:
            timer.cancel()
        conn.close()


def probe_url(url, *, timeout=10, max_redirects=5, resolver=None, transport=None):
    resolver = resolver or resolve_public
    transport = transport or head_transport
    result = {'url': url, 'final_url': url, 'status': None, 'redirects': []}
    deadline = time.monotonic() + timeout

    def remaining():
        budget = deadline - time.monotonic()
        if budget <= 0:
            raise TimeoutError('Probe deadline exceeded')
        return budget

    try:
        for hop in range(max_redirects + 1):
            current = result['final_url']
            _, host, port = destination(current)
            addresses = resolver(host, port, remaining())
            if not addresses:
                raise socket.gaierror('No DNS addresses')
            if not all(public_address(address) for address in addresses):
                raise UnsafeDestination('DNS includes a nonpublic address')
            status, headers = transport(current, addresses[0], remaining())
            remaining()
            result['status'] = status
            location = next((v for k, v in headers.items() if k.lower() == 'location'), None)
            if status in (301, 302, 303, 307, 308) and location:
                if hop == max_redirects:
                    result['outcome'] = 'redirect_limit'
                    return result
                target = urljoin(current, location)
                result['redirects'].append(target)
                result['final_url'] = target
                continue
            result['outcome'] = ('reachable' if 200 <= status < 300 else
                                 'blocked' if status in (401, 403) else
                                 'rate_limited' if status == 429 else
                                 'transient' if status >= 500 or status == 408 else 'http_error')
            return result
    except UnsafeDestination as exc:
        outcome = 'unsafe_destination'
    except socket.gaierror as exc:
        outcome = 'dns_error'
    except ssl.SSLError as exc:
        outcome = 'tls_error'
    except (TimeoutError, socket.timeout) as exc:
        outcome = 'timeout'
    except (OSError, http.client.HTTPException) as exc:
        outcome = 'transient'
    except (ValueError, UnicodeError) as exc:
        outcome = 'unsafe_destination'
    result['outcome'] = outcome
    return result


# Review metadata is provenance only, never a second catalogue or proof of quality.
ROOT = Path(__file__).resolve().parents[1]
CAVEAT = ('HTTP 200 indicates reachability only, not quality, safety, endorsement, '
          'pricing accuracy, or hands-on verification. HEAD may be blocked even '
          'when browser access works. Network failures require human review; '
          'nothing is automatically deleted or edited.')


def review_findings(resources, data, today, max_age_days):
    errors = []
    records = data.get('reviews') if isinstance(data, dict) else None
    if not isinstance(records, list):
        records = []
        errors.append('Review metadata must contain a reviews list')
    indexed = {}
    for number, record in enumerate(records, 1):
        resource = record if isinstance(record, dict) else None
        if (not isinstance(resource, dict) or not isinstance(resource.get('url'), str)
                or not isinstance(resource.get('name'), str)):
            errors.append(f'Review {number}: url and name must be strings')
            continue
        indexed.setdefault((resource['url'], resource['name']), []).append(record)
    findings = []
    for resource in resources:
        if 'recommend' not in resource['categoryPath']:
            continue
        finding = {key: resource[key] for key in ('id', 'name', 'url')}
        matches = indexed.get((resource['url'], resource['name']), [])
        finding['state'] = 'missing'
        if matches:
            review = matches[0]
            finding.update({key: review.get(key) for key in
                            ('checked_at', 'method', 'rationale', 'scope', 'limitations', 'evidence')})
            problems = []
            if len(matches) != 1:
                problems.append('Duplicate review records')
            for key in ('rationale', 'scope', 'limitations'):
                if not isinstance(review.get(key), str) or not review[key].strip():
                    problems.append(f'{key} must be a nonempty string')
            if review.get('method') not in ('document-review', 'hands-on'):
                problems.append('method must be document-review or hands-on')
            evidence = review.get('evidence')
            if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
                problems.append('evidence must be a nonempty list of strings')
            try:
                checked = date.fromisoformat(review.get('checked_at', ''))
                if checked.isoformat() != review['checked_at']:
                    raise ValueError('Use YYYY-MM-DD')
                finding['age_days'] = (today - checked).days
                if checked > today:
                    problems.append('checked_at is in the future')
            except (TypeError, ValueError):
                problems.append('checked_at must be an ISO YYYY-MM-DD date')
            description_changed = (not isinstance(review.get('reviewed_description'), str)
                                   or review['reviewed_description'] != resource.get('description', ''))
            if description_changed:
                problems.append('reviewed_description missing or differs from the current README description')
            finding['reviewed_description'] = review.get('reviewed_description')
            finding['current_description'] = resource.get('description', '')
            finding['problems'] = problems
            invalid = any(not problem.startswith('reviewed_description') for problem in problems)
            finding['state'] = ('invalid' if invalid else 'review-needed' if description_changed
                                else 'expired' if finding['age_days'] >= max_age_days else 'current')
        findings.append(finding)
    return findings, errors


def build_report(catalog, reviews, *, previous=None, today=None, max_age_days=90,
                 max_workers=8, timeout=10, limit=None, probe=None):
    today = today or datetime.now(timezone.utc).date()
    probe = probe or probe_url
    if not 1 <= max_workers <= 32 or not 0 < timeout <= 120 or max_age_days < 0 or (limit is not None and limit < 0):
        raise ValueError('workers: 1..32; timeout: (0,120]; age and limit: nonnegative')
    resources = catalog['resources']
    grouped = {}
    for resource in resources:
        grouped.setdefault(resource['url'], []).append(resource)
    urls = list(grouped)
    selected = urls if limit is None else urls[:limit]
    previous_links = previous.get('links', {}) if isinstance(previous, dict) else {}
    errors = []
    if not isinstance(previous_links, dict):
        errors.append('Previous snapshot links must be an object')
        previous_links = {}
    def check(url):
        result = probe(url, timeout=timeout)
        result['occurrences'] = grouped[url]
        old = previous_links.get(url)
        prior = old.get('final_url') if isinstance(old, dict) else None
        result['previous_final_url'] = prior
        observed = result['outcome'] in ('reachable', 'http_error', 'blocked', 'rate_limited')
        result['redirect_target_changed'] = (prior != result['final_url']) if prior and observed else None
        return result
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        links = list(pool.map(check, selected))
    recommendations, metadata_errors = review_findings(resources, reviews, today, max_age_days)
    return {'schema_version': 1, 'checked_at': today.isoformat(), 'caveat': CAVEAT,
            'resource_occurrences': len(resources), 'unique_urls': len(urls),
            'probed_urls': len(selected), 'unprobed_urls': len(urls) - len(selected),
            'max_age_days': max_age_days, 'max_workers': max_workers, 'timeout_seconds': timeout,
            'outcomes': dict(Counter(link['outcome'] for link in links)),
            'links': links, 'recommendations': recommendations,
            'errors': errors + metadata_errors, 'previous_links': previous_links}


def link_snapshot(report):
    # Keep the last observed target through DNS/TLS/timeout failures and partial runs.
    links = {url: value for url, value in report.get('previous_links', {}).items()
             if isinstance(value, dict) and isinstance(value.get('final_url'), str)}
    for link in report['links']:
        if link['outcome'] in ('reachable', 'http_error', 'blocked', 'rate_limited'):
            links[link['url']] = {key: link[key] for key in ('final_url', 'outcome', 'status')}
            links[link['url']]['checked_at'] = report['checked_at']
    return {'schema_version': 1, 'checked_at': report['checked_at'], 'links': links}


def render_markdown(report):
    def cell(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')
    lines = ['# Catalogue maintenance audit', '', report['caveat'], '',
             f"Checked (UTC): {report['checked_at']}; occurrences: {report['resource_occurrences']}; "
             f"unique URLs: {report['unique_urls']}; probed: {report['probed_urls']}; "
             f"not probed: {report['unprobed_urls']}", '', '## Input errors', '']
    lines.extend('- ' + cell(error) for error in report['errors'])
    if not report['errors']:
        lines.append('None.')
    lines += ['', '## Link probes', '', '| URL | Outcome | HTTP | Final URL | Previous target | Changed |',
              '| --- | --- | --- | --- | --- | --- |']
    for link in report['links']:
        lines.append('| ' + ' | '.join(cell(link.get(key)) for key in
                     ('url', 'outcome', 'status', 'final_url', 'previous_final_url', 'redirect_target_changed')) + ' |')
    lines += ['', f"## Recommendation reviews (maximum age {report['max_age_days']} days)", '',
              'Current means metadata is complete and recent, not independently verified. '
              'document-review and hands-on are recorded methods, not inferred from HTTP responses.', '']
    for review in report['recommendations']:
        lines += [f"### {cell(review['name'])}: {review['state']}", '', cell(review['url']), '']
        for key in ('checked_at', 'age_days', 'method', 'reviewed_description', 'current_description', 'rationale', 'scope', 'limitations', 'evidence', 'problems'):
            if key in review:
                lines.append(f"- {key}: {cell(review[key])}")
        lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--readme', type=Path, default=ROOT / 'README.md')
    parser.add_argument('--reviews', type=Path, default=ROOT / 'docs/reviews/recommendations.json')
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'audit-reports')
    parser.add_argument('--max-workers', type=int, default=8)
    parser.add_argument('--timeout', type=float, default=10)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--max-age-days', type=int, default=90)
    args = parser.parse_args(argv)
    if (not 1 <= args.max_workers <= 32 or not 0 < args.timeout <= 120
            or args.max_age_days < 0 or (args.limit is not None and args.limit < 0)):
        parser.error('workers: 1..32; timeout: (0,120]; age and limit: nonnegative')
    errors = []
    fatal = False
    try:
        catalog = parse_readme(args.readme.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        errors.append(f'README: {exc}')
        catalog = {'resources': []}
        fatal = True
    def load(path, label, default):
        if path is None:
            return default
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'{label}: {exc}')
            return default
    reviews = load(args.reviews, 'Reviews', {'reviews': []})
    previous = load(args.previous, 'Previous snapshot', {})
    report = build_report(catalog, reviews, previous=previous, max_age_days=args.max_age_days,
                          max_workers=args.max_workers, timeout=args.timeout, limit=args.limit)
    report['errors'].extend(errors)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, value in [('report.json', report), ('link-snapshot.json', link_snapshot(report))]:
        (args.output_dir / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'report.md').write_text(render_markdown(report), encoding='utf-8')
    print(f"Audit: {report['probed_urls']} URLs; {len(report['errors'])} input errors; reports: {args.output_dir}")
    return 1 if fatal else 0


if __name__ == '__main__':
    raise SystemExit(main())
