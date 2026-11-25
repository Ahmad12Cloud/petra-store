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
                  "extra->department,created_at&active=eq.true&order=code.asc&limit=1000&offset=%d" % off)
        out += rows
        if len(rows) < 1000:
            return out
        off += 1000


GROUPS_DEFAULT = [
    ("القواطع", ["قواطع صغيرة MCB – AC", "قواطع صغيرة MCB – DC", "قواطع صناعية MCCB – DC", "قواطع ذكية Smart MCB – AC / DC"]),
    ("الكونتاكتورات", ["كونتاكتور مودولار (Contactor)", "كونتاكتورات تحكّم · صناعي"]),
    ("الحمايات والتحكّم", ["ريليه حماية 3 فاز – مع نيوترال · بدون نيوترال", "بروتكشن 3 فاز · سنجل فاز – حماية فولتاج", "تايمرات – ريليه وقت", "حساسات ضوئية (فوتوسيل)"]),
    ("مفاتيح التحويل والعزل", ["ATS تلقائي / يدوي", "أيزوليتر DC (مفاتيح عزل)"]),
    ("القياس والعدادات", ["أجهزة القياس والفحص – أفوميتر · كلامب ميتر", "عدادات تابلو – فولتميتر · أمبيرميتر · ملتيميتر"]),
    ("الفيوزات", ["بورد فيوز 1000V_DC", "بورد فيوز AC", "فيوزات DC"]),
    ("الكوسات والأدوات", ["كوسات وأطراف كابلات – أنبوبي بلاستيك · نحاس · ألمنيوم", "كبّاسات وأدوات تركيب – MC4 · كوسات أنبوبي · مشكّل"]),
    ("المكيفات", ["مكيفات (Air Conditioners)", "مكيفات ميديا (Midea)", "مكيفات فيليبس (Philips)", "مكيفات إل جي (LG)", "مكيفات تي سي إل (TCL)", "مكيفات سامسونج (Samsung)"]),
]


def groups():
    """Main sections as the owner arranged them in the store (V232), else the default."""
    try:
        rows = sb("store_settings?select=g:data->pp232Groups&id=eq.1")
        g = rows[0].get("g") if rows else None
        if isinstance(g, list) and g:
            return [(x.get("name") or "", [c for c in (x.get("cats") or []) if isinstance(c, str)]) for x in g if isinstance(x, dict)]
    except Exception as e:
        print("groups fallback:", e)
    return GROUPS_DEFAULT


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


# ---------------------------------------------------------------- home page (/)
# Real landing page for Google (was an instant redirect to /shop/).
# Font: Noto Sans Arabic, self-hosted in /fonts (SIL OFL), so every phone shows the same letters.
AR_RANGE = "U+0600-06FF,U+0750-077F,U+0870-08FF,U+FB50-FDFF,U+FE70-FEFF,U+200C-200F"
LA_RANGE = "U+0000-00FF,U+2010-2027,U+20AC"
FONT_CSS = "".join(
    "@font-face{font-family:'PE Sans';src:url('/fonts/noto-sans-arabic-%s-%d-normal.woff2') format('woff2');"
    "font-weight:%d;font-display:swap;unicode-range:%s}" % (sub, w, w, rng)
    for w in (400, 700, 800) for sub, rng in (("arabic", AR_RANGE), ("latin", LA_RANGE)))

WA_SVG = ('<svg viewBox="0 0 32 32" width="18" height="18" aria-hidden="true"><path fill="#25D366" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3z"/>'
          '<path fill="#fff" d="M23.3 19.2c-.4-.2-2.3-1.1-2.6-1.2-.4-.1-.6-.2-.9.2-.3.4-1 1.2-1.2 1.4-.2.2-.4.3-.8.1-.4-.2-1.6-.6-3-1.9-1.1-1-1.9-2.2-2.1-2.6-.2-.4 0-.6.2-.8l.6-.7c.2-.2.3-.4.4-.7.1-.3 0-.5 0-.7l-1.2-2.8c-.3-.7-.6-.6-.9-.6h-.7c-.3 0-.7.1-1 .5-.4.4-1.4 1.3-1.4 3.2s1.4 3.7 1.6 4c.2.3 2.8 4.2 6.7 5.9 2.5 1 3.4 1.1 4.6.9.7-.1 2.3-.9 2.6-1.8.3-.9.3-1.7.2-1.8-.1-.2-.4-.3-.8-.5z"/></svg>')

HOME_CSS = """*{box-sizing:border-box}body{margin:0;font-family:'PE Sans',Tahoma,Arial,sans-serif;background:#f6f2e8;color:#1b1b1b;line-height:1.7}
a{color:inherit;text-decoration:none}.top{background:#000;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;position:sticky;top:0;z-index:2}
.brand{display:flex;align-items:center;gap:8px}.brand img{width:43px;height:43px}
.bl{display:flex;flex-direction:column;align-items:center;font-family:Arial,sans-serif;font-weight:800;color:#d4af37;text-transform:uppercase;line-height:1.15}.bl .l1{font-size:16px}.bl .l2{font-size:12px}
.all{background:linear-gradient(#ffd34d,#f29a10);color:#141414;font-weight:800;border-radius:12px;padding:7px 12px;font-size:14px}
.hero{background:linear-gradient(160deg,#111 0%,#1d1a12 60%,#3a2c08 100%);color:#fff;padding:22px 16px 20px;text-align:center}
.hero .lg{width:84px;height:84px}.hero h1{font-size:21px;line-height:1.5;margin:8px 0 6px;color:#fff;font-weight:800}.hero h1 em{font-style:normal;color:#f5c23e}
.hero p{font-size:14px;color:#ddd;margin:0 auto 14px;max-width:560px}
.cta{display:inline-block;background:linear-gradient(#ffd34d,#f29a10);color:#141414;font-weight:800;border-radius:24px;padding:10px 26px;font-size:16px}
.warow{display:flex;justify-content:center;gap:8px;margin-top:12px;flex-wrap:wrap}
.wa{display:inline-flex;align-items:center;gap:5px;background:#f0f9f3;border:1px solid #d6eedf;border-radius:20px;padding:5px 12px;font-size:14px;font-weight:700;color:#2c6b45;white-space:nowrap}
.chips{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:14px}.chips span{border:1px solid #6b5520;color:#f0d68a;border-radius:16px;padding:2px 10px;font-size:12px}
.br{margin-top:12px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap;align-items:center;font-size:13px}.br b{color:#f5c23e;width:100%}
.br span{background:rgba(255,255,255,.08);border:1px solid #6b5520;color:#fff;border-radius:16px;padding:3px 12px}
.wrap{max-width:760px;margin:0 auto;padding:4px 12px 10px}h2{font-size:19px;margin:20px 2px 10px;display:flex;align-items:center;gap:8px}h2:before{content:"";width:5px;height:20px;background:#f29a10;border-radius:3px}
.cats,.pr{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}
.ct{background:#fff;border-radius:16px;padding:8px;box-shadow:0 2px 8px rgba(0,0,0,.07);display:flex;flex-direction:column;text-align:center}
.ct img,.pc img{width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;border-radius:12px}.ct b{font-size:14px;line-height:1.45;margin-top:4px;min-height:22px}.ct em{font-style:normal;font-size:11.5px;color:#666;line-height:1.5;margin:2px 0 4px}.ct span{font-size:12px;color:#a06a00;font-weight:700}
.box{background:#fff;border-radius:18px;padding:14px 16px;box-shadow:0 2px 8px rgba(0,0,0,.07);font-size:14.5px}.box p{margin:0 0 8px}
.sv{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}.sv div{background:#faf6ea;border-radius:12px;padding:8px;font-size:13px;font-weight:700;text-align:center}
.sv div small{display:block;font-weight:400;color:#777;font-size:11.5px;direction:ltr}
.pc{background:#fff;border-radius:16px;padding:8px;box-shadow:0 2px 8px rgba(0,0,0,.07);font-size:12.5px;display:flex;flex-direction:column}
.pc b{line-height:1.45;min-height:38px;font-size:13.5px}.pc small{display:block;color:#666;font-size:11.5px;line-height:1.4;min-height:32px;text-align:left}
.pc i{font-style:normal;color:#e07b00;font-weight:800;font-size:17px;direction:ltr;unicode-bidi:isolate;margin-top:auto}
.loc{display:grid;gap:10px}.lc{background:#fff;border-radius:16px;padding:12px 14px;box-shadow:0 2px 8px rgba(0,0,0,.07);display:flex;gap:10px;align-items:center}
.lc .ic{font-size:26px}.lc b{display:block;font-size:15px}.lc span{font-size:13px;color:#555;direction:ltr;display:inline-block}
.more{text-align:center;margin:14px 0 4px}.go{display:inline-flex;gap:6px;background:#fff8e6;border:1px solid #efd9a0;border-radius:22px;padding:7px 16px;font-size:14px;font-weight:700;color:#6b4e00}
details{margin-top:12px;background:#faf6ea;border-radius:12px;padding:8px 12px;font-size:13.5px}summary{font-weight:800;cursor:pointer}
.soc{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}.soc a{background:#fff;border-radius:16px;padding:10px 12px;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,.07);display:flex;align-items:center;gap:10px;min-width:0}
.soc svg{width:38px;height:38px;border-radius:50%;padding:7px;flex:none}.soc b{display:block;font-size:15px;line-height:1.3}.soc small{display:block;color:#777;font-size:11px;direction:ltr;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
footer{background:#000;color:#bbb;text-align:center;font-size:12.5px;padding:18px 10px;margin-top:20px}footer b{color:#d4af37}"""


# official social pages (clean links, no tracking parameters)
SOCIAL = [
    ("YouTube", "https://www.youtube.com/@deye.installation", "Petra Power Energy", "#ff0000",
     '<path fill="#fff" d="M9.5 7.5v9l7.5-4.5z"/>'),
    ("Facebook", "https://www.facebook.com/share/1EJPw6eAka/", "Petra Power Energy", "#1877f2",
     '<path fill="#fff" d="M13.5 21v-7.5H16l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/>'),
    ("TikTok", "https://www.tiktok.com/@petrapowerenergy", "@petrapowerenergy", "#111",
     '<path fill="#fff" d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.1v12.4a2.6 2.6 0 1 1-2.6-2.6c.3 0 .5 0 .8.1V9.7a5.7 5.7 0 1 0 4.9 5.7V9a7.3 7.3 0 0 0 4.3 1.4V7.3a4.3 4.3 0 0 1-3.2-1.5z"/>'),
    ("Instagram", "https://www.instagram.com/petrapower_energy/", "@petrapower_energy", "linear-gradient(45deg,#f9a825,#e1306c,#833ab4)",
     '<rect x="4" y="4" width="16" height="16" rx="5" fill="none" stroke="#fff" stroke-width="2"/><circle cx="12" cy="12" r="3.6" fill="none" stroke="#fff" stroke-width="2"/><circle cx="17" cy="7" r="1.2" fill="#fff"/>'),
]


def arabic_count(n):
    if n == 1:
        return "منتج واحد"
    if n == 2:
        return "منتجان"
    return ("%d منتجات" % n) if n <= 10 else ("%d منتجاً" % n)


def phone_for(contact_list, cc, fallback):
    for c in contact_list:
        num = re.sub(r"\D", "", c.get("phone") or "")
        if num.startswith(cc) and (c.get("where") or {}).get("elec"):
            return c.get("phone").strip()
    return fallback


def build_home(rows, contact_list):
    elec = [p for p in rows if not is_ac(p)]
    # main sections (grouped like the store), each with its sub-sections listed for Google
    cats = {}
    for p in elec:
        c = p.get("category_name") or ""
        if c:
            cats.setdefault(c, []).append(p)
    tiles, used = [], set()

    def tile(name, ps, subs):
        img = next((imgs_of(p)[0] for p in ps if imgs_of(p)), None)
        sub = ('<em>%s</em>' % " · ".join(html.escape(x) for x in subs)) if len(subs) > 1 else ""
        cnt = ("%s · %s" % ({2: "قسمين"}.get(len(subs), "%d أقسام" % len(subs)), arabic_count(len(ps)))) if len(subs) > 1 else arabic_count(len(ps))
        return '<a class="ct" href="%s"><img src="%s" alt="%s" width="300" height="300" loading="lazy"><b>%s</b>%s<span>%s</span></a>' % (
            html.escape(STORE), html.escape(thumb_or_full(img) if img else LOGO), html.escape(name), html.escape(name), sub, cnt)
    for gname, gcats in groups():
        subs = [c for c in gcats if c in cats]
        used.update(subs)
        if not subs:
            continue
        ps = [p for c in subs for p in cats[c]]
        tiles.append(tile(gname if len(subs) > 1 else subs[0], ps, subs))
    for c, ps in cats.items():
        if c not in used:
            tiles.append(tile(c, ps, [c]))
    cat_html = "".join(tiles)
    # newest 4 priced products
    new = sorted([p for p in elec if money(p.get("price")) and imgs_of(p)],
                 key=lambda p: p.get("created_at") or "", reverse=True)[:4]

    def pcard(p):
        name = clean(p.get("name_ar") or p["code"], 140)
        a, _, b = name.partition(" – ")
        return '<a class="pc" href="/p/%s/"><img src="%s" alt="%s" width="300" height="300" loading="lazy"><b>%s</b><small dir="ltr">%s</small><i>%s $</i></a>' % (
            html.escape(p["code"]), html.escape(thumb_or_full(imgs_of(p)[0])), html.escape(name),
            html.escape(a), html.escape(b), money(p.get("price")))
    new_html = "".join(pcard(p) for p in new)
    # WhatsApp (same main numbers as the product pages)
    msg = urllib.parse.quote("مرحبا، بدي استفسر عن منتجاتكم\n" + SITE + "/")
    wa = []
    for c in contact_list:
        if not (c.get("where") or {}).get("elec"):
            continue
        num = re.sub(r"\D", "", c.get("phone") or "")
        if num:
            label = re.sub(r"^(فرع|قسم)\s+", "", no_flags(c.get("name") or ""))
            wa.append('<a class="wa" href="https://wa.me/%s?text=%s">%s %s</a>' % (num, msg, WA_SVG, html.escape(label)))
    lb = phone_for(contact_list, "961", "+961 76 685 783")
    sy = phone_for(contact_list, "963", "+963 957 320 372")
    title = "Petra Power Energy – معدات كهربائية وطاقة شمسية في بيروت، لبنان وسوريا"
    desc = ("متجر Petra Power Energy للمعدات الكهربائية والطاقة الشمسية في بيروت – لبنان ودمشق – سوريا: "
            "قواطع MCB و MCCB، كونتاكتورات، ATS، حمايات فولتاج وفازات، أيزوليتر DC وأجهزة قياس، مع طلب مباشر عبر واتساب.")
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/", "inLanguage": ["ar", "en"]},
          {"@context": "https://schema.org", "@type": "Store", "name": BRAND, "alternateName": "Petra Power",
           "url": SITE + "/", "logo": LOGO, "image": LOGO, "description": desc, "telephone": lb,
           "address": {"@type": "PostalAddress", "addressLocality": "Beirut", "addressCountry": "LB"},
           "areaServed": [{"@type": "Country", "name": "Lebanon"}, {"@type": "Country", "name": "Syria"}],
           "department": [{"@type": "Store", "name": BRAND + " – Damascus", "telephone": sy,
                           "address": {"@type": "PostalAddress", "addressLocality": "Damascus – Al-Qazzaz", "addressCountry": "SY"}}],
           "sameAs": [u for _, u, _, _, _ in SOCIAL],
           "knowsAbout": ["Solar energy", "On-Grid", "Off-Grid", "Control panels", "Fuel Save", "MCB", "MCCB", "ATS", "Contactor"]}]
    ldj = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    page = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{brand}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{logo}">
<meta property="og:url" content="{site}/">
<link rel="canonical" href="{site}/">
<link rel="icon" href="/icon-192.png">
<link rel="preload" href="/fonts/noto-sans-arabic-arabic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<script>
/* old links (?p=CODE, #...) and the installed app still open the store directly */
(function(){{var s=location.search,h=location.hash,a=false;try{{a=matchMedia("(display-mode: standalone)").matches||navigator.standalone;}}catch(e){{}}
if(s||h||a)location.replace("/shop/"+s+h);}})();
</script>
<script type="application/ld+json">{ld}</script>
<style>{font}{css}</style>
</head><body>
<header class="top"><a class="brand" href="/" aria-label="{brand}"><img src="/pe-logo.webp" alt="{brand}" width="43" height="43"><span class="bl"><span class="l1">Petrapower</span><span class="l2">Energy</span></span></a><a class="all" href="{store}">🛒 كل المنتجات</a></header>
<section class="hero"><img class="lg" src="/pe-logo.webp" alt="{brand}" width="84" height="84">
<h1>Petra Power Energy<br><em>معدات كهربائية وطاقة شمسية</em><br>في بيروت – لبنان وسوريا</h1>
<p>قواطع MCB و MCCB، كونتاكتورات، ATS، حمايات فولتاج وفازات، أيزوليتر DC وأجهزة قياس — أسعار واضحة وطلب مباشر عبر واتساب.</p>
<a class="cta" href="{store}">🛒 ادخل المتجر</a>
<div class="warow">{wa}</div>
<div class="chips"><span>⚡ منتجات أصلية</span><span>☀️ طاقة شمسية · خبرة طويلة في مجال العمل</span></div>
<div class="br"><b>📍 فروعنا</b><span>لبنان – بيروت</span><span>سوريا – دمشق – القزاز</span></div>
</section>
<main class="wrap">
<h2>الأقسام</h2><div class="cats">{cats}</div>
<h2>مين نحنا</h2>
<div class="box"><p><b>Petra Power Energy</b> شركة هندسية مقرّها بيروت، لها خبرة طويلة في مشاريع الطاقة الشمسية في لبنان وسوريا، وتوفّر المعدات الكهربائية التي تستخدمها في مشاريعها لكل فنّي وصاحب مشروع.</p>
<div class="sv"><div>☀️ تصميم وتنفيذ أنظمة شمسية<small>On-Grid · Off-Grid</small></div><div>🎛️ تابلوهات تحكّم<small>Control Panels</small></div><div>⛽ توفير وقود المولدات<small>Fuel Save</small></div><div>🔌 معدات كهربائية أصلية<small>MCB · MCCB · ATS</small></div></div></div>
{newsec}
<div class="more"><a class="go" href="{store}">🛒 اكتشف منتجات أكثر</a></div>
<h2>وين نحنا</h2>
<div class="loc"><div class="lc"><span class="ic">📍</span><div><b>بيروت – لبنان</b><span>{lb}</span></div></div>
<div class="lc"><span class="ic">📍</span><div><b>دمشق – القزاز – سوريا</b><span>{sy}</span></div></div></div>
<h2>تابع مشاريعنا</h2><div class="soc">{social}</div>
<details open dir="ltr"><summary>English</summary>Petra Power Energy – electrical equipment &amp; solar energy store in Beirut, Lebanon and Syria: MCB &amp; MCCB breakers, contactors, ATS, voltage &amp; phase protection, DC isolators and meters. Order directly on WhatsApp.</details>
</main>
<footer><b>{brand}</b><br>بيروت – لبنان · دمشق – سوريا<br><a href="{store}">petrapowerstore.com</a></footer>
</body></html>
""".format(title=html.escape(title), desc=html.escape(desc), brand=BRAND, logo=LOGO, site=SITE, store=html.escape(STORE),
           ld=ldj, font=FONT_CSS, css=HOME_CSS, wa="".join(wa), cats=cat_html,
           newsec=('<h2>وصل حديثاً</h2><div class="pr">%s</div>' % new_html) if new_html else "",
           lb=html.escape(lb), sy=html.escape(sy),
           social="".join('<a href="%s" target="_blank" rel="noopener" aria-label="%s"><svg viewBox="0 0 24 24" style="background:%s" aria-hidden="true">%s</svg><b>%s</b></a>' % (
               html.escape(u), n, bg, ic, n) for n, u, h, bg, ic in SOCIAL))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


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
    build_home(rows, contact_list)
    print("built", len(rows), "product pages + home + sitemap")


if __name__ == "__main__":
    main()
