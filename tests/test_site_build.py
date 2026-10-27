"""Publication boundary and deterministic README build regressions."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from readme_catalog import parse_readme

class SiteBuildTests(unittest.TestCase):
    def run_build(self, output):
        subprocess.run(['python3',str(ROOT/'scripts/build_site.py'),'--output',str(output),'--revision','fixture-revision'],check=True,cwd=ROOT,capture_output=True,text=True)
    def test_complete_readme_data_and_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'site';self.run_build(dest)
            first=(dest/'resources.json').read_bytes();data=json.loads(first)
            self.assertEqual(data['source']['commit'],'fixture-revision')
            self.assertTrue(data['resources']);self.assertTrue(data['categories'])
            self.assertEqual(data['source']['readme'],'https://github.com/currenjin/site-for-developers/blob/fixture-revision/README.md')
            english=json.loads((dest/'en/resources.json').read_text())
            self.assertEqual(data['locale'],'ko');self.assertEqual(english['locale'],'en')
            self.assertEqual(len(data['resources']),len(english['resources']))
            self.assertEqual(len(data['categories']),len(english['categories']))
            source=parse_readme((ROOT/'README.md').read_text())
            for actual,expected in zip(data['resources'],source['resources']):
                for key,value in expected.items():self.assertEqual(actual[key],value)
            for actual,expected in zip(data['categories'],source['categories']):
                for key,value in expected.items():self.assertEqual(actual[key],value)
            for actual,expected in zip(english['resources'],source['resources']):
                for key in ('id','url','labels','labelSource','categoryPath','sourceLine'):
                    self.assertEqual(actual[key],expected[key])
            snapshot={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()}
            self.run_build(dest)
            self.assertEqual(snapshot,{str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()})
    def test_public_allowlist_and_approved_brand(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'site';self.run_build(dest)
            actual={str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(actual,{'index.html','styles.css','app.js','logo.svg','favicon.svg','resources.json','LICENSE','.nojekyll','404.html','sitemap.xml','art/scene.html','art/poster.png','art/three.min.js','art/THREE-LICENSE.txt','en/index.html','en/resources.json'})
            self.assertEqual((dest/'logo.svg').read_bytes(),(ROOT/'resources/icons/header_base/576x157/header_base.svg').read_bytes())
            html=(dest/'index.html').read_text()
            self.assertNotIn('noindex',html);self.assertNotIn('비공개 미리보기',html)
            self.assertIn('https://currenjin.github.io/site-for-developers/',html)
    def test_favicon_is_original_gem_without_wordmark(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'site';self.run_build(dest)
            ns='{http://www.w3.org/2000/svg}'
            icon=ET.parse(dest/'favicon.svg').getroot()
            original=ET.parse(ROOT/'resources/icons/header_base/576x157/header_base.svg').getroot()
            paths=icon.findall(ns+'path')
            self.assertEqual(len(paths),1)
            self.assertEqual(paths[0].attrib,original.findall(ns+'path')[1].attrib)
            self.assertEqual(icon.get('viewBox'),'22 12 128 128')
            self.assertEqual(len(icon.findall('.//'+ns+'text')),0)
            self.assertIn('href="favicon.svg"',(dest/'index.html').read_text())
            self.assertEqual((dest/'logo.svg').read_bytes(),(ROOT/'resources/icons/header_base/576x157/header_base.svg').read_bytes())

    def test_unknown_output_is_not_erased(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp);(dest/'unrelated.txt').write_text('keep')
            result=subprocess.run(['python3',str(ROOT/'scripts/build_site.py'),'--output',str(dest)],cwd=ROOT,capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((dest/'unrelated.txt').read_text(),'keep')

if __name__=='__main__':unittest.main(verbosity=2)
