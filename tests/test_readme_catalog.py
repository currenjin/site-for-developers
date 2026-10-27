import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from readme_catalog import parse_readme, safe_url

class ParserTests(unittest.TestCase):
    def test_nested_unicode_labels_aliases_and_balanced_url(self):
        text='''# ignored
- [nav](https://ignore.test)
## 링크
- <span id="root">도구 &amp; 문서</span>
  - <span id="old"></span><span id="child">IDE</span>
    - [**도구 [A]** <sub>KR, F</sub>](https://example.org/a_(b)?x=1&y=2) - 설명 <책 이름> &amp; `code`
    - [도구](https://example.org/a_(b)?x=1&y=2)
## 기여
- [not resource](https://ignore.test)
'''
        d=parse_readme(text)
        self.assertEqual(len(d['resources']),2)
        r=d['resources'][0]
        self.assertEqual(r['name'],'도구 [A]')
        self.assertEqual(r['labels'],['KR','F'])
        self.assertEqual(r['description'],'설명 <책 이름> & code')
        self.assertEqual(r['url'],'https://example.org/a_(b)?x=1&y=2')
        self.assertEqual(r['categoryPath'],['root','child'])
        self.assertEqual(d['categories'][1]['aliases'],['old'])
        self.assertNotEqual(r['id'],d['resources'][1]['id'])
        self.assertEqual(d,parse_readme(text))
    def test_rejects_unsafe_urls(self):
        for u in ['javascript:alert(1)','data:text/html,x','//evil.test','https://a.test/\nfoo','https://','https://user:secret@example.org','https://:secret@example.org']:
            self.assertFalse(safe_url(u))
        with self.assertRaises(ValueError):
            parse_readme('## 링크\n- <span id="x">X</span>\n  - [bad](javascript:alert(1))')
    def test_literal_angle_titles_not_eaten(self):
        d=parse_readme('## 링크\n- <span id="x">X</span>\n  - [A](https://a.test) - <The Site Reliability Workbook> by A')
        self.assertEqual(d['resources'][0]['description'],'<The Site Reliability Workbook> by A')
    def test_source_coverage_and_taxonomy(self):
        text=Path(__file__).resolve().parents[1].joinpath('README.md').read_text()
        d=parse_readme(text)
        source=text.split('## 링크',1)[1].split('\n## ',1)[0]
        import re
        expected=re.findall(r'^\s*- \[.*?\]\((https?://.*?)\)',source,re.M)
        self.assertEqual(len(d['resources']),len(expected))
        self.assertEqual([r['url'] for r in d['resources']],expected)
        self.assertEqual(len(set(r['id'] for r in d['resources'])),len(expected))
        self.assertEqual(next(c for c in d['categories'] if c['id']=='development-infra')['aliases'],['ai-infra'])
        self.assertEqual(next(r for r in d['resources'] if r['name']=='IntelliJ IDEA')['categoryPath'],['tool','ide','jetbrains'])
        self.assertTrue(all(r['categoryPath'] for r in d['resources']))
    def test_stable_ids_across_unrelated_insertions(self):
        base='## 링크\n- <span id="x">X</span>\n  - [A](https://a.test) - a\n  - [A](https://a.test) - a'
        a=parse_readme(base)['resources']
        b=parse_readme(base.replace('  - [A]','  - [B](https://b.test)\n  - [A]',1))['resources']
        self.assertEqual([r['id'] for r in a],[r['id'] for r in b if r['name']=='A'])

if __name__=='__main__': unittest.main(verbosity=2)
