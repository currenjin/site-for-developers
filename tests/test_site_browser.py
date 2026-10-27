"""Exercise the actual Pages artifact under its project URL prefix."""
import json
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
PREFIX='/site-for-developers/'
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if not path.startswith(PREFIX):return str(SITE/'__not_found__')
        return super().translate_path('/'+path[len(PREFIX):])
    def log_message(self, format, *args):pass

class SiteBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((SITE/'resources.json').read_text())
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(SITE)))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'+PREFIX
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch()
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def open_page(self,**kwargs):
        page=self.browser.new_page(**kwargs);page.goto(self.base,wait_until='networkidle');page.wait_for_function('document.querySelectorAll(".resource").length>0');self.addCleanup(page.close);return page
    def test_all_rows_and_responsive_layout(self):
        for width in [320,390,1440]:
            with self.subTest(width=width):
                page=self.open_page(viewport={'width':width,'height':900},reduced_motion='reduce')
                self.assertEqual(page.locator('.resource').count(),len(self.data['resources']))
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth===innerWidth'))
                actual=page.locator('.resource a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))')
                self.assertEqual(actual,[r['url'] for r in self.data['resources']])
    def test_search_categories_url_reload_and_reset(self):
        page=self.open_page(reduced_motion='reduce');page.locator('#search').fill('Cursor')
        self.assertGreater(page.locator('.resource').count(),0);self.assertIn('q=Cursor',page.url)
        count=page.locator('.resource').count();page.reload(wait_until='networkidle');self.assertEqual(page.locator('.resource').count(),count)
        page.locator('#search').fill('');page.locator('[data-category="recommend"]').click()
        expected=sum('recommend' in r['categoryPath'] for r in self.data['resources'])
        self.assertEqual(page.locator('.resource').count(),expected);self.assertIn('category=recommend',page.url)
        page.locator('#search').fill('unlikely-no-result-571392');self.assertTrue(page.locator('#empty').is_visible())
        page.locator('#reset').click();self.assertEqual(page.locator('.resource').count(),len(self.data['resources']))
    def test_reduced_motion_uses_poster_without_webgl(self):
        page=self.open_page(reduced_motion='reduce');page.wait_for_function('!document.querySelector("#gem-poster").hidden')
        self.assertIsNone(page.locator('#gem-frame').get_attribute('src'));self.assertTrue(page.locator('#gem-frame').is_hidden())
        self.assertGreater(page.locator('#gem-poster').evaluate('(e)=>e.naturalWidth'),0)
    def test_live_scene_loads_or_keeps_verified_fallback(self):
        page=self.open_page(viewport={'width':1440,'height':1000});page.wait_for_function('!document.querySelector("#gem-poster").hidden')
        page.wait_for_function('(()=>{let f=document.querySelector("#gem-frame");return f.contentWindow?.__GEM_READY__||f.contentWindow?.__GEM_ERROR__})()')
        frame=page.locator('#gem-frame')
        info=frame.evaluate('(e)=>({ready:!!e.contentWindow.__GEM_READY__,error:e.contentWindow.__GEM_ERROR__||null})')
        if info['ready']:
            page.wait_for_function('!document.querySelector("#gem-frame").hidden')
            self.assertTrue(frame.is_visible())
        else:
            self.assertTrue(frame.is_hidden());self.assertTrue(page.locator('#gem-poster').is_visible())
    def test_catalogue_failure_is_actionable(self):
        page=self.browser.new_page(reduced_motion='reduce');self.addCleanup(page.close)
        page.route('**/resources.json',lambda route:route.fulfill(status=503,body='unavailable'))
        page.goto(self.base);page.wait_for_function('!document.querySelector("#load-error").hidden')
        self.assertIn('README',page.locator('#load-error').inner_text())
    def test_safe_text_and_no_script_urls(self):
        page=self.browser.new_page(reduced_motion='reduce');self.addCleanup(page.close)
        data=json.loads(json.dumps(self.data));data['resources'].append({**data['resources'][0],'name':'<img src=x onerror="window.BAD=true">','id':'safe-text','url':'https://example.test/'})
        data['resources'].append({**data['resources'][0],'name':'unsafe','id':'unsafe','url':'javascript:alert(1)'})
        page.route('**/resources.json',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(data)))
        page.goto(self.base,wait_until='networkidle');page.wait_for_function('document.querySelectorAll(".resource").length>0')
        self.assertEqual(page.locator('[data-id="safe-text"] img').count(),0);self.assertIn('<img',page.locator('[data-id="safe-text"]').inner_text());self.assertEqual(page.locator('[data-id="unsafe"]').count(),0)
        self.assertFalse(page.evaluate('!!window.BAD'))

if __name__=='__main__':unittest.main(verbosity=2)
