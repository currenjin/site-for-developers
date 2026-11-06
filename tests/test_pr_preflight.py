"""PR 사전 검사의 데이터 및 신뢰 경계 회귀 테스트."""
import os
import re
import textwrap
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/pr_preflight.py'
sys.path.insert(0, str(ROOT / 'scripts'))


def readme(*rows):
    return '## 링크\n- <span id="tools">Tools</span>\n' + '\n'.join('  - ' + row for row in rows) + '\n## 기여\n'


A = '[Alpha](https://alpha.test) - 작업 실행 도구'
B = '[Beta](https://beta.test) - 문서 검색 도구'


def evidence(name='Beta', url='https://beta.test', mode='직접 사용'):
    return f'''### 항목: {name}
- 대상 URL: {url}
- 공식 홈페이지·문서·저장소 URL: {url}/docs
- 확인일 및 접속 환경 / HTTP·DNS·TLS 상태 / 최종 URL: 2026-11-06 / Linux / HTTP 200 / {url}
- 제작자 또는 이해관계 여부: 없음
- 검증 방식: {mode}
- 수행한 작업 / 입력: beta search --query python 실행
- 기대 결과 / 실제 결과: 검색 결과 반환 / Python 문서 3건 반환
- 확인 범위 / 확인하지 못한 범위: CLI 검색 기능 / 유료 팀 기능은 확인하지 못함
- 기존 항목 대신 선택할 이유: Alpha와 달리 오프라인 문서를 검색할 수 있음
'''


class PreflightTests(unittest.TestCase):
    def run_cli(self, base, head, body, output='json'):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for name, text in [('base', base), ('head', head), ('body', body)]:
                path = Path(directory) / name
                path.write_text(text, encoding='utf-8')
                paths.append(str(path))
            return subprocess.run([sys.executable, str(SCRIPT), '--base-readme', paths[0], '--head-readme', paths[1], '--body-file', paths[2], '--format', output], capture_output=True, text=True)

    def check(self, base, head, body):
        result = self.run_cli(base, head, body)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result, json.loads(result.stdout)

    def test_new_resource_requires_explicit_evidence(self):
        result, report = self.check(readme(A), readme(A, B), '')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['status'], 'needs_changes')
        self.assertEqual(report['changed'][0]['name'], 'Beta')
        self.assertTrue(report['errors'])

    def test_complete_hands_on_evidence_passes(self):
        result, report = self.check(readme(A), readme(A, B), evidence())
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['errors'], [])

    def test_docs_only_and_unchanged_existing_duplicates_pass(self):
        result, report = self.check(readme(A, A), '# new introduction\n' + readme(A, A), '')
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['changed'], [])

    def test_description_and_label_changes_require_evidence(self):
        for row in [A.replace('작업 실행 도구', '다른 기능 설명'), A.replace('Alpha]', 'Alpha <sub>F</sub>]')]:
            with self.subTest(row=row):
                result, report = self.check(readme(A), readme(row), '')
                self.assertEqual(result.returncode, 1, report)

    def test_reordering_does_not_require_evidence(self):
        result, report = self.check(readme(A, B), readme(B, A), '')
        self.assertEqual(result.returncode, 0, report)

    def test_each_resource_must_match_its_heading_and_exact_target_url(self):
        for body in [evidence('Alpha'), evidence(url='https://wrong.test'), evidence().replace('### 항목: Beta', '### 기타')]:
            result, report = self.check(readme(), readme(B), body)
            self.assertEqual(result.returncode, 1, report)

    def test_empty_placeholders_are_not_evidence_but_no_conflict_is_valid(self):
        for placeholder in ['-', '없음', '(작성)', 'TODO', 'N/A', '미확인']:
            body = evidence().replace('Alpha와 달리 오프라인 문서를 검색할 수 있음', placeholder)
            result, report = self.check(readme(), readme(B), body)
            self.assertEqual(result.returncode, 1, (placeholder, report))
        result, report = self.check(readme(), readme(B), evidence())
        self.assertEqual(result.returncode, 0, report)

    def test_conflict_disclosure_and_valid_checked_date_are_required(self):
        for old, new in [('제작자 또는 이해관계 여부: 없음', '제작자 또는 이해관계 여부: -'), ('2026-11-06', '2026-02-30')]:
            result, report = self.check(readme(), readme(B), evidence().replace(old, new))
            self.assertEqual(result.returncode, 1, report)

    def test_hands_on_requires_both_expected_and_actual_outcome(self):
        for outcome in ['문서 참고', '검색 결과 반환 / -', '검색 결과 반환 / 미실행']:
            body = evidence().replace('검색 결과 반환 / Python 문서 3건 반환', outcome)
            result, report = self.check(readme(), readme(B), body)
            self.assertEqual(result.returncode, 1, report)

    def test_documentation_mode_allows_honest_nonexecution_with_source_scope_and_limits(self):
        body = evidence(mode='문서 확인').replace('beta search --query python 실행', 'https://beta.test/docs/search 의 CLI 입력 예제와 옵션 표 확인').replace('검색 결과 반환 / Python 문서 3건 반환', '직접 실행하지 않음, 문서 설명만 확인')
        result, report = self.check(readme(), readme(B), body)
        self.assertEqual(result.returncode, 0, report)
        for bad in [body.replace('https://beta.test/docs/search 의 CLI 입력 예제와 옵션 표 확인', '문서 확인'), body.replace('CLI 검색 기능 / 유료 팀 기능은 확인하지 못함', '확인 완료')]:
            result, report = self.check(readme(), readme(B), bad)
            self.assertEqual(result.returncode, 1, report)

    def test_documentation_scope_can_reference_shared_official_url(self):
        body = evidence(mode='문서 확인').replace('beta search --query python 실행', '공식 검색 가이드의 CLI 입력 예제와 옵션 표 확인').replace('검색 결과 반환 / Python 문서 3건 반환', '입력 옵션이 검색 절에 명시된 것을 확인함. 실제 검색 실행은 하지 않음')
        result, report = self.check(readme(), readme(B), body)
        self.assertEqual(result.returncode, 0, report)

    def test_unverified_and_unselected_mode_need_changes(self):
        for mode in ['미확인', '(직접 사용 / 문서 확인 / 미확인)']:
            result, report = self.check(readme(), readme(B), evidence(mode=mode))
            self.assertEqual(result.returncode, 1, report)

    def test_duplicate_canonical_url_name_and_tracking_are_warnings_only(self):
        row = '[Alpha](https://www.alpha.test/?utm_source=ad&fbclid=123) - 세계 최고의 도구'
        body = evidence('Alpha', 'https://www.alpha.test/?utm_source=ad&fbclid=123')
        result, report = self.check(readme(A), readme(A, row), body)
        self.assertEqual(result.returncode, 0, report)
        codes = {warning['code'] for warning in report['warnings']}
        self.assertTrue({'duplicate_url', 'duplicate_name', 'tracking_url', 'sales_language'} <= codes, codes)
        self.assertEqual(report['changed'][0]['url'], 'https://www.alpha.test/?utm_source=ad&fbclid=123')

    def test_obvious_known_name_hostname_mismatch_is_warning_only(self):
        row = '[GitHub](https://gitlab.com) - 코드 호스팅'
        result, report = self.check(readme(), readme(row), evidence('GitHub', 'https://gitlab.com'))
        self.assertEqual(result.returncode, 0, report)
        self.assertIn('name_hostname', {w['code'] for w in report['warnings']})

    def test_recommendation_reexposure_is_allowed(self):
        head = readme(A).replace('\n## 기여', '\n- <span id="recommend">추천</span>\n  - ' + A + '\n## 기여')
        result, report = self.check(readme(A), head, '')
        self.assertEqual(result.returncode, 0, report)

    def test_comments_and_fenced_examples_cannot_supply_evidence(self):
        for body in ['<!--\n' + evidence() + '\n-->', '```markdown\n' + evidence() + '\n```']:
            result, report = self.check(readme(), readme(B), body)
            self.assertEqual(result.returncode, 1, report)

    def test_template_item_marker_and_global_fields_are_supported(self):
        body = evidence().replace('### 항목: Beta\n- 대상 URL: https://beta.test', '## 최소 확인 결과\n- 검증 대상 이름 / README URL: Beta / https://beta.test')
        lines = body.splitlines()
        shared = [line for line in lines if any(line.startswith('- ' + label + ':') for label in ['공식 홈페이지·문서·저장소 URL', '확인일 및 접속 환경 / HTTP·DNS·TLS 상태 / 최종 URL', '제작자 또는 이해관계 여부'])]
        details = [line for line in lines if line not in shared]
        shared[2] = '**제작자 또는 이해관계 여부:** 없음'
        body = '## 공통 근거\n' + '\n'.join(shared) + '\n' + '\n'.join(details)
        result, report = self.check(readme(), readme(B), body)
        self.assertEqual(result.returncode, 0, report)

    def test_multiple_item_blocks_cannot_silently_share_work_evidence(self):
        beta = evidence().replace('### 항목: Beta\n- 대상 URL: https://beta.test', '## 최소 확인 결과\n- 검증 대상 이름 / README URL: Beta / https://beta.test')
        alpha = evidence('Alpha', 'https://alpha.test').replace('### 항목: Alpha\n- 대상 URL: https://alpha.test', '## 최소 확인 결과\n- 검증 대상 이름 / README URL: Alpha / https://alpha.test')
        for body, expected in [(beta, 1), (beta + '\n' + alpha, 0), (beta + '\n' + beta + '\n' + alpha, 1)]:
            result, report = self.check(readme(), readme(A, B), body)
            self.assertEqual(result.returncode, expected, report)

    def test_current_empty_template_cannot_supply_evidence(self):
        body = (ROOT / '.github/pull_request_template.md').read_text()
        result, report = self.check(readme(), readme(B), body)
        self.assertEqual(result.returncode, 1, report)

    def test_unselected_conflict_template_is_not_disclosure(self):
        result, report = self.check(readme(), readme(B), evidence().replace('제작자 또는 이해관계 여부: 없음', '제작자 또는 이해관계 여부: (없음 / 본인 제작 등)'))
        self.assertEqual(result.returncode, 1, report)

    def test_hands_on_cannot_claim_actual_outcome_was_not_executed(self):
        body = evidence().replace('Python 문서 3건 반환', '직접 실행하지 않음, 결과는 문서에서만 확인')
        result, report = self.check(readme(), readme(B), body)
        self.assertEqual(result.returncode, 1, report)

    def test_report_output_and_invalid_readme(self):
        result = self.run_cli(readme(), readme(B), evidence(), 'report')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS', result.stdout)
        result, report = self.check(readme(), readme('[Bad](javascript:alert(1))'), '')
        self.assertEqual(result.returncode, 1, report)
        self.assertEqual(report['errors'][0]['code'], 'invalid_readme')


class WorkflowTests(unittest.TestCase):
    workflow = ROOT / '.github/workflows/pr-preflight.yml'

    def test_read_only_trusted_base_workflow_contract(self):
        self.assertTrue(self.workflow.is_file(), 'Missing preflight workflow')
        text = self.workflow.read_text()
        self.assertRegex(text, r'(?m)^  pull_request:')
        self.assertNotIn('pull_request_target', text)
        self.assertNotIn('secrets.', text)
        self.assertNotRegex(text, r':\s*write\b')
        self.assertIn('contents: read', text)
        self.assertIn('ref: ${{ github.event.pull_request.base.sha }}', text)
        self.assertIn('persist-credentials: false', text)
        self.assertIn('edited', text)
        self.assertIn('synchronize', text)
        for uses in re.findall(r'uses: (\S+)', text):
            self.assertRegex(uses, r'@[a-f0-9]{40}$')
        for block in re.findall(r'run: \|\n((?:          .*\n|\n)+)', text):
            self.assertNotIn('${{', block, 'Untrusted expressions must not enter shell source')
        self.assertIn('GITHUB_EVENT_PATH', text)
        self.assertIn('git', text)
        self.assertNotIn('checkout FETCH_HEAD', text)

    def test_workflow_reads_head_as_data_and_rejects_changed_head_sha(self):
        self.assertTrue(self.workflow.is_file(), 'Missing preflight workflow')
        text = self.workflow.read_text()
        match = re.search(r"python - <<'PY'\n(.*?)\n          PY", text, re.S)
        self.assertIsNotNone(match)
        program = textwrap.dedent(match[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repository'
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()
            git('init', '-q')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            (repo / 'README.md').write_text(readme(A))
            git('add', 'README.md')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            (repo / 'README.md').write_text(readme(A, B))
            (repo / 'malicious.py').write_text("raise RuntimeError('head code executed')")
            git('add', '.')
            git('commit', '-qm', 'head')
            head = git('rev-parse', 'HEAD')
            git('update-ref', 'refs/pull/7/head', head)
            git('checkout', '--detach', base)
            git('remote', 'add', 'origin', str(repo))
            event = root / 'event.json'
            payload = {'number': 7, 'pull_request': {'head': {'sha': head}, 'body': evidence() + '\n$(touch SHOULD_NOT_EXIST)'}}
            event.write_text(json.dumps(payload))
            env = dict(os.environ, RUNNER_TEMP=str(root / 'runner'), GITHUB_EVENT_PATH=str(event))
            result = subprocess.run([sys.executable, '-c', program], cwd=repo, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = root / 'runner/sfd-preflight'
            self.assertEqual((data / 'base.md').read_text(), readme(A))
            self.assertEqual((data / 'head.md').read_text(), readme(A, B))
            self.assertEqual((data / 'body.md').read_text(), payload['pull_request']['body'])
            self.assertFalse((repo / 'malicious.py').exists())
            self.assertFalse((repo / 'SHOULD_NOT_EXIST').exists())
            self.assertEqual(git('rev-parse', 'HEAD'), base)
            payload['pull_request']['head']['sha'] = base
            event.write_text(json.dumps(payload))
            result = subprocess.run([sys.executable, '-c', program], cwd=repo, env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('head SHA', result.stderr)


if __name__ == '__main__':
    unittest.main()
