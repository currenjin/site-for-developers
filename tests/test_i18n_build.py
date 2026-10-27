"""Offline bilingual publication contracts, independent of real translation coverage."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site
from readme_catalog import parse_readme

README = '''# Fixture
## 링크
- <span id="tools">도구</span>
  - [이름 <sub>KR, F</sub>](https://example.com/a) - 설명
  - [English](https://example.com/b) - English description
'''
CACHE = {'도구': 'Tools', '이름': 'Name', '설명': 'Description'}
UI = {'ko': {'title': '제목', 'message': '한국어'},
      'en': {'title': 'Title', 'message': '<safe "quoted"> & text'}}
# Minimal fixture shell still supplies the real static renderer's UI contracts.
for values in UI.values():
    values.update(result_count='{count} / {total}', loading='Loading…',
                  korean_original='Korean original', static_load_error='Search unavailable.',
                  page_title=values['title'], meta_description=values['message'])
TEMPLATE = '''<!doctype html><html lang="{{lang}}"><head><title>{{title}}</title>
<link rel="canonical" href="{{canonical_url}}">
<link rel="alternate" hreflang="ko" href="{{alternate_ko_url}}">
<link rel="alternate" hreflang="en" href="{{alternate_en_url}}">
<link rel="icon" href="{{asset_prefix}}favicon.svg"></head>
<body data-message="{{message}}"><div id="results" class="results"></div><span id="category-total"></span><p id="result-count">{{loading}}</p><a href="{{locale_switch_href}}" lang="{{locale_switch_lang}}">switch</a>
<script src="{{asset_prefix}}app.js"></script></body></html>'''


class I18nBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        for name in build_site.ASSETS:
            dest = self.root / 'web' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / 'web' / name).read_bytes())
        logo = Path('resources/icons/header_base/576x157/header_base.svg')
        (self.root / logo).parent.mkdir(parents=True)
        (self.root / logo).write_bytes((ROOT / logo).read_bytes())
        (self.root / 'LICENSE').write_text('fixture license')
        (self.root / 'README.md').write_text(README)
        (self.root / 'web/index.html').write_text(TEMPLATE)
        (self.root / 'web/i18n').mkdir(exist_ok=True)
        self.write_json('ui.json', UI)
        self.write_json('en.json', CACHE)
        self.output = Path(self.temp.name) / 'site'
        self.patcher = patch.object(build_site, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def write_json(self, name, data):
        (self.root / 'web/i18n' / name).write_text(json.dumps(data, ensure_ascii=False))

    def build(self):
        build_site.build(self.output, 'fixture')
        self.assertTrue((self.output / 'en/resources.json').is_file(), 'English catalogue must be generated')
        return [json.loads((self.output / path).read_text())
                for path in ('resources.json', 'en/resources.json')]

    def test_both_locales_preserve_canonical_identity_and_source(self):
        original = (self.root / 'README.md').read_bytes()
        source = parse_readme(README)
        ko, en = self.build()
        self.assertEqual([ko['locale'], en['locale']], ['ko', 'en'])
        self.assertEqual(ko['ui'], UI['ko'])
        self.assertEqual(en['ui'], UI['en'])
        self.assertEqual(ko['resources'][0]['name'], '이름')
        self.assertEqual(en['resources'][0]['name'], 'Name')
        self.assertEqual(en['resources'][0]['description'], 'Description')
        self.assertEqual(en['resources'][0]['originalName'], '이름')
        self.assertEqual(en['resources'][0]['originalDescription'], '설명')
        self.assertEqual(en['resources'][0]['untranslatedFields'], [])
        self.assertEqual(en['categories'][0]['name'], 'Tools')
        self.assertEqual(en['categories'][0]['originalName'], '도구')
        self.assertFalse(en['categories'][0]['untranslated'])
        self.assertEqual(ko['resources'][0]['searchAliases'], ['Name', 'Description'])
        self.assertIn('Tools', ko['categories'][0]['searchAliases'])
        for locale in (ko, en):
            self.assertEqual(locale['translationStatus'],
                             {'pendingStrings': [], 'pendingResources': 0, 'pendingCategories': 0})
            self.assertEqual(locale['categoryReferences'], source['categoryReferences'])
            for actual, expected in zip(locale['resources'], source['resources']):
                for key in ('id', 'url', 'labels', 'labelSource', 'categoryPath', 'sourceLine'):
                    self.assertEqual(actual[key], expected[key])
            for actual, expected in zip(locale['categories'], source['categories']):
                for key in ('id', 'parent', 'path', 'aliases', 'count'):
                    self.assertEqual(actual[key], expected[key])
        self.assertEqual(ko['source'], en['source'])
        self.assertEqual((self.root / 'README.md').read_bytes(), original)

    def test_changed_source_never_reuses_stale_translation(self):
        (self.root / 'README.md').write_text(README.replace('설명', '새 설명'))
        ko, en = self.build()
        self.assertEqual(en['resources'][0]['description'], '새 설명')
        self.assertEqual(en['resources'][0]['untranslatedFields'], ['description'])
        self.assertEqual(en['translationStatus'],
                         {'pendingStrings': ['새 설명'], 'pendingResources': 1, 'pendingCategories': 0})
        self.assertEqual(ko['translationStatus'], en['translationStatus'])
        self.assertNotIn('Description', ko['resources'][0]['searchAliases'])

    def test_missing_cache_is_pending_not_a_build_blocker(self):
        (self.root / 'web/i18n/en.json').unlink()
        ko, en = self.build()
        self.assertEqual(en['resources'][0]['name'], '이름')
        self.assertEqual(en['resources'][0]['untranslatedFields'], ['name', 'description'])
        self.assertTrue(en['categories'][0]['untranslated'])
        status = en['translationStatus']
        self.assertEqual(set(status['pendingStrings']), set(CACHE))
        self.assertEqual(status['pendingResources'], 1)
        self.assertEqual(status['pendingCategories'], 1)
        self.assertEqual(ko['translationStatus'], status)
        self.assertEqual(en['resources'][1]['untranslatedFields'], [])

    def test_invalid_translations_are_pending_never_claimed_english(self):
        for value in ('', '  ', None, 12, [], '아직 한국어'):
            with self.subTest(value=value):
                self.write_json('en.json', dict(CACHE, 이름=value))
                ko, en = self.build()
                self.assertEqual(en['resources'][0]['name'], '이름')
                self.assertEqual(en['resources'][0]['untranslatedFields'], ['name'])
                self.assertNotIn(value, ko['resources'][0]['searchAliases'])

    def test_empty_cache_deduplicates_pending_text_but_counts_each_record(self):
        self.write_json('en.json', {})
        (self.root / 'README.md').write_text(README + '  - [이름](https://example.com/repeated) - 설명\n')
        ko, en = self.build()
        self.assertEqual(en['translationStatus'],
                         {'pendingStrings': sorted(CACHE), 'pendingResources': 2, 'pendingCategories': 1})
        self.assertEqual(len(en['resources']), 3)

    def test_malformed_cache_fails_before_artifacts_are_written(self):
        for value in ('{', '[]', 'null'):
            with self.subTest(value=value):
                (self.root / 'web/i18n/en.json').write_text(value)
                with self.assertRaises(ValueError):
                    build_site.build(self.output, 'fixture')
                self.assertFalse(self.output.exists())

    def test_unsafe_nested_output_does_not_overwrite_external_file(self):
        self.output.mkdir()
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside / 'index.html').write_text('keep')
        (self.output / 'en').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            build_site.build(self.output, 'fixture')
        self.assertEqual((outside / 'index.html').read_text(), 'keep')

    def test_template_context_is_escaped_and_shared_assets_not_duplicated(self):
        self.build()
        ko = (self.output / 'index.html').read_text()
        en = (self.output / 'en/index.html').read_text()
        self.assertIn('lang="ko"', ko)
        self.assertIn('lang="en"', en)
        self.assertIn('href="en/" lang="en"', ko)
        self.assertIn('href="../" lang="ko"', en)
        self.assertIn('src="../app.js"', en)
        self.assertIn('href="../favicon.svg"', en)
        self.assertIn('data-message="&lt;safe &quot;quoted&quot;&gt; &amp; text"', en)
        self.assertNotIn('{{', en)
        self.assertIn(build_site.SITE_URL + 'en/', en)
        self.assertIn(build_site.SITE_URL + 'en/', (self.output / 'sitemap.xml').read_text())
        self.assertEqual({p.name for p in (self.output / 'en').iterdir()}, {'index.html', 'resources.json'})
        self.assertFalse((self.output / 'i18n').exists())

    def test_ui_can_intentionally_leave_a_structural_fragment_empty(self):
        ui = copy.deepcopy(UI)
        ui['en']['title'] = ''
        self.write_json('ui.json', ui)
        ko, en = self.build()
        self.assertEqual(en['ui']['title'], '')
        self.assertIn('<title></title>', (self.output / 'en/index.html').read_text())

    def test_output_symlink_is_rejected_without_touching_target(self):
        target = Path(self.temp.name) / 'target'
        target.mkdir()
        self.output.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            build_site.build(self.output, 'fixture')
        self.assertEqual(list(target.iterdir()), [])

    def test_ui_key_coverage_or_unknown_template_key_fails_before_publication(self):
        cases = [({'ko': UI['ko'], 'en': {'title': 'Title'}}, TEMPLATE),
                 (UI, TEMPLATE + '{{missing}}'),
                 (UI, TEMPLATE + '{{ title }}'),
                 ({'ko': UI['ko'], 'en': dict(UI['en'], message=12)}, TEMPLATE)]
        for ui, template in cases:
            with self.subTest(ui=ui, template=template):
                self.write_json('ui.json', ui)
                (self.root / 'web/index.html').write_text(template)
                with self.assertRaises(ValueError):
                    build_site.build(self.output, 'fixture')
                self.assertFalse(self.output.exists())

    def test_status_cli_uses_same_pending_rules_and_optional_check(self):
        self.write_json('en.json', {'도구': 'Tools'})
        command = [sys.executable, str(ROOT / 'scripts/translation_status.py'), '--root', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status['pendingResources'], 1)
        self.assertEqual(status['pendingCategories'], 0)
        self.assertEqual(set(status['pendingStrings']), {'이름', '설명'})
        result = subprocess.run(command + ['--check'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), status)
        self.write_json('en.json', CACHE)
        self.assertEqual(subprocess.run(command + ['--check'], capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
