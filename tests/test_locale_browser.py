"""Bilingual UI browser contracts, plus a real project-prefix build smoke test.

Fixtures isolate frontend behavior from the translation-cache/build workstream.
They render the actual HTML template and run the actual JS/CSS in Chromium.
"""
import copy
import html
import json
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '/site-for-developers/'
CANONICAL = 'https://currenjin.github.io' + PREFIX


def fixture(locale, ui):
    english = locale == 'en'
    return {
        'locale': locale, 'ui': ui,
        'source': {'readme': 'https://github.com/currenjin/site-for-developers/blob/fixture/README.md', 'commit': 'fixture123'},
        'categories': [
            {'id': 'tools', 'name': 'Tools' if english else '개발 도구', 'originalName': '개발 도구', 'searchAliases': ['Tools'], 'aliases': ['개발 도구'], 'parent': None, 'path': ['tools'], 'count': 2},
            {'id': 'editors', 'name': 'Editors' if english else '편집기', 'originalName': '편집기', 'searchAliases': ['Editors'], 'aliases': ['편집기'], 'parent': 'tools', 'path': ['tools', 'editors'], 'count': 2},
        ],
        'resources': [
            {'id': 'editor-one', 'name': 'Cloud editor' if english else '구름 편집기', 'description': 'Collaborative programming' if english else '협업 프로그래밍', 'originalName': '구름 편집기', 'originalDescription': '협업 프로그래밍', 'searchAliases': ['Cloud editor', 'Collaborative programming'], 'url': 'https://example.com/editor?original=1#start', 'categoryPath': ['tools', 'editors'], 'labels': ['KR', 'F']},
            {'id': 'editor-two', 'name': '로컬 편집기', 'description': 'Offline editor' if english else '오프라인 편집기', 'originalName': '로컬 편집기', 'originalDescription': '오프라인 편집기', 'searchAliases': ['Offline editor'], 'url': 'https://example.com/offline', 'categoryPath': ['tools', 'editors'], 'labels': ['EN', 'O'], 'untranslatedFields': ['name'] if english else []},
        ],
        'translationStatus': {'pendingStrings': ['로컬 편집기'] if english else [], 'pendingResources': 1 if english else 0, 'pendingCategories': 0},
    }


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if not path.startswith(PREFIX):
            return str(Path(self.directory) / '__not_found__')
        return super().translate_path('/' + path[len(PREFIX):])

    def log_message(self, *args):
        pass


class LocaleBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='sfd-locales-')
        cls.site = Path(cls.temp.name)
        shutil.copytree(ROOT / 'web', cls.site, dirs_exist_ok=True)
        for name in ['logo.svg', 'favicon.svg', 'LICENSE']:
            source = ROOT / '_site' / name
            if source.exists():
                shutil.copyfile(source, cls.site / name)
        ui_file = ROOT / 'web/i18n/ui.json'
        ui = json.loads(ui_file.read_text()) if ui_file.exists() else {'en': {}, 'ko': {}}
        template = (ROOT / 'web/index.html').read_text()
        cls.datasets = {}
        for locale in ['ko', 'en']:
            dest = cls.site / ('en' if locale == 'en' else '')
            dest.mkdir(exist_ok=True)
            values = {**ui[locale], 'lang': locale, 'canonical_url': CANONICAL + ('en/' if locale == 'en' else ''), 'alternate_ko_url': CANONICAL, 'alternate_en_url': CANONICAL + 'en/', 'asset_prefix': '../' if locale == 'en' else '', 'locale_switch_href': '../' if locale == 'en' else 'en/', 'locale_switch_lang': 'ko' if locale == 'en' else 'en'}
            values.update(github_stars='1.2k', github_stars_full='1,179')
            rendered = re.sub(r'\{\{([a-z_]+)\}\}', lambda m: html.escape(values[m[1]], quote=True), template)
            (dest / 'index.html').write_text(rendered)
            cls.datasets[locale] = fixture(locale, ui[locale])
            (dest / 'resources.json').write_text(json.dumps(cls.datasets[locale], ensure_ascii=False))
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(cls.site)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}' + PREFIX
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def open(self, path='en/', **kwargs):
        page = self.browser.new_page(reduced_motion='reduce', **kwargs)
        self.addCleanup(page.close)
        page.goto(self.base + path, wait_until='networkidle')
        return page

    def test_english_template_metadata_and_shared_assets(self):
        page = self.open()
        self.assertEqual(page.locator('html').get_attribute('lang'), 'en')
        self.assertEqual(page.locator('h1').inner_text(), 'Your first\nbookmark.')
        self.assertEqual(page.locator('#language-switch').inner_text(), '한국어')
        self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), CANONICAL + 'en/')
        for language, suffix in [('ko', ''), ('en', 'en/'), ('x-default', '')]:
            self.assertEqual(page.locator(f'link[hreflang="{language}"]').get_attribute('href'), CANONICAL + suffix)
        for selector, attr, name in [('script[src]', 'src', 'app.js'), ('link[rel="stylesheet"]', 'href', 'styles.css'), ('link[rel="icon"]', 'href', 'favicon.svg'), ('.brand img', 'src', 'logo.svg'), ('#gem-poster', 'src', 'art/poster.png')]:
            self.assertEqual(page.locator(selector).get_attribute(attr), '../' + name)
        self.assertIn('Original README', page.locator('#readme-link').inner_text())
        page.locator('#label-note summary').click()
        self.assertIn('original resource', page.locator('#label-note').inner_text())

    def test_deep_link_switch_preserves_query_category_hash_reload_and_back(self):
        page = self.open('en/?q=Cloud&category=editors#directory')
        self.assertEqual(page.locator('.resource').count(), 1)
        switch = page.locator('#language-switch')
        href = switch.get_attribute('href')
        self.assertEqual(urlsplit(href).fragment, 'directory')
        self.assertEqual(parse_qs(urlsplit(href).query), {'q': ['Cloud'], 'category': ['editors']})
        # A real anchor retains browser-native open-in-new-tab behavior.
        with page.context.expect_page() as popup:
            switch.click(modifiers=['ControlOrMeta'])
        popup.value.wait_for_load_state('networkidle')
        self.assertEqual(popup.value.locator('html').get_attribute('lang'), 'ko')
        popup.value.close()
        switch.click()
        self.assertEqual(page.locator('html').get_attribute('lang'), 'ko')
        self.assertEqual(page.locator('.resource').count(), 1)
        self.assertEqual(page.locator('#search').input_value(), 'Cloud')
        page.reload(wait_until='networkidle')
        page.locator('#language-switch').click()
        self.assertEqual(page.locator('html').get_attribute('lang'), 'en')
        self.assertEqual(page.locator('.resource').count(), 1)
        page.go_back(wait_until='networkidle')
        self.assertEqual(page.locator('html').get_attribute('lang'), 'ko')
        self.assertIn('#directory', page.url)

    def test_search_both_languages_and_categories_in_either_locale(self):
        for locale in ['', 'en/']:
            page = self.open(locale)
            for query, expected in [('구름', 1), ('Cloud', 1), ('협업', 1), ('Collaborative', 1), ('편집기', 2), ('Editors', 2)]:
                page.locator('#search').fill(query)
                self.assertEqual(page.locator('.resource').count(), expected, (locale, query))
            page.locator('#search').fill('no-such-resource')
            self.assertTrue(page.locator('#empty').is_visible())
            page.locator('#reset').click()
            self.assertEqual(page.locator('.resource').count(), 2)
            page.go_back(wait_until='networkidle')
            self.assertEqual(page.locator('#search').input_value(), 'no-such-resource')

    def test_switch_tracks_changes_and_hash_without_data(self):
        page = self.open()
        page.locator('#search').fill('Cloud')
        page.locator('[data-category="tools"]').click()
        page.evaluate("location.hash='directory'")
        page.wait_for_function("document.querySelector('#language-switch').hash==='#directory'")
        href = page.locator('#language-switch').get_attribute('href')
        self.assertEqual(parse_qs(urlsplit(href).query), {'q': ['Cloud'], 'category': ['tools']})
        page.go_back(wait_until='networkidle')
        self.assertEqual(urlsplit(page.locator('#language-switch').get_attribute('href')).fragment, '')

    def test_original_links_labels_and_honest_translation_fallback(self):
        page = self.open()
        self.assertEqual(page.locator('.resource a').evaluate_all('(es)=>es.map(e=>e.href)'), [r['url'] for r in self.datasets['en']['resources']])
        self.assertEqual(page.locator('[data-id="editor-two"] h3').get_attribute('lang'), 'ko')
        self.assertIn('Korean original', page.locator('[data-id="editor-two"]').inner_text())
        self.assertNotEqual(page.locator('[data-id="editor-two"] p').get_attribute('lang'), 'ko')
        self.assertTrue(page.locator('#translation-note').is_visible())
        self.assertEqual(page.locator('.label').all_text_contents(), ['KR', 'F', 'EN', 'O'])
        self.assertEqual(page.locator('#source-revision').inner_text(), 'Source fixture')
        korean = self.open('')
        self.assertTrue(korean.locator('#translation-note').is_hidden())

    def test_pending_category_and_description_are_marked_not_translated(self):
        data = copy.deepcopy(self.datasets['en'])
        data['categories'][0].update(name='개발 도구', untranslated=True)
        data['resources'][0].update(description='협업 프로그래밍', untranslatedFields=['description'])
        data['translationStatus'].update(pendingResources=2, pendingCategories=1)
        page = self.browser.new_page(reduced_motion='reduce')
        self.addCleanup(page.close)
        page.route('**/resources.json', lambda route: route.fulfill(json=data))
        page.goto(self.base + 'en/', wait_until='networkidle')
        self.assertEqual(page.locator('[data-category="tools"] .cat-name').get_attribute('lang'), 'ko')
        self.assertEqual(page.locator('[data-id="editor-one"] p').get_attribute('lang'), 'ko')
        self.assertEqual(page.locator('[data-id="editor-one"] .resource-path [lang="ko"]').inner_text(), '개발 도구')
        page.locator('[data-category="tools"]').click()
        self.assertEqual(page.locator('#category-heading').get_attribute('lang'), 'ko')
        page.locator('[data-category=""]').click()
        self.assertEqual(page.locator('#category-heading').get_attribute('lang'), 'en')

    def test_complete_translations_hide_pending_note(self):
        data = copy.deepcopy(self.datasets['en'])
        data['resources'][1].update(name='Local editor', untranslatedFields=[])
        data['translationStatus'] = {'pendingStrings': [], 'pendingResources': 0, 'pendingCategories': 0}
        page = self.browser.new_page(reduced_motion='reduce')
        self.addCleanup(page.close)
        page.route('**/resources.json', lambda route: route.fulfill(json=data))
        page.goto(self.base + 'en/', wait_until='networkidle')
        self.assertTrue(page.locator('#translation-note').is_hidden())
        self.assertEqual(page.locator('.original-badge').count(), 0)
        self.assertEqual(page.locator('#result-count').inner_text(), '2 of 2 resources')
        self.assertEqual(page.locator('[aria-controls="children-tools"]').get_attribute('aria-label'), 'Subcategories of Tools')
        page.locator('#search').fill('Cloud')
        self.assertEqual(page.locator('#filter-summary').inner_text(), 'Results for “Cloud”')

    def test_no_overflow_at_mobile_and_desktop(self):
        for path in ['', 'en/']:
            for width in [320, 390, 1440]:
                page = self.open(path, viewport={'width': width, 'height': 900})
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth===innerWidth'), (path, width))
                self.assertEqual(page.locator('.resource').count(), 2)
                self.assertTrue(page.locator('#language-switch').is_visible())
                page.wait_for_function('!document.querySelector("#gem-poster").hidden')
                self.assertTrue(page.locator('#gem-frame').is_hidden())
                self.assertIsNone(page.locator('#gem-frame').get_attribute('src'))

    def test_no_javascript_keeps_localized_navigation_and_readme(self):
        page = self.open(java_script_enabled=False)
        self.assertIn('Search requires JavaScript.', page.locator('noscript').inner_text())
        self.assertTrue(page.locator('#language-switch').is_visible())
        self.assertEqual(page.locator('.brand').get_attribute('href'), './')
        self.assertEqual(page.locator('footer a[href="../LICENSE"]').inner_text(), 'MIT License')
        page.locator('#language-switch').click()
        self.assertEqual(page.locator('html').get_attribute('lang'), 'ko')
        self.assertIn('검색에는 JavaScript가 필요합니다.', page.locator('noscript').inner_text())

    def test_english_scene_uses_root_asset_and_fallback(self):
        page = self.browser.new_page()
        self.addCleanup(page.close)
        page.goto(self.base + 'en/', wait_until='networkidle')
        page.wait_for_function('document.querySelector("#gem-frame").getAttribute("src")')
        self.assertEqual(page.locator('#gem-frame').get_attribute('src'), '../art/scene.html')
        page.wait_for_function('(()=>{let f=document.querySelector("#gem-frame");return f.contentWindow?.__GEM_READY__||f.contentWindow?.__GEM_ERROR__})()')
        ready = page.locator('#gem-frame').evaluate('(e)=>!!e.contentWindow.__GEM_READY__')
        if ready:
            page.wait_for_function('!document.querySelector("#gem-frame").hidden')
        else:
            self.assertTrue(page.locator('#gem-poster').is_visible())
            self.assertTrue(page.locator('#gem-frame').is_hidden())

    def test_localized_load_failure_and_switch_without_dataset(self):
        page = self.browser.new_page(reduced_motion='reduce')
        self.addCleanup(page.close)
        page.route('**/resources.json', lambda route: route.fulfill(status=503, body='unavailable'))
        page.goto(self.base + 'en/?q=구름&category=editors#directory', wait_until='networkidle')
        self.assertTrue(page.locator('#load-error').is_visible())
        self.assertIn('Unable to load', page.locator('#result-count').inner_text())
        self.assertIn('README', page.locator('#load-error').inner_text())
        self.assertIn('q=', page.locator('#language-switch').get_attribute('href'))
        page.locator('#language-switch').click()
        self.assertEqual(page.locator('html').get_attribute('lang'), 'ko')
        self.assertIn('불러오지 못했습니다', page.locator('#result-count').inner_text())


class LocaleBuildIntegrationTests(unittest.TestCase):
    def test_actual_builder_serves_english_at_project_prefix(self):
        with tempfile.TemporaryDirectory(prefix='sfd-built-locales-') as tmp:
            site = Path(tmp) / 'site'
            subprocess.run(['python3', str(ROOT / 'scripts/build_site.py'), '--output', str(site), '--revision', 'locale-browser-test'], cwd=ROOT, check=True, capture_output=True, text=True)
            self.assertTrue((site / 'en/index.html').exists(), 'Builder must publish /en/')
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch()
                    try:
                        page = browser.new_page(reduced_motion='reduce')
                        page.goto(f'http://127.0.0.1:{server.server_port}' + PREFIX + 'en/?q=Cursor#directory', wait_until='networkidle')
                        self.assertEqual(page.locator('html').get_attribute('lang'), 'en')
                        self.assertGreater(page.locator('.resource').count(), 0)
                        self.assertEqual(page.locator('#search').input_value(), 'Cursor')
                        self.assertNotIn('{{', page.content())
                        page.locator('#language-switch').click()
                        self.assertEqual(page.locator('html').get_attribute('lang'), 'ko')
                        self.assertGreater(page.locator('.resource').count(), 0)
                        self.assertIn('#directory', page.url)
                        base = f'http://127.0.0.1:{server.server_port}' + PREFIX
                        for locale, suffix in [('ko', ''), ('en', 'en/')]:
                            data = json.loads((site / suffix / 'resources.json').read_text())
                            for width in [320, 390, 1440]:
                                page.set_viewport_size({'width': width, 'height': 900})
                                page.goto(base + suffix, wait_until='networkidle')
                                self.assertTrue(page.evaluate('document.documentElement.scrollWidth===innerWidth'), (locale, width))
                                self.assertEqual(page.locator('.resource').count(), len(data['resources']))
                                self.assertEqual(page.locator('.resource a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'), [r['url'] for r in data['resources']])
                            page.locator('#search').fill('Cursor')
                            self.assertGreater(page.locator('.resource').count(), 0)
                            original = next(r.get('originalDescription', r['description']) for r in data['resources'] if re.search('[가-힣]', r.get('originalDescription', r['description'])))
                            page.locator('#search').fill(original)
                            self.assertGreater(page.locator('.resource').count(), 0)
                            page.reload(wait_until='networkidle')
                            self.assertGreater(page.locator('.resource').count(), 0)
                    finally:
                        browser.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == '__main__':
    unittest.main(verbosity=2)
