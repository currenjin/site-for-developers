"""Real build regressions for the refined hero and GitHub Star CTA."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_site

class StarCallToActionTests(unittest.TestCase):
    def test_compact_stars(self):
        import github_stats
        for count,label in [(0,'0'),(999,'999'),(1000,'1k'),(1179,'1.2k'),(1250,'1.3k'),(1000000,'1m')]:
            with self.subTest(count=count):self.assertEqual(github_stats.compact_stars(count),label)
        for count in [-1,True,'1179',None]:
            with self.assertRaises(ValueError):github_stats.compact_stars(count)
    def test_stats_snapshot_is_build_only_and_localized_cta_is_real_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'site';build_site.build(out,'stars-test')
            for path in ['index.html','en/index.html']:
                text=(out/path).read_text()
                self.assertNotIn('class="hero-note"',text)
                self.assertNotIn('class="art-caption"',text)
                self.assertIn('id="github-star-button"',text)
                self.assertIn('id="github-star-count"',text)
                self.assertIn('href="https://github.com/currenjin/site-for-developers"',text)
                import github_stats
                self.assertIn(github_stats.compact_stars(github_stats.read_snapshot(ROOT/'web/github.json')),text)
            self.assertFalse((out/'github.json').exists())
    def test_stats_http_payload_is_validated(self):
        import github_stats
        for data in [{'stargazers_count':-1},{'stargazers_count':True},{'stars':1179}]:
            with self.assertRaises(ValueError):github_stats.validate_payload(data)
        self.assertEqual(github_stats.validate_payload({'stargazers_count':1179}),1179)
    def test_network_failure_retains_last_verified_snapshot(self):
        import github_stats
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'github.json';before='{"stars":1179,"fetchedAt":"fixture"}\n';target.write_text(before)
            with patch('github_stats.fetch_stars',side_effect=OSError('unavailable')):
                self.assertFalse(github_stats.update_snapshot(target))
            self.assertEqual(target.read_text(),before)
    def test_network_success_updates_snapshot_with_actual_number(self):
        import github_stats
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'github.json'
            with patch('github_stats.fetch_stars',return_value=1182):self.assertTrue(github_stats.update_snapshot(target))
            data=json.loads(target.read_text());self.assertEqual(data['stars'],1182);self.assertTrue(data['fetchedAt'])

if __name__=='__main__':unittest.main(verbosity=2)
