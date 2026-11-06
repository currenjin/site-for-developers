"""README 변경 항목의 PR 근거를 검사한다. 네트워크 조회나 원문 수정은 하지 않는다."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from readme_catalog import parse_readme, safe_url

OFFICIAL = '공식 홈페이지·문서·저장소 URL'
CHECKED = '확인일 및 접속 환경 / HTTP·DNS·TLS 상태 / 최종 URL'
CONFLICT = '제작자 또는 이해관계 여부'
MODE = '검증 방식'
WORK = '수행한 작업 / 입력'
OUTCOME = '기대 결과 / 실제 결과'
SCOPE = '확인 범위 / 확인하지 못한 범위'
REASON = '기존 항목 대신 선택할 이유'
FIELDS = (OFFICIAL, CHECKED, CONFLICT, MODE, WORK, OUTCOME, SCOPE, REASON)
PLACEHOLDERS = {'', '-', '없음', '미확인', '미실행', 'todo', 'tbd', 'n/a', '작성', '작성 필요', '입력', '여기에 작성'}
TRACKING = {'fbclid', 'gclid', 'dclid', 'msclkid', 'mc_cid', 'mc_eid'}


def substantive(value):
    value = value.strip().strip('()<>[]').strip()
    return value.casefold() not in PLACEHOLDERS and len(re.sub(r'\W', '', value)) >= 3


def tracking(key):
    return key.casefold().startswith('utm_') or key.casefold() in TRACKING


def canonical_url(value):
    """비교 전용 키. 원문 URL, 기능성 쿼리 및 경로 대소문자를 보존한다."""
    parts = urlsplit(value)
    host = (parts.hostname or '').lower().removeprefix('www.')
    port = parts.port
    if port and not ((parts.scheme == 'https' and port == 443) or (parts.scheme == 'http' and port == 80)):
        host += ':' + str(port)
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not tracking(k)))
    return urlunsplit(('https', host, parts.path.rstrip('/'), query, ''))


def signature(resource, category=True):
    values = (resource['name'], resource['url'], resource['description'], tuple(resource['labels']))
    return values + (tuple(resource['categoryPath']),) if category else values


def evidence_blocks(body):
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    blocks = []
    shared = {}
    current = None
    fence = None
    active_field = None
    for line in body.splitlines():
        fenced = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fenced:
            marker = fenced[1][0]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence:
            continue
        heading = re.match(r'^#{1,6}\s+항목:\s*(.+?)\s*$', line)
        if heading:
            current = {'name': heading[1], 'fields': {}}
            blocks.append(current)
            active_field = None
            continue
        if re.match(r'^#{1,3}\s', line):
            current = None
            active_field = None
        normalized = re.sub(r'^\s*-\s+', '', line).replace('**', '')
        field = re.match(r'^([^:]+):\s*(.*)$', normalized)
        if field:
            key, value = field.groups()
            if key == '검증 대상 이름 / README URL':
                target = re.fullmatch(r'(.+?)\s+/\s+(https?://\S+)', value)
                current = {'name': target[1] if target else '', 'fields': {'대상 URL': target[2] if target else ''}}
                blocks.append(current)
                active_field = None
                continue
            destination = current['fields'] if current is not None else shared
            if current is None and key not in (OFFICIAL, CHECKED, CONFLICT):
                continue
            # 중복 필드는 마지막 값으로 덮어쓰지 않고 모호한 근거로 처리한다.
            destination[key] = '' if key in destination else value
            active_field = key
        elif active_field and line.startswith(('  ', '\t')):
            destination = current['fields'] if current is not None else shared
            destination[active_field] += ' ' + line.strip()
    for block in blocks:
        block['fields'] = dict(shared, **block['fields'])
    return blocks


def paired(value):
    parts = re.split(r'\s+/\s+', value, maxsplit=1)
    return len(parts) == 2 and all(substantive(part) for part in parts)


def validate_evidence(resource, blocks):
    matches = [b['fields'] for b in blocks if b['name'] == resource['name'] and b['fields'].get('대상 URL') == resource['url']]
    if len(matches) != 1:
        return [('evidence_match', '- 검증 대상 이름 / README URL: 이름 / 원문 URL이 일치하는 항목별 근거 블록 하나가 필요합니다. (### 항목: 이름 및 - 대상 URL: 원문 URL도 지원합니다.)')]
    fields = matches[0]
    errors = []
    for label in FIELDS:
        value = fields.get(label, '')
        valid = substantive(value)
        if label == CONFLICT:
            valid = value.strip() == '없음' or (substantive(value) and '없음 / 본인 제작' not in value)
        if not valid:
            errors.append(('required_field', label + ': 구체적인 근거가 필요합니다.'))
    official_urls = re.findall(r'https?://[^\s<>]+', fields.get(OFFICIAL, ''))
    if not any(safe_url(url) for url in official_urls):
        errors.append(('official_url', OFFICIAL + ': HTTP(S) URL이 필요합니다.'))
    checked = re.search(r'\b\d{4}-\d{2}-\d{2}\b', fields.get(CHECKED, ''))
    try:
        if not checked:
            raise ValueError()
        date.fromisoformat(checked[0])
    except ValueError:
        errors.append(('checked_date', CHECKED + ': 유효한 YYYY-MM-DD 확인일이 필요합니다.'))
    mode = fields.get(MODE, '').strip()
    if mode not in ('직접 사용', '문서 확인'):
        errors.append(('verification_mode', '검증 방식은 직접 사용 또는 문서 확인이어야 합니다. 미확인은 보완이 필요합니다.'))
    if mode == '직접 사용':
        outcome = fields.get(OUTCOME, '')
        actual = re.split(r'\s+/\s+', outcome, maxsplit=1)[-1]
        not_executed = re.search(r'미실행|실행하지 않|실행 안 함|not (?:run|executed)', actual, re.I)
        if not paired(outcome) or not_executed:
            errors.append(('outcome', OUTCOME + ': 기대 결과 / 실제 관찰 결과를 각각 작성하세요.'))
    if not paired(fields.get(SCOPE, '')):
        errors.append(('scope', SCOPE + ': 확인 범위 / 확인하지 못한 범위를 각각 작성하세요.'))
    if mode == '문서 확인':
        work = fields.get(WORK, '')
        urls = re.findall(r'https?://[^\s<>]+', work) + official_urls
        remainder = re.sub(r'https?://[^\s<>]+', '', work).strip()
        generic = remainder in ('문서 확인', '공식 문서 확인', '문서를 확인함', '확인 완료')
        if not any(safe_url(url) for url in urls) or not substantive(remainder) or generic:
            errors.append(('document_scope', WORK + ': 공식 출처 URL과 실제 확인한 절·표·예제 등 확인 대상을 작성하세요. 출처 URL은 공통 필드에 있어도 되며, 실행하지 않았다고 밝혀도 됩니다.'))
    return errors


def preflight(base_text, head_text, body):
    report = {'status': 'pass', 'changed': [], 'errors': [], 'warnings': []}
    try:
        base = parse_readme(base_text)
        head = parse_readme(head_text)
    except ValueError as exc:
        report['errors'].append({'code': 'invalid_readme', 'message': str(exc)})
        report['status'] = 'needs_changes'
        return report
    counts = Counter(signature(r) for r in base['resources'])
    existing = {signature(r, False) for r in base['resources']}
    recommended = {c['id'] for c in head['categories'] if re.search(r'추천|recommend', c['name'] + ' ' + c['id'], re.I)}
    for resource in head['resources']:
        key = signature(resource)
        if counts[key]:
            counts[key] -= 1
        elif signature(resource, False) in existing and recommended.intersection(resource['categoryPath']):
            continue
        else:
            report['changed'].append(resource)
    blocks = evidence_blocks(body)
    for resource in report['changed']:
        context = {'name': resource['name'], 'url': resource['url'], 'sourceLine': resource['sourceLine']}
        for code, message in validate_evidence(resource, blocks):
            report['errors'].append(dict(context, code=code, message=message))
        def warn(code, message):
            report['warnings'].append(dict(context, code=code, message=message))
        others = [r for r in head['resources'] if r is not resource]
        try:
            duplicates = [r for r in others if canonical_url(r['url']) == canonical_url(resource['url'])]
        except ValueError:
            duplicates = []
        if duplicates:
            warn('duplicate_url', '정확히 일치하거나 추적 매개변수를 제외한 URL 중복 후보입니다. 추천 재노출 여부를 사람이 확인하세요.')
        if any(re.sub(r'\W', '', r['name']).casefold() == re.sub(r'\W', '', resource['name']).casefold() for r in others):
            warn('duplicate_name', '이름 중복 후보입니다. 동일 서비스인지 사람이 확인하세요.')
        if any(tracking(k) for k, _ in parse_qsl(urlsplit(resource['url']).query)):
            warn('tracking_url', '추적 매개변수가 포함되어 있습니다. 원문 URL은 변경하지 않았습니다.')
        if re.search(r'세계 최고|최고의|업계 유일|압도적|\b(?:world.s best|best-in-class|number one)\b', resource['name'] + ' ' + resource['description'], re.I):
            warn('sales_language', '홍보성 최상급 표현 후보입니다. 사람이 문맥을 확인하세요.')
        # 단순 이름 유사도는 브랜드, 모회사, 한국어 이름을 오판하므로 사용하지 않는다.
        known = {'github': 'github.com', 'gitlab': 'gitlab.com'}
        name = resource['name'].casefold()
        host = (urlsplit(resource['url']).hostname or '').lower().removeprefix('www.')
        if name in known and host in known.values() and host != known[name]:
            warn('name_hostname', '알려진 코드 호스팅 이름과 다른 코드 호스팅 호스트입니다. 공식 출처를 사람이 확인하세요.')
    if report['errors']:
        report['status'] = 'needs_changes'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-readme', type=Path, required=True)
    parser.add_argument('--head-readme', type=Path, required=True)
    parser.add_argument('--body-file', type=Path, required=True)
    parser.add_argument('--format', choices=('json', 'report'), default='json')
    args = parser.parse_args()
    try:
        report = preflight(args.base_readme.read_text(encoding='utf-8'), args.head_readme.read_text(encoding='utf-8'), args.body_file.read_text(encoding='utf-8'))
    except (OSError, UnicodeError) as exc:
        report = {'status': 'needs_changes', 'changed': [], 'errors': [{'code': 'input_error', 'message': str(exc)}], 'warnings': []}
    if args.format == 'json':
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print('# PR preflight: ' + ('PASS' if report['status'] == 'pass' else 'NEEDS CHANGES'))
        print(f"\nChanged occurrences: {len(report['changed'])}; errors: {len(report['errors'])}; warnings: {len(report['warnings'])}")
        for severity in ('errors', 'warnings'):
            for finding in report[severity]:
                # 들여쓴 코드 블록으로 출력하여 제출한 Markdown을 명령/링크로 렌더링하지 않는다.
                text = f"{severity.upper()} [{finding['code']}] {finding.get('name', '')}: {finding['message']}"
                print('\n' + '\n'.join('    ' + line for line in text.splitlines()))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
