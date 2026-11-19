#!/usr/bin/env python3
"""Bump the store version everywhere (PETRA_APP_VERSION, pp-app-version meta, version.json) so the V181 auto-updater sees it.
Usage: python3 tools/bump_version.py V182"""
import re, sys, pathlib
new = sys.argv[1]
root = pathlib.Path(__file__).resolve().parent.parent
for d in ['shop', 'admin']:
    f = root / d / 'index.html'
    s = f.read_text(encoding='utf-8')
    s = re.sub(r"const PETRA_APP_VERSION='V\d+'", f"const PETRA_APP_VERSION='{new}'", s, count=1)
    s = re.sub(r'<meta name="pp-app-version" content="V\d+">', f'<meta name="pp-app-version" content="{new}">', s, count=1)
    f.write_text(s, encoding='utf-8')
    (root / d / 'version.json').write_text('{"v":"%s"}\n' % new)
print('bumped to', new)
