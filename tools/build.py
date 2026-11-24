#!/usr/bin/env python3
"""Petra Power product pages + sitemap.

Builds /p/<CODE>/index.html for every active product: a real, readable page
(name, price, sizes, full description, photos, WhatsApp order buttons) that
Google can index, with Product structured data.  Also writes /sitemap.xml.
WhatsApp/Facebook previews keep working through the og: tags.
Run by .github/workflows/links.yml (hourly + manual).
"""
import html, json, os, re, shutil, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

SB_URL = "https://akkshuvvgjqkattbxvvk.supabase.co"
SB_KEY = os.environ.get("SB_ANON_KEY", "").strip()
STORE = "https://petrapowerstore.com/shop/"
SITE = "https://petrapowerstore.com"
BRAND = "Petra Power Energy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = SITE + "/icon-512.png"
DEFAULT_CONTACTS = [{"name": "فرع لبنان", "phone": "+961 76 685 783", "where": {"elec": True}},
                    {"name": "فرع سوريا", "phone": "+963 957 320 372", "where": {"elec": True}}]


def get(url, headers=None, method="GET"):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def sb(path):
    _, b = get(SB_URL + "/rest/v1/" + path, {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY})
    return json.loads(b)


def products():
    if not SB_KEY:
        sys.exit("SB_ANON_KEY missing")
    out, off = [], 0
    while True:
        rows = sb("products?select=code,name_ar,name_en,description_ar,description_en,images,active,price,"
                  "category_name,updated_at,extra->priceMax,extra->sizes,extra->sizePrices,extra->sizeLabel,"
                  "extra->department&active=eq.true&order=code.asc&limit=1000&offset=%d" % off)
        out += rows
        if len(rows) < 1000:
            return out
        off += 1000


def contacts():
    try:
        rows = sb("store_settings?select=c:data->pp210Contacts&id=eq.1")
        c = rows[0].get("c") if rows else None
        if isinstance(c, list) and c:
            return c
    except Exception as e:
        print("contacts fallback:", e)
    return DEFAULT_CONTACTS


def clean(t, n):
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = re.sub(r"\s+", " ", t).strip()
    return (t[: n - 1] + "…") if len(t) > n else t


def no_flags(t):
    # regional-indicator flag emoji (the phone 🇸🇾 is the old flag) are dropped
    return re.sub(r"[\U0001F1E6-\U0001F1FF]", "", t or "").strip()


_thumb = {}


def thumb_or_full(full):
    if full in _thumb:
        return _thumb[full]
    res = full
    if "/storage/v1/object/public/product-images/" in full:
        try:
            st, _ = get(full + ".t.webp", method="HEAD")
            if st == 200:
                res = full + ".t.webp"
        except Exception:
            pass
    _thumb[full] = res
    return res


def imgs_of(p):
    return [x for x in (p.get("images") or []) if isinstance(x, str) and x.startswith("https://")]


def money(v):
    try:
        n = float(v)
    except (TypeError, ValueError):
        return ""
    if n <= 0:
        return ""
    return ("%.2f" % n) if round(n * 100) % 100 else ("%d" % round(n))


def is_ac(p):
    if (p.get("department") or "") == "ac" or (p.get("code") or "").upper().startswith("MK-"):
        return True
    cat = p.get("category_name") or ""
    return "مكيف" in cat or "المكيفات" in cat


def desc_html(t):
    out, ul = [], []

    def flush():
        if ul:
            out.append("<ul>" + "".join("<li>%s</li>" % x for x in ul) + "</ul>")
            ul.clear()
    for raw in (t or "").split("\n"):
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("- "):
            ul.append(html.escape(line[2:]))
            continue
        flush()
        if line.endswith(":") and len(line) < 60:
            out.append("<h3>%s</h3>" % html.escape(line[:-1]))
        else:
            out.append("<p>%s</p>" % html.escape(line))
    flush()
    return "\n".join(out)


def brand_of(p):
    m = re.search(r"\(Brand\)\s*:\s*([^\n]+)", p.get("description_ar") or "") or \
        re.search(r"Brand:\s*([^\n]+)", p.get("description_en") or "")
    return m.group(1).strip() if m else ""


CSS = """*{box-sizing:border-box}body{margin:0;font-family:Tahoma,Arial,sans-serif;background:#f6f2e8;color:#1b1b1b;line-height:1.7}
a{color:inherit}.top{background:#000;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;position:sticky;top:0;z-index:2}
.brand{display:flex;align-items:center;gap:8px;text-decoration:none}.brand img{width:43px;height:43px}
.bl{display:flex;flex-direction:column;align-items:center;font-family:Arial,sans-serif;font-weight:800;color:#d4af37;text-transform:uppercase;line-height:1.15}
.bl .l1{font-size:16px}.bl .l2{font-size:12px}
.all{background:linear-gradient(#ffd34d,#f29a10);color:#141414;font-weight:800;text-decoration:none;border-radius:12px;padding:7px 12px;font-size:14px}
.wrap{max-width:760px;margin:0 auto;padding:12px}.card{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.08)}
.hero{width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;background:#fff;display:block}
.in{padding:14px 16px}h1{font-size:22px;line-height:1.4;margin:0 0 4px}.en{direction:ltr;text-align:left;color:#666;font-size:14px;margin:0 0 6px}
.price{color:#e07b00;font-size:30px;font-weight:800;direction:ltr;unicode-bidi:isolate;display:inline-block}.ask{color:#555;font-size:18px;font-weight:700}
.contact{margin:12px 0 6px;text-align:center}.contact .lb{display:block;font-size:13px;color:#777;margin-bottom:6px}
.warow{display:flex;justify-content:center;gap:8px;flex-wrap:nowrap}
.wa{display:inline-flex;align-items:center;gap:5px;background:#f0f9f3;border:1px solid #d6eedf;border-radius:20px;padding:5px 12px;font-size:14px;font-weight:700;color:#2c6b45;text-decoration:none;white-space:nowrap}
.more{text-align:center;margin:8px 0 12px}.go{display:inline-flex;align-items:center;gap:6px;background:#fff8e6;border:1px solid #efd9a0;border-radius:22px;padding:7px 16px;font-size:14px;font-weight:700;color:#6b4e00;text-decoration:none}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:15px}td,th{border:1px solid #eee;padding:6px 8px;text-align:center}th{background:#faf6ea}
.d h3{font-size:17px;margin:16px 0 4px;color:#7a5a00}.d p{margin:6px 0}.d ul{margin:4px 0;padding-inline-start:20px}
.gal{display:flex;gap:8px;overflow-x:auto;padding:4px 0}.gal img{height:150px;width:auto;border-radius:12px;background:#fff;border:1px solid #eee}
details{margin-top:14px;background:#faf6ea;border-radius:12px;padding:8px 12px}summary{font-weight:800;cursor:pointer}
details .d{direction:ltr;text-align:left}.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.rel a{background:#fff;border-radius:14px;text-decoration:none;padding:8px;font-size:13px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.rel img{width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;border-radius:10px}h2{font-size:18px;margin:20px 0 8px}
.cat{display:inline-block;background:#fff3cd;border-radius:20px;padding:2px 12px;font-size:13px;margin-bottom:6px;text-decoration:none}
footer{text-align:center;color:#777;font-size:13px;padding:22px 10px}"""

PAGE = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {brand}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="{brand}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ogimg}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
<link rel="icon" href="/icon-192.png">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
</head><body>
<header class="top"><a class="brand" href="{store}" aria-label="{brand}"><img src="/pe-logo.webp" alt="{brand}" width="43" height="43"><span class="bl"><span class="l1">Petrapower</span><span class="l2">Energy</span></span></a><a class="all" href="{store}">🛒 كل المنتجات</a></header>
<main class="wrap"><article class="card">
<img class="hero" src="{img}" alt="{title_attr}" width="800" height="800">
<div class="in">
{catlink}<h1>{title}</h1>
{en}
{price}
{wa}<div class="more"><a class="go" href="{target}">🛒 اكتشف منتجات أكثر</a></div>
{sizes}
<div class="d">{body}</div>
{gallery}
{endesc}
</div></article>
{related}
</main>
<footer>{brand} · بيروت – لبنان · دمشق – سوريا<br><a href="{store}">petrapowerstore.com</a></footer>
</body></html>
"""


def build_page(p, by_cat, contact_list):
    code = p["code"]
    url = SITE + "/p/" + code + "/"
    target = STORE + "?p=" + code + "&src=link"
    name = clean(p.get("name_ar") or p.get("name_en") or code, 140)
    name_en = clean(p.get("name_en") or "", 160)
    desc = clean(p.get("description_ar") or "", 180) or BRAND
    imgs = imgs_of(p)
    hero = imgs[0] if imgs else LOGO
    og = thumb_or_full(hero) if imgs else LOGO
    lo = money(p.get("price"))
    hi = money(p.get("priceMax"))
    if lo and hi and hi != lo:
        price = '<div class="price">%s – %s $</div>' % (lo, hi)
    elif lo:
        price = '<div class="price">%s $</div>' % lo
    else:
        price = '<div class="ask">السعر عند الطلب</div>'
    # sizes
    sizes_html = ""
    sizes = p.get("sizes") or []
    sp = p.get("sizePrices") or {}
    if isinstance(sizes, list) and len(sizes) > 1:
        label = html.escape(p.get("sizeLabel") or "القياس")
        rows = []
        for s in sizes:
            v = money(sp.get(s)) if isinstance(sp, dict) else ""
            rows.append("<tr><td dir=\"ltr\">%s</td><td dir=\"ltr\">%s</td></tr>" % (html.escape(str(s)), (v + " $") if v else "—"))
        sizes_html = "<table><tr><th>%s</th><th>السعر</th></tr>%s</table>" % (label, "".join(rows))
    # whatsapp
    ac = is_ac(p)
    msg = "مرحبا، بدي استفسر عن: %s (%s)\n%s" % (name, code, url)
    wa = []
    for c in contact_list:
        w = c.get("where") or {}
        if (ac and not w.get("ac")) or ((not ac) and not w.get("elec")):
            continue
        num = re.sub(r"\D", "", c.get("phone") or "")
        if not num:
            continue
        label = re.sub(r"^(فرع|قسم)\s+", "", no_flags(c.get("name") or ""))
        wa.append('<a class="wa" href="https://wa.me/%s?text=%s"><svg viewBox="0 0 32 32" width="17" height="17" aria-hidden="true"><path fill="#25D366" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3z"/><path fill="#fff" d="M23.3 19.2c-.4-.2-2.3-1.1-2.6-1.2-.4-.1-.6-.2-.9.2-.3.4-1 1.2-1.2 1.4-.2.2-.4.3-.8.1-.4-.2-1.6-.6-3-1.9-1.1-1-1.9-2.2-2.1-2.6-.2-.4 0-.6.2-.8l.6-.7c.2-.2.3-.4.4-.7.1-.3 0-.5 0-.7l-1.2-2.8c-.3-.7-.6-.6-.9-.6h-.7c-.3 0-.7.1-1 .5-.4.4-1.4 1.3-1.4 3.2s1.4 3.7 1.6 4c.2.3 2.8 4.2 6.7 5.9 2.5 1 3.4 1.1 4.6.9.7-.1 2.3-.9 2.6-1.8.3-.9.3-1.7.2-1.8-.1-.2-.4-.3-.8-.5z"/></svg> %s</a>' % (
            num, urllib.parse.quote(msg), html.escape(label)))
    gal = ""
    if len(imgs) > 1:
        gal = '<div class="gal">' + "".join('<img src="%s" alt="%s" loading="lazy">' % (html.escape(u), html.escape(name)) for u in imgs[1:]) + "</div>"
    endesc = ""
    if (p.get("description_en") or "").strip():
        endesc = '<details><summary>English</summary><div class="d">%s</div></details>' % desc_html(p["description_en"])
    cat = p.get("category_name") or ""
    catlink = ('<a class="cat" href="%s">%s</a>' % (html.escape(STORE), html.escape(cat))) if cat else ""
    rel = [q for q in by_cat.get(cat, []) if q["code"] != code][:6] if cat else []
    related = ""
    if rel:
        related = "<h2>منتجات من نفس القسم</h2><div class=\"rel\">" + "".join(
            '<a href="/p/%s/"><img src="%s" alt="%s">%s</a>' % (
                html.escape(q["code"]), html.escape(thumb_or_full(imgs_of(q)[0]) if imgs_of(q) else LOGO),
                html.escape(clean(q.get("name_ar") or q["code"], 110)), html.escape(clean(q.get("name_ar") or q["code"], 80)))
            for q in rel) + "</div>"
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name, "sku": code,
          "image": imgs or [LOGO], "description": clean(p.get("description_ar") or "", 4000), "url": url}
    if name_en:
        ld["alternateName"] = name_en
    b = brand_of(p)
    if b:
        ld["brand"] = {"@type": "Brand", "name": b}
    if cat:
        ld["category"] = cat
    if lo:
        if hi and hi != lo:
            ld["offers"] = {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": lo, "highPrice": hi,
                            "url": url, "seller": {"@type": "Organization", "name": BRAND}}
        else:
            ld["offers"] = {"@type": "Offer", "priceCurrency": "USD", "price": lo, "url": url,
                            "seller": {"@type": "Organization", "name": BRAND}}
    ldj = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    return PAGE.format(title=html.escape(name), title_attr=html.escape(name), brand=BRAND, desc=html.escape(desc),
                       ogimg=html.escape(og), url=url, ld=ldj, css=CSS, store=STORE, img=html.escape(hero),
                       catlink=catlink, en=('<p class="en">%s</p>' % html.escape(name_en)) if name_en else "",
                       price=price, wa=('<div class="contact"><span class="lb">تواصل معنا</span><div class="warow">%s</div></div>' % "".join(wa)) if wa else "", target=html.escape(target), sizes=sizes_html,
                       body=desc_html(p.get("description_ar") or ""), gallery=gal, endesc=endesc, related=related)


def main():
    rows = [p for p in products() if re.fullmatch(r"[A-Za-z0-9_-]{2,40}", (p.get("code") or "").strip())]
    for p in rows:
        p["code"] = p["code"].strip()
    contact_list = contacts()
    by_cat = {}
    for p in rows:
        by_cat.setdefault(p.get("category_name") or "", []).append(p)
    pdir = os.path.join(ROOT, "p")
    shutil.rmtree(pdir, ignore_errors=True)
    urls = [(SITE + "/", None), (STORE, None)]
    for p in rows:
        d = os.path.join(pdir, p["code"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_page(p, by_cat, contact_list))
        urls.append((SITE + "/p/" + p["code"] + "/", (p.get("updated_at") or "")[:10] or None))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in urls:
        sm.append("<url><loc>%s</loc>%s</url>" % (html.escape(u), ("<lastmod>%s</lastmod>" % lm) if lm else ""))
    sm.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    print("built", len(rows), "product pages + sitemap")


if __name__ == "__main__":
    main()
