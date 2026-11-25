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
let pp232MG='';
function pp232Groups(){const g=state.settings.pp232Groups;return (Array.isArray(g)&&g.length?g:PP232_DEFAULT).filter(x=>x&&x.id&&Array.isArray(x.cats));}
function pp232Owner(){try{return visibleAdmin()&&!(typeof pp123Staff!=='undefined'&&pp123Staff)}catch(_){return false}}
function pp232Prods(c){const hid=pp183Hidden(state),adm=visibleAdmin();return state.products.filter(p=>p.category===c&&(p.active||adm)&&(adm||!hid.includes(c)));}
function pp232Show(c){return visibleAdmin()?true:pp232Prods(c).length>0;}
function pp232Name(g){return lang==='en'?(g.nameEn||g.name):g.name;}
function pp232CatBtn(c,sub){return `<button type="button" data-action="menu-category" data-category="${esc(c)}"${sub?' class="pp232-s"':''}>${esc(ppCatLabel(c))}</button>`;}
function pp232MenuHtml(){
  const all=allCategories(),used=new Set();let h='';
  pp232Groups().forEach(g=>{const cs=g.cats.filter(c=>all.includes(c)&&pp232Show(c));g.cats.forEach(c=>used.add(c));if(!cs.length)return;
    if(cs.length===1){h+=pp232CatBtn(cs[0]);return;}
    h+=`<div class="pp232-acc" data-g="${esc(g.id)}"><button type="button" class="pp232-gh" data-pp232m="tog"><span>${esc(g.icon||'')}${g.icon?' ':''}${esc(pp232Name(g))}</span><i>▾</i></button><div class="pp232-subs"><button type="button" class="pp232-s pp232-sall" data-pp232m="all" data-v="${esc(g.id)}">${T('كل','All')} ${esc(pp232Name(g))}</button>${cs.map(c=>pp232CatBtn(c,true)).join('')}</div></div>`;});
  all.filter(c=>!used.has(c)&&pp232Show(c)).forEach(c=>{h+=pp232CatBtn(c);});
  if(pp232Owner())h+=`<button type="button" data-pp232="edit" style="border:2px dashed #c9a24a;font-weight:800">🗂 ${T('ترتيب الأقسام الرئيسية والفرعية','Arrange main sections')}</button>`;
  return h;}
try{const _dc232=drawCatalog;drawCatalog=function(){_dc232.apply(this,arguments);try{
  if(!pp232MG||cat||q||tab!=='catalog'||pp24HomeMode())return;const g=pp232Groups().find(x=>x.id===pp232MG);if(!g)return;const v=$('view');if(!v)return;
  const items=list().filter(p=>g.cats.includes(p.category));const grid=v.querySelector(':scope > .grid-products');if(grid)grid.innerHTML=pp45GridMarkup(items,null);
  v.querySelectorAll(':scope > .pager').forEach(x=>x.style.setProperty('display','none','important'));
  const tb=v.querySelector(':scope > .toolbar');if(tb){const st=tb.querySelector('strong'),mu=tb.querySelector('.muted');if(st)st.textContent=pp232Name(g);if(mu)mu.textContent=items.length+' '+T('منتج','products');}
  }catch(e){console.warn('pp232',e)}};}catch(_){}
(function(){const st=document.createElement('style');st.textContent='.pp232-acc{display:block}.v12-menu-list .pp232-gh{display:flex!important;justify-content:space-between;align-items:center;width:100%;font-weight:800!important}.pp232-gh i{font-style:normal;width:28px;height:28px;border-radius:50%;background:#fff3cd;color:#7a5a00;display:inline-flex;align-items:center;justify-content:center;flex:none;transition:transform .2s}.pp232-acc.open .pp232-gh{color:#7a5a00}.pp232-acc.open .pp232-gh i{background:#f29a10;color:#111;transform:rotate(180deg)}.pp232-subs{display:none;background:#fff8e6;border-radius:12px;margin:0 0 8px;padding:2px 8px;border-right:4px solid #f29a10}.pp232-acc.open .pp232-subs{display:block}.v12-menu-list .pp232-s{display:block;width:100%;font-size:15px!important;background:transparent!important}.v12-menu-list .pp232-sall{font-weight:800!important;color:#6b4e00!important}#pp232ed{position:fixed;inset:0;z-index:99999;background:#fdf9f0;overflow:auto;padding:12px 14px 90px;direction:rtl;color:#2d2f33}#pp232ed h2{margin:6px 0}#pp232ed .hint{font-size:13px;color:#6b5b45;line-height:1.7;margin:0 0 10px}#pp232ed .g{background:#fff;border:1px solid #e3cf9f;border-radius:14px;padding:10px;margin-bottom:10px}#pp232ed .g input{width:100%;box-sizing:border-box;padding:9px;border:1px solid #d8c38d;border-radius:10px;font:inherit;margin-bottom:6px}#pp232ed .ctl{display:flex;gap:6px;flex-wrap:wrap}#pp232ed button{border:1px solid #d8c38d;background:#fff8e6;border-radius:10px;padding:8px 11px;font:inherit;font-size:14px}#pp232ed .del{color:#a02020;border-color:#e6b8b8;background:#fff3f3}#pp232ed .c{display:grid;gap:4px;border-top:1px dashed #e3cf9f;padding:8px 0}#pp232ed .c select{padding:8px;border:1px solid #d8c38d;border-radius:10px;font:inherit;background:#fffdf8}#pp232ed .bar{position:fixed;left:0;right:0;bottom:0;padding:10px 14px;background:#fff;border-top:1px solid #e3cf9f;display:flex;gap:8px}#pp232ed .bar button{flex:1;font-weight:800}#pp232ed .bar .ok{background:#f3bc4f}';document.head.appendChild(st);})();
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
document.addEventListener('click',async e=>{const b=e.target&&e.target.closest&&e.target.closest('[data-pp232],[data-pp232e],[data-pp232m]');if(!b)return;e.preventDefault();e.stopImmediatePropagation();
  const a=b.dataset.pp232,v=b.dataset.v||'';
  try{
  if(b.dataset.pp232m==='tog'){const acc=b.closest('.pp232-acc');if(acc){const op=!acc.classList.contains('open');acc.parentElement.querySelectorAll('.pp232-acc.open').forEach(x=>x.classList.remove('open'));if(op)acc.classList.add('open');}return;}
  if(b.dataset.pp232m==='all'){try{setMenu(false)}catch(_){}pp232MG=b.dataset.v||'';ppDept='';pp24ShowAllProducts=true;cat='';q='';pg=1;ppOnlyNew=false;goto('catalog');return;}
  if(a){if(a==='edit'){if(!pp232Owner())return;try{setMenu(false)}catch(_){}pp232Draft=JSON.parse(JSON.stringify(pp232Groups()));pp232EdDraw();}return;}
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
window.addEventListener('click',e=>{try{const b=e.target&&e.target.closest&&e.target.closest('[data-pp139="dept"],[data-action="pp24-home"],[data-pp139n],[data-pp200],[data-action="menu-all"],[data-action="menu-category"],[data-action="menu-new"],[data-action="open-search"]');if(b){pp232MG='';}}catch(_){}},true);
