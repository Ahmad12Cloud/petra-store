#!/usr/bin/env python3
"""Petra Power short links: builds /p/<CODE>/index.html for every active product.

Each page carries the product name, short description and photo (so WhatsApp /
Facebook show a branded preview card) and forwards the visitor to the store,
which opens that product.  Run by .github/workflows/build.yml (hourly + manual).
"""
import html, json, os, re, shutil, sys, urllib.request

SB_URL = "https://akkshuvvgjqkattbxvvk.supabase.co"
SB_KEY = os.environ.get("SB_ANON_KEY", "").strip()
STORE = "https://petrapowerstore.com/shop/"
SITE = "https://petrapowerstore.com"
BRAND = "Petra Power Energy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = SITE + "/icon-512.png"


def get(url, headers=None, method="GET"):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def products():
    if not SB_KEY:
        sys.exit("SB_ANON_KEY missing")
    out, off = [], 0
    while True:
        url = (SB_URL + "/rest/v1/products?select=code,name_ar,name_en,description_ar,images,active"
               "&active=eq.true&order=code.asc&limit=1000&offset=%d" % off)
        _, b = get(url, {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY})
        rows = json.loads(b)
        out += rows
        if len(rows) < 1000:
            return out
        off += 1000


def clean(t, n):
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = re.sub(r"\s+", " ", t).strip()
    return (t[: n - 1] + "…") if len(t) > n else t


def image_for(p):
    imgs = [x for x in (p.get("images") or []) if isinstance(x, str) and x.startswith("https://")]
    if not imgs:
        return LOGO
    full = imgs[0]
    if "/storage/v1/object/public/product-images/" in full:
        try:
            st, _ = get(full + ".t.webp", method="HEAD")
            if st == 200:
                return full + ".t.webp"
        except Exception:
            pass
    return full


PAGE = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {brand}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="{brand}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{target}">
<link rel="icon" href="/icon-192.png">
<meta http-equiv="refresh" content="0;url={target}">
<script>(function(){{var t={target_js};if(/[?&]ref=s(&|$)/.test(location.search))t+="&ref=s";location.replace(t);}})();</script>
<style>body{{margin:0;font-family:system-ui,Tahoma,sans-serif;background:#111;color:#f5c542;display:grid;place-items:center;min-height:100vh;text-align:center}}a{{color:#f5c542}}img{{width:120px}}</style>
</head><body><div><img src="/icon-192.png" alt="{brand}"><p>{title}</p><p><a href="{target}">فتح المنتج في متجر {brand}</a></p></div></body></html>
"""


def main():
    rows = products()
    pdir = os.path.join(ROOT, "p")
    shutil.rmtree(pdir, ignore_errors=True)
    n = 0
    for p in rows:
        code = (p.get("code") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{2,40}", code):
            continue
        title = clean(p.get("name_ar") or p.get("name_en") or code, 110)
        desc = clean(p.get("description_ar") or "", 180) or BRAND
        target = STORE + "?p=" + code + "&src=link"
        d = os.path.join(pdir, code)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(PAGE.format(title=html.escape(title), desc=html.escape(desc), brand=BRAND,
                                img=html.escape(image_for(p)), url=SITE + "/p/" + code,
                                target=html.escape(target), target_js=json.dumps(target)))
        n += 1
    print("built", n, "product links")


if __name__ == "__main__":
    main()
