"""Report current exact-source English translation misses without network access."""
import argparse
import json
from pathlib import Path
from readme_catalog import parse_readme
from site_i18n import load_translations, translation_status

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT,
                        help='Repository root (defaults to this checkout)')
    parser.add_argument('--check', action='store_true',
                        help='Exit nonzero when translations are pending; normal builds do not require this')
    args = parser.parse_args(argv)
    data = parse_readme((args.root / 'README.md').read_text(encoding='utf-8'))
    cache = load_translations(args.root / 'web/i18n/en.json')
    status = translation_status(data, cache)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 1 if args.check and status['pendingStrings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
