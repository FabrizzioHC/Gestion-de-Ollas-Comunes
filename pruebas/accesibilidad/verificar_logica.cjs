// Pruebas de lógica con DOM simulado; no sustituye la revisión visual en navegador.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../../frontend/static/assets/js/accessibility.js'),'utf8');
function environment(saved=null,storageBlocked=false){
 const ids={},events={};let data=saved;
 class El {
  constructor(id=''){this.id=id;ids[id]=this;this.hidden=false;this.inert=false;this.dataset={};this.attrs={};this.listeners={};this.textContent='';this.childNodes=[];this.isConnected=true;this.bars=[];const props={};this.style={overflow:'',setProperty:(k,v)=>props[k]=v,getPropertyValue:k=>props[k]||'',getPropertyPriority:()=>'',removeProperty:k=>delete props[k]};const classes=new Set();this.classList={contains:k=>classes.has(k),toggle:(k,v)=>v?classes.add(k):classes.delete(k)};}
  addEventListener(k,fn){this.listeners[k]=fn;}
  click(){this.listeners.click?.({target:this});}
  focus(){document.activeElement=this;}
  setAttribute(k,v){this.attrs[k]=v;}
  getAttribute(k){return this.attrs[k]??null;}
  querySelector(){return {textContent:this.dataset.setting};}
  querySelectorAll(){return this.bars;}
  closest(){return null;}
  matches(s){return false;}
  getClientRects(){return [{}];}
  getBoundingClientRect(){return {top:200,height:40};}
 }
 const root=new El('html'),widget=new El('rc-a11y'),panel=new El('rc-a11y-panel'),body=new El('body'),heading=new El('heading');heading.childNodes=[{nodeType:3,textContent:'Título'}];
 for(const id of ['rc-a11y-launcher','rc-a11y-close','rc-a11y-profile','rc-a11y-status','rc-a11y-mask-top','rc-a11y-mask-bottom','rc-a11y-reset','rc-profile-summary'])new El(id);
 const settings=['text','contrast','cursor','mask','dyslexia','line'].map(k=>{const b=new El(k);b.dataset.setting=k;b.bars=[new El(),new El(),new El()];new El('rc-state-'+k);return b;});
 const focusable=[ids['rc-a11y-close'],...settings,ids['rc-a11y-reset']];
 widget.querySelectorAll=()=>settings;widget.contains=e=>e===widget||settings.includes(e)||focusable.includes(e);panel.querySelectorAll=()=>focusable;
 const profile=ids['rc-a11y-profile'];Object.defineProperty(profile,'selectedOptions',{get:()=>[{textContent:profile.value}]});
 body.children=[heading,widget,ids['rc-a11y-mask-top'],ids['rc-a11y-mask-bottom']];body.querySelectorAll=()=>[heading];
 const document={documentElement:root,body,head:{append(){}},activeElement:ids['rc-a11y-launcher'],getElementById:id=>ids[id],createElement:()=>new El(),addEventListener:(k,fn,capture)=>{if(!capture)events[k]=fn;}};
 const context={document,window:{addEventListener:(k,fn)=>events[k]=fn},localStorage:{getItem:()=>{if(storageBlocked)throw Error();return data;},setItem:(k,v)=>{if(storageBlocked)throw Error();data=v;}},Node:{TEXT_NODE:3},innerHeight:800,getComputedStyle:e=>({fontSize:e.style.getPropertyValue('font-size')||'20px'}),MutationObserver:class{observe(){}},requestAnimationFrame:fn=>fn(),encodeURIComponent,console};
 vm.runInNewContext(source,context);
 return {ids,root,heading,events,document,settings,getSaved:()=>JSON.parse(data)};
}
const e=environment();const click=k=>e.ids[k].click();
click('rc-a11y-launcher');assert.equal(e.ids['rc-a11y-panel'].hidden,false);assert.equal(e.heading.inert,true);assert.equal(e.document.activeElement.id,'rc-a11y-close');
for(const size of ['25px','30px','40px','']){click('text');assert.equal(e.heading.style.getPropertyValue('font-size'),size);}
for(const level of [1,2,3,undefined]){click('contrast');assert.equal(e.root.dataset.rcContrast,level);}
click('cursor');assert.equal(e.getSaved().cursor,1);
click('dyslexia');assert.equal(e.root.classList.contains('rc-a11y-dyslexia'),true);
click('line');assert.equal(e.root.dataset.rcLine,1);
click('mask');assert.equal(e.ids['rc-a11y-mask-top'].hidden,true);
click('rc-a11y-close');assert.equal(e.ids['rc-a11y-mask-top'].hidden,false);assert.equal(e.heading.inert,false);assert.equal(e.document.activeElement.id,'rc-a11y-launcher');
const old=e.ids['rc-a11y-mask-top'].style.height;e.events.keydown({key:'ArrowDown',target:e.heading,preventDefault(){}});assert.notEqual(e.ids['rc-a11y-mask-top'].style.height,old);
const restored=environment(JSON.stringify(e.getSaved()));assert.equal(restored.root.dataset.rcLine,1);assert.equal(restored.root.classList.contains('rc-a11y-dyslexia'),true);
click('rc-a11y-launcher');e.ids['rc-a11y-profile'].value='lowvision';e.ids['rc-a11y-profile'].listeners.change();assert.equal(e.getSaved().text,2);assert.equal(e.getSaved().contrast,1);
click('rc-a11y-reset');assert.equal(e.getSaved().mask,0);assert.equal(e.root.dataset.rcContrast,undefined);assert.equal(e.heading.style.getPropertyValue('font-size'),'');
e.ids['rc-a11y-reset'].focus();let prevented=false;e.events.keydown({key:'Tab',preventDefault(){prevented=true;}});assert.equal(prevented,true);assert.equal(e.document.activeElement.id,'rc-a11y-close');
e.events.keydown({key:'Escape',preventDefault(){}});assert.equal(e.ids['rc-a11y-panel'].hidden,true);
for(const value of ['bad json','{"text":999,"contrast":-1}','null']){const bad=environment(value);assert.equal(bad.root.dataset.rcContrast,undefined);assert.equal(bad.heading.style.getPropertyValue('font-size'),'');}
const blocked=environment(null,true);blocked.ids.text.click();assert.match(blocked.ids['rc-a11y-status'].textContent,/no permite guardar/);
// La ampliacion se recalcula sin acumularse al cambiar el ancho de la ventana.
const responsive=environment();responsive.ids.text.click();responsive.events.resize();
assert.equal(responsive.heading.style.getPropertyValue('font-size'),'25px');
// La mascara no roba las flechas a controles ni a otros manejadores.
const protectedKeys=environment();protectedKeys.ids.mask.click();
const maskHeight=protectedKeys.ids['rc-a11y-mask-top'].style.height;
protectedKeys.events.keydown({key:'ArrowDown',defaultPrevented:true,target:protectedKeys.heading,preventDefault(){throw Error('No debe interceptarse');}});
assert.equal(protectedKeys.ids['rc-a11y-mask-top'].style.height,maskHeight);
protectedKeys.events.keydown({key:'ArrowDown',target:{closest:()=>({})},preventDefault(){throw Error('No debe interceptarse');}});
assert.equal(protectedKeys.ids['rc-a11y-mask-top'].style.height,maskHeight);
console.log('CORRECTO: niveles, restauración de tamaños, perfiles, máscara, persistencia, reinicio, foco, Escape/Tab y almacenamiento no disponible (DOM simulado).');
