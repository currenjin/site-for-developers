"""Real-build crawler/no-JS and hydration contracts (no network dependencies)."""
import json
import sys
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright
from test_locale_browser import Handler, PREFIX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import build, SITE_URL


class StaticSEOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='sfd-seo-')
        cls.site = Path(cls.temp.name) / 'site'
        build(cls.site, 'seo-test')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(cls.site)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}' + PREFIX
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(); cls.temp.cleanup()

    def page(self, **kwargs):
        page = self.browser.new_page(reduced_motion='reduce', **kwargs)
        self.addCleanup(page.close)
        return page

    def test_no_js_has_every_localized_card_and_exact_original_links_labels(self):
        for suffix in ('', 'en/'):
            data = json.loads((self.site / suffix / 'resources.json').read_text())
            page = self.page(java_script_enabled=False)
            page.goto(self.base + suffix)
            self.assertEqual(page.locator('.resource').count(), len(data['resources']))
            self.assertEqual(page.locator('.resource').evaluate_all('(es)=>es.map(e=>e.dataset.id)'), [r['id'] for r in data['resources']])
            self.assertEqual(page.locator('.resource a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'), [r['url'] for r in data['resources']])
            self.assertEqual(page.locator('.resource h3').all_text_contents(), [r['name'] for r in data['resources']])
            self.assertEqual(page.locator('.resource a > p').all_text_contents(), [r['description'] for r in data['resources'] if r['description']])
            self.assertTrue(page.locator('.resource').first.is_visible())
            self.assertTrue(page.locator('.resource').last.is_visible())
            self.assertEqual(page.locator('.label').all_text_contents(), [label for r in data['resources'] for label in r['labels']])
            categories = {c['id']: c for c in data['categories']}
            self.assertEqual(page.locator('.resource-path').all_text_contents(), [' / '.join(categories[c]['name'] for c in r['categoryPath']) for r in data['resources']])
            self.assertEqual(page.locator('#result-count').inner_text(), data['ui']['result_count'].format(count=len(data['resources']), total=len(data['resources'])))
            self.assertEqual(page.locator('#category-total').inner_text(), str(len(data['categories'])))

    def test_hydration_reuses_initial_cards_then_search_reset_and_failure_preserve_list(self):
        for suffix in ('', 'en/'):
            data = json.loads((self.site / suffix / 'resources.json').read_text())
            page = self.page()
            page.route('**/resources.json', lambda route: route.fulfill(status=503, body='unavailable'))
            page.goto(self.base + suffix, wait_until='networkidle')
            self.assertEqual(page.locator('.resource').count(), len(data['resources']))
            self.assertTrue(page.locator('#load-error').is_visible())
            self.assertNotIn('Unable to load', page.locator('#result-count').inner_text())
            page.unroute('**/resources.json')
            page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{window.initialCard=document.querySelector('.resource')})")
            page.reload(wait_until='networkidle')
            self.assertTrue(page.evaluate("window.initialCard===document.querySelector('.resource')"))
            self.assertEqual(page.locator('.resource').count(), len(data['resources']))
            page.locator('#search').fill('Cursor')
            self.assertGreater(page.locator('.resource').count(), 0)
            page.locator('#reset').click()
            self.assertEqual(page.locator('.resource').count(), len(data['resources']))
            self.assertEqual(page.locator('.resource').evaluate_all('(es)=>new Set(es.map(e=>e.dataset.id)).size'), len(data['resources']))
            self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), SITE_URL + suffix)

    def test_injected_markup_is_text_and_pending_fields_are_marked(self):
        from static_render import render_cards, structured_data
        data = {'locale': 'en', 'ui': {'korean_original': 'Korean original'},
                'categories': [{'id': 'c', 'name': '원문 <cat>', 'untranslated': True}],
                'resources': [{'id': 'id\"<>', 'name': '</script><img src=x onerror=alert(1)>',
                               'description': '원문 & <b>', 'url': 'https://example.com/?a=1&b=2',
                               'categoryPath': ['c'], 'labels': ['<F>'],
                               'untranslatedFields': ['name', 'description']}]}
        page = self.page(java_script_enabled=False)
        page.set_content('<div id="results">' + render_cards(data) + '</div>')
        self.assertEqual(page.locator('img, b, script').count(), 0)
        self.assertEqual(page.locator('h3').inner_text(), data['resources'][0]['name'])
        self.assertEqual(page.locator('h3').get_attribute('lang'), 'ko')
        self.assertEqual(page.locator('.resource p').get_attribute('lang'), 'ko')
        self.assertEqual(page.locator('.resource-path [lang="ko"]').inner_text(), '원문 <cat>')
        self.assertEqual(page.locator('.original-badge').inner_text(), 'Korean original')
        hostile = '</script><script>alert(1)</script>\u2028\u2029&'
        encoded = structured_data('en', SITE_URL, hostile, hostile)
        self.assertNotIn('<', encoded); self.assertNotIn('&', encoded)
        self.assertNotIn('\u2028', encoded); self.assertNotIn('\u2029', encoded)
        self.assertIn(hostile, [n.get('name') for n in json.loads(encoded)['@graph']])

    def test_structured_data_canonical_sitemap_and_404(self):
        for suffix, locale in (('', 'ko'), ('en/', 'en')):
            page = self.page(java_script_enabled=False)
            page.goto(self.base + suffix)
            graph = json.loads(page.locator('script[type="application/ld+json"]').text_content())['@graph']
            website = next(n for n in graph if n['@type'] == 'WebSite')
            collection = next(n for n in graph if n['@type'] == 'CollectionPage')
            self.assertEqual(website['url'], SITE_URL)
            self.assertEqual(collection['url'], SITE_URL + suffix)
            self.assertEqual(collection['inLanguage'], locale)
            self.assertNotIn('SearchAction', json.dumps(graph))
            self.assertNotIn('aggregateRating', json.dumps(graph))
            self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), SITE_URL + suffix)
            self.assertEqual(page.locator('link[hreflang="ko"]').get_attribute('href'), SITE_URL)
            self.assertEqual(page.locator('link[hreflang="en"]').get_attribute('href'), SITE_URL + 'en/')
            self.assertIn('AI', page.title())
        sitemap = ET.parse(self.site / 'sitemap.xml')
        self.assertEqual([n.text for n in sitemap.findall('.//{*}loc')], [SITE_URL, SITE_URL + 'en/'])
        self.assertEqual(sitemap.findall('.//{*}lastmod'), [])
        self.assertIn('noindex', (self.site / '404.html').read_text())


if __name__ == '__main__':
    unittest.main()
