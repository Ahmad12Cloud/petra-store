/* ===== V232: nested categories — a main section opens its sub-sections, then the products ===== */
const PP232_DEFAULT=[
 {id:'brk',name:'القواطع',nameEn:'Circuit Breakers',cats:['قواطع صغيرة MCB – AC','قواطع صغيرة MCB – DC','قواطع صناعية MCCB – DC','قواطع ذكية Smart MCB – AC / DC']},
 {id:'con',name:'الكونتاكتورات',nameEn:'Contactors',cats:['كونتاكتور مودولار (Contactor)','كونتاكتورات تحكّم · صناعي']},
 {id:'prot',name:'الحمايات والتحكّم',nameEn:'Protection & Control',cats:['ريليه حماية 3 فاز – مع نيوترال · بدون نيوترال','بروتكشن 3 فاز · سنجل فاز – حماية فولتاج','تايمرات – ريليه وقت','حساسات ضوئية (فوتوسيل)']},
 {id:'sw',name:'مفاتيح التحويل والعزل',nameEn:'Transfer & Isolator Switches',cats:['ATS تلقائي / يدوي','أيزوليتر DC (مفاتيح عزل)']},
 {id:'meas',name:'القياس والعدادات',nameEn:'Meters & Testers',cats:['أجهزة القياس والفحص – أفوميتر · كلامب ميتر','عدادات تابلو – فولتميتر · أمبيرميتر · ملتيميتر']},
 {id:'fuse',name:'الفيوزات',nameEn:'Fuses',cats:['بورد فيوز 1000V_DC','بورد فيوز AC','فيوزات DC']},
 {id:'lug',name:'الكوسات والأدوات',nameEn:'Cable Lugs & Tools',cats:['كوسات وأطراف كابلات – أنبوبي بلاستيك · نحاس · ألمنيوم','كبّاسات وأدوات تركيب – MC4 · كوسات أنبوبي · مشكّل']},
 {id:'acu',name:'المكيفات',nameEn:'Air Conditioners',cats:['مكيفات (Air Conditioners)','مكيفات ميديا (Midea)','مكيفات فيليبس (Philips)','مكيفات إل جي (LG)','مكيفات تي سي إل (TCL)','مكيفات سامسونج (Samsung)']}
];
let pp232G='',pp232GAll=false,pp232Flat=false,pp232Dept=null;
function pp232Groups(){const g=state.settings.pp232Groups;return (Array.isArray(g)&&g.length?g:PP232_DEFAULT).filter(x=>x&&x.id&&Array.isArray(x.cats));}
function pp232Owner(){try{return visibleAdmin()&&!(typeof pp123Staff!=='undefined'&&pp123Staff)}catch(_){return false}}
function pp232Prods(c){const hid=pp183Hidden(state),adm=visibleAdmin();return state.products.filter(p=>p.category===c&&(p.active||adm)&&(adm||!hid.includes(c)));}
function pp232CatsOf(g){const all=allCategories();return g.cats.filter(c=>all.includes(c)&&(!ppDept||pp139InDept(ppDept,c))&&pp232Prods(c).length);}
function pp232GroupOf(c){return pp232Groups().find(g=>g.cats.includes(c))||null;}
function pp232Name(g){return lang==='en'?(g.nameEn||g.name):g.name;}
function pp232Img(cats){for(const c of cats){const p=pp232Prods(c).find(x=>Array.isArray(x.images)&&x.images[0]);if(p)return pp149Thumb(p.images[0]);}return '';}
function pp232Count(n,one,two,many){return n===1?one:n===2?two:n+' '+many;}
function pp232Tile(img,name,sub,act,val){return `<button type="button" class="pp232-tile" data-pp232="${act}" data-v="${esc(val)}">${img?`<img src="${esc(img)}" alt="${esc(name)}" loading="lazy">`:`<span class="pp232-noimg">⚡</span>`}<span class="pp232-arr">‹</span><b>${esc(name)}</b><small>${sub}</small></button>`;}
function pp232ProdTxt(n){return lang==='en'?n+' products':pp232Count(n,'منتج واحد','منتجين',n<=10?'منتجات':'منتج');}
function pp232SecTxt(n){return lang==='en'?n+' sections':pp232Count(n,'قسم واحد','قسمين',n<=10?'أقسام':'قسم');}
function pp232DeptTiles(){
  const used=new Set();let h='';
  pp232Groups().forEach(g=>{const cs=pp232CatsOf(g);cs.forEach(c=>used.add(c));if(!cs.length)return;const n=cs.reduce((a,c)=>a+pp232Prods(c).length,0);
    if(cs.length===1)h+=pp232Tile(pp232Img(cs),ppCatLabel(cs[0]),pp232ProdTxt(n),'cat',cs[0]);
    else h+=pp232Tile(pp232Img(cs),pp232Name(g),pp232SecTxt(cs.length)+' · '+pp232ProdTxt(n),'grp',g.id);});
  allCategories().filter(c=>!used.has(c)&&(!ppDept||pp139InDept(ppDept,c))&&pp232Prods(c).length).forEach(c=>{h+=pp232Tile(pp232Img([c]),ppCatLabel(c),pp232ProdTxt(pp232Prods(c).length),'cat',c);});
  return h;}
function pp232Root(){const d=ppDept&&pp139Dept(ppDept);return d?(lang==='en'?(d.nameEn||d.name):d.name):T('الأقسام','Sections');}
function pp232Crumb(parts){return `<div class="pp232-crumb"><button type="button" class="pp232-back" data-pp232="back" aria-label="${T('رجوع','Back')}">→</button><span>${parts.map((p,i)=>i<parts.length-1?`<button type="button" data-pp232="${p[1]}" data-v="${esc(p[2]||'')}">${esc(p[0])}</button> ‹ `:`<b>${esc(p[0])}</b>`).join('')}</span></div>`;}
function pp232Chips(g,on){const cs=pp232CatsOf(g);return `<div class="pp232-chips"><button type="button" data-pp232="gall" data-v="${esc(g.id)}" class="${on?'':'on'}">${T('الكل','All')}</button>${cs.map(c=>`<button type="button" data-pp232="cat" data-v="${esc(c)}" class="${on===c?'on':''}">${esc(ppCatLabel(c))}</button>`).join('')}</div>`;}
function pp232Hide(v,grid){v.querySelectorAll('.pp139-chips').forEach(x=>x.style.setProperty('display','none','important'));if(grid)v.querySelectorAll(':scope > .toolbar, :scope > .grid-products, :scope > .pager, :scope > .empty').forEach(x=>x.style.setProperty('display','none','important'));}
function pp232Apply(){
  const v=$('view');if(!v||tab!=='catalog'||pp24HomeMode())return;
  if(pp232Dept!==ppDept){pp232Dept=ppDept;pp232G='';pp232GAll=false;pp232Flat=false;}
  v.querySelectorAll('.pp232-box').forEach(x=>x.remove());
  if(q||ppOnlyNew)return;
  const anchor=v.querySelector('.owner-tools')||v.querySelector(':scope > .toolbar')||v.firstElementChild;
  const put=html=>{const box=document.createElement('div');box.className='pp232-box';box.innerHTML=html;if(anchor&&anchor.parentNode===v)v.insertBefore(box,anchor);else v.appendChild(box);};
  const og=pp232Owner()?`<button type="button" class="pp232-own" data-pp232="edit">🗂 ${T('ترتيب الأقسام الرئيسية والفرعية','Arrange main sections')}</button>`:'';
  if(cat){const g=pp232GroupOf(cat);if(!g||pp232CatsOf(g).length<2)return;pp232G=g.id;pp232GAll=false;
    pp232Hide(v,false);v.querySelectorAll('.pp139-head').forEach(x=>x.style.setProperty('display','none','important'));
    put(pp232Crumb([[pp232Root(),'root'],[pp232Name(g),'grp',g.id],[ppCatLabel(cat)]])+pp232Chips(g,cat));return;}
  if(!ppDept)return;
  if(pp232Flat)return;
  if(pp232G){const g=pp232Groups().find(x=>x.id===pp232G);if(!g){pp232G='';return pp232Apply();}
    const cs=pp232CatsOf(g);v.querySelectorAll('.pp139-head').forEach(x=>x.style.setProperty('display','none','important'));
    if(pp232GAll){const items=list().filter(p=>cs.includes(p.category));pp232Hide(v,false);
      const grid=v.querySelector(':scope > .grid-products');if(grid)grid.innerHTML=pp45GridMarkup(items,null);
      v.querySelectorAll(':scope > .pager').forEach(x=>x.style.setProperty('display','none','important'));const tb=v.querySelector(':scope > .toolbar .muted');if(tb)tb.textContent=items.length+' '+T('منتج','products');
      put(pp232Crumb([[pp232Root(),'root'],[pp232Name(g)]])+pp232Chips(g,''));return;}
    const n=cs.reduce((a,c)=>a+pp232Prods(c).length,0);pp232Hide(v,true);
    put(pp232Crumb([[pp232Root(),'root'],[pp232Name(g)]])+`<h2 class="pp232-h">${esc(pp232Name(g))}</h2><div class="pp232-grid">${cs.map(c=>pp232Tile(pp232Img([c]),ppCatLabel(c),pp232ProdTxt(pp232Prods(c).length),'cat',c)).join('')}</div><button type="button" class="pp232-all" data-pp232="gall" data-v="${esc(g.id)}">🛒 ${T('شوف كل','See all')} ${esc(pp232Name(g))} (${pp232ProdTxt(n)})</button>`+og);return;}
  const tiles=pp232DeptTiles();if(!tiles)return;pp232Hide(v,true);const d=pp139Dept(ppDept);v.querySelectorAll('.pp139-title small').forEach(x=>x.style.setProperty('display','none','important'));
  put(`<div class="pp232-grid">${tiles}</div><button type="button" class="pp232-all" data-pp232="flat">🛒 ${T('شوف كل منتجات','See all')} ${esc(d?(lang==='en'?(d.nameEn||d.name):d.name):'')}</button>`+og);}
try{const _dc232=drawCatalog;drawCatalog=function(){_dc232.apply(this,arguments);try{pp232Apply()}catch(e){console.warn('pp232',e)}};}catch(_){}
(function(){const st=document.createElement('style');st.textContent='.pp232-box{margin:6px 0 12px}.pp232-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}.pp232-tile{position:relative;display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid #eadfc4;border-radius:16px;padding:8px;box-shadow:0 2px 8px rgba(0,0,0,.07);font:inherit;color:#1b1b1b;text-align:center;cursor:pointer}.pp232-tile img,.pp232-noimg{width:100%;aspect-ratio:1/1;object-fit:contain;border-radius:12px;background:#fff}.pp232-noimg{display:flex;align-items:center;justify-content:center;font-size:40px;background:#fff8e6}.pp232-tile b{font-size:14px;line-height:1.4;margin-top:5px;min-height:39px;display:flex;align-items:center}.pp232-tile small{margin-top:4px;font-size:12px;font-weight:700;color:#7a5a00;background:#fff3cd;border-radius:10px;padding:1px 9px}.pp232-arr{position:absolute;left:12px;top:12px;width:26px;height:26px;border-radius:50%;background:#111;color:#ffd34d;display:flex;align-items:center;justify-content:center;font-size:16px}.pp232-all{display:block;width:100%;margin:12px 0 4px;background:#fff8e6;border:1px solid #efd9a0;border-radius:14px;padding:11px;font:inherit;font-weight:800;color:#6b4e00;font-size:15px}.pp232-own{display:block;width:100%;margin:8px 0;border:2px dashed #c9a24a;background:#fffdf5;border-radius:12px;padding:10px;font:inherit;font-weight:800;color:#6b4e00}.pp232-crumb{display:flex;align-items:center;gap:8px;margin:2px 0 8px;font-size:14px;color:#777;flex-wrap:wrap}.pp232-crumb span button{border:0;background:none;color:#8a6a1c;font:inherit;padding:0;text-decoration:underline;cursor:pointer}.pp232-crumb b{color:#111;font-size:15px}.pp232-back{width:34px;height:34px;border-radius:50%;background:#fff;border:1px solid #e3d6b0;color:#6b4e00;font-size:18px;flex:none}.pp232-h{font-size:19px;margin:4px 2px 10px}.pp232-chips{display:flex;gap:7px;overflow-x:auto;padding:2px 0 8px;scrollbar-width:none}.pp232-chips::-webkit-scrollbar{display:none}.pp232-chips button{flex:none;border:1.5px solid #e0b040;border-radius:18px;padding:5px 13px;font:inherit;font-size:13.5px;font-weight:700;background:#fff;color:#1b1b1b;white-space:nowrap}.pp232-chips button.on{background:linear-gradient(#ffd34d,#f29a10);border-color:#9a6400}#pp232ed{position:fixed;inset:0;z-index:99999;background:#fdf9f0;overflow:auto;padding:12px 14px 90px;direction:rtl;color:#2d2f33}#pp232ed h2{margin:6px 0}#pp232ed .hint{font-size:13px;color:#6b5b45;line-height:1.7;margin:0 0 10px}#pp232ed .g{background:#fff;border:1px solid #e3cf9f;border-radius:14px;padding:10px;margin-bottom:10px}#pp232ed .g input{width:100%;box-sizing:border-box;padding:9px;border:1px solid #d8c38d;border-radius:10px;font:inherit;margin-bottom:6px}#pp232ed .ctl{display:flex;gap:6px;flex-wrap:wrap}#pp232ed button{border:1px solid #d8c38d;background:#fff8e6;border-radius:10px;padding:8px 11px;font:inherit;font-size:14px}#pp232ed .del{color:#a02020;border-color:#e6b8b8;background:#fff3f3}#pp232ed .c{display:grid;grid-template-columns:1fr;gap:4px;border-top:1px dashed #e3cf9f;padding:8px 0}#pp232ed .c select{padding:8px;border:1px solid #d8c38d;border-radius:10px;font:inherit;background:#fffdf8}#pp232ed .bar{position:fixed;left:0;right:0;bottom:0;padding:10px 14px;background:#fff;border-top:1px solid #e3cf9f;display:flex;gap:8px}#pp232ed .bar button{flex:1;font-weight:800}#pp232ed .bar .ok{background:#f3bc4f}';document.head.appendChild(st);})();
let pp232Draft=null;
function pp232EdDraw(){let o=document.getElementById('pp232ed');if(!o){o=document.createElement('div');o.id='pp232ed';document.body.appendChild(o);}
  const all=allCategories(),gs=pp232Draft;const where=c=>{const g=gs.find(x=>x.cats.includes(c));return g?g.id:'';};
  o.innerHTML=`<h2>🗂 ${T('الأقسام الرئيسية','Main sections')}</h2><p class="hint">كل قسم رئيسي بيفتح الأقسام اللي جوّاته. غيّر الأسماء، رتّب بالأسهم، واختار لكل قسم فرعي تحت أي قسم رئيسي بيكون. القسم اللي ما إلو قسم رئيسي بيبيّن لحاله. القسم الفاضي ما بيبيّن للزبون.</p>
  ${gs.map((g,i)=>`<div class="g"><input data-pp232f="name" data-i="${i}" value="${esc(g.name)}" placeholder="الاسم بالعربي"><input data-pp232f="nameEn" data-i="${i}" value="${esc(g.nameEn||'')}" placeholder="English name" dir="ltr"><div class="ctl"><button type="button" data-pp232e="up" data-i="${i}">▲</button><button type="button" data-pp232e="down" data-i="${i}">▼</button><button type="button" class="del" data-pp232e="del" data-i="${i}">🗑 حذف القسم الرئيسي</button></div><div style="font-size:12.5px;margin-top:6px;color:#6b5b45">${g.cats.filter(c=>all.includes(c)).map(c=>esc(c)).join(' · ')||'— فاضي —'}</div></div>`).join('')}
  <button type="button" data-pp232e="add" style="width:100%;font-weight:800;background:#f3bc4f">＋ قسم رئيسي جديد</button>
  <h2 style="margin-top:16px">${T('وين بينحط كل قسم','Sub-sections')}</h2>${all.map(c=>`<div class="c"><b style="font-size:14px">${esc(c)}</b><select data-pp232c="${esc(c)}"><option value="">— لحاله (بدون قسم رئيسي) —</option>${gs.map(g=>`<option value="${esc(g.id)}" ${where(c)===g.id?'selected':''}>${esc(g.name)}</option>`).join('')}</select></div>`).join('')}
  <div class="bar"><button type="button" class="ok" data-pp232e="save">✅ حفظ</button><button type="button" data-pp232e="close">إلغاء</button></div>`;}
function pp232EdRead(){const o=document.getElementById('pp232ed');if(!o)return;o.querySelectorAll('[data-pp232f]').forEach(i=>{const g=pp232Draft[+i.dataset.i];if(g)g[i.dataset.pp232f]=i.value.trim();});
  const sel=[...o.querySelectorAll('[data-pp232c]')];if(!sel.length)return;pp232Draft.forEach(g=>{g.cats=g.cats.filter(c=>!allCategories().includes(c));});sel.forEach(s=>{const g=pp232Draft.find(x=>x.id===s.value);if(g)g.cats.push(s.dataset.pp232c);});}
document.addEventListener('click',async e=>{const b=e.target&&e.target.closest&&e.target.closest('[data-pp232],[data-pp232e]');if(!b)return;e.preventDefault();e.stopImmediatePropagation();
  const a=b.dataset.pp232,v=b.dataset.v||'';
  try{
  if(a){window.scrollTo({top:0,behavior:'instant'});
    if(a==='grp'){pp232G=v;pp232GAll=false;cat='';pg=1;goto('catalog');return;}
    if(a==='cat'){const g=pp232GroupOf(v);if(g)pp232G=g.id;pp232GAll=false;cat=v;pg=1;goto('catalog');return;}
    if(a==='gall'){pp232G=v;pp232GAll=true;cat='';pg=1;goto('catalog');return;}
    if(a==='flat'){pp232Flat=true;cat='';pg=1;goto('catalog');return;}
    if(a==='root'){if(!ppDept){const c=cat;const d=pp139Depts().find(x=>pp139InDept(x.id,c));ppDept=d?d.id:'';pp24ShowAllProducts=false;}pp232Dept=ppDept;pp232G='';pp232GAll=false;pp232Flat=false;cat='';pg=1;goto('catalog');return;}
    if(a==='back'){if(cat||pp232GAll){const g=pp232GroupOf(cat)||pp232Groups().find(x=>x.id===pp232G);if(!ppDept){const d=pp139Depts().find(x=>pp139InDept(x.id,cat));ppDept=d?d.id:'';pp24ShowAllProducts=false;pp232Dept=ppDept;}pp232G=g?g.id:'';pp232GAll=false;cat='';}else{pp232G='';}pp232Flat=false;pg=1;goto('catalog');return;}
    if(a==='edit'){if(!pp232Owner())return;pp232Draft=JSON.parse(JSON.stringify(pp232Groups()));pp232EdDraw();return;}
    return;}
  const x=b.dataset.pp232e,i=+b.dataset.i;if(!pp232Draft)return;pp232EdRead();
  if(x==='close'){pp232Draft=null;document.getElementById('pp232ed')?.remove();return;}
  if(x==='up'&&i>0){[pp232Draft[i-1],pp232Draft[i]]=[pp232Draft[i],pp232Draft[i-1]];}
  if(x==='down'&&i<pp232Draft.length-1){[pp232Draft[i+1],pp232Draft[i]]=[pp232Draft[i],pp232Draft[i+1]];}
  if(x==='del'){if(!confirm('حذف القسم الرئيسي؟ الأقسام اللي جوّاته بيرجعوا يبيّنوا لحالهن، وما بينمحى أي منتج.'))return;pp232Draft.splice(i,1);}
  if(x==='add'){pp232Draft.push({id:'g'+Date.now().toString(36),name:'قسم رئيسي جديد',nameEn:'',cats:[]});}
  if(x==='save'){if(pp232Draft.some(g=>!g.name)){note('اكتب اسم لكل قسم رئيسي');return;}state.settings.pp232Groups=pp232Draft;pp232Draft=null;document.getElementById('pp232ed')?.remove();await changed();start();note('✅ انحفظت الأقسام الرئيسية');return;}
  pp232EdDraw();
  }catch(err){note('صار خطأ: '+(err&&err.message||err));}
},true);
window.addEventListener('click',e=>{try{const b=e.target&&e.target.closest&&e.target.closest('[data-pp139="dept"],[data-action="pp24-home"],[data-pp139n],[data-pp200],[data-action="menu-all"],[data-action="menu-category"],[data-action="menu-new"]');if(b){pp232G='';pp232GAll=false;pp232Flat=false;pp232Dept=null;}}catch(_){}},true);
