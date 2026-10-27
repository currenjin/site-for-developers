"""Publication boundary and deterministic README build regressions."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

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
            self.run_build(dest);self.assertEqual(first,(dest/'resources.json').read_bytes())
    def test_public_allowlist_and_approved_brand(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'site';self.run_build(dest)
            actual={str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(actual,{'index.html','styles.css','app.js','logo.svg','resources.json','LICENSE','.nojekyll','404.html','sitemap.xml','art/scene.html','art/poster.png','art/three.min.js','art/THREE-LICENSE.txt'})
            self.assertEqual((dest/'logo.svg').read_bytes(),(ROOT/'resources/icons/header_base/576x157/header_base.svg').read_bytes())
            html=(dest/'index.html').read_text()
            self.assertNotIn('noindex',html);self.assertNotIn('비공개 미리보기',html)
            self.assertIn('https://currenjin.github.io/site-for-developers/',html)
    def test_unknown_output_is_not_erased(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp);(dest/'unrelated.txt').write_text('keep')
            result=subprocess.run(['python3',str(ROOT/'scripts/build_site.py'),'--output',str(dest)],cwd=ROOT,capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((dest/'unrelated.txt').read_text(),'keep')

if __name__=='__main__':unittest.main(verbosity=2)
