/* Preferencias locales. No envía datos ni depende de bibliotecas externas. */
(() => {
  'use strict';
  if (window.rcAccessibilityLoaded) return;
  window.rcAccessibilityLoaded = true;
  const root = document.documentElement;
  const widget = document.getElementById('rc-a11y');
  if (!widget) return;
  const panel = document.getElementById('rc-a11y-panel');
  const launcher = document.getElementById('rc-a11y-launcher');
  const profile = document.getElementById('rc-a11y-profile');
  const status = document.getElementById('rc-a11y-status');
  const maskTop = document.getElementById('rc-a11y-mask-top');
  const maskBottom = document.getElementById('rc-a11y-mask-bottom');
  const key = 'redcomunitaria.accessibility.v1';
  const limits = {text:3, contrast:3, cursor:2, mask:1, dyslexia:1, line:3};
  const defaults = () => ({text:0,contrast:0,cursor:0,mask:0,dyslexia:0,line:0,profile:'custom'});
  const presets = { lowvision:{text:2,contrast:1,cursor:1}, reading:{text:1,line:1,mask:1}, dyslexia:{text:1,line:1,dyslexia:1} };
  const labels = {text:['Normal','125 %','150 %','200 %'],contrast:['Original','Alto contraste claro','Alto contraste oscuro','Azul y amarillo'],cursor:['Normal','Grande','Extra grande'],mask:['Desactivada','Activada'],dyslexia:['Desactivada','Activada: fuente y espaciado de lectura'],line:['Original','1,7','2','2,3']};
  function sanitize(value) {
    const clean = defaults();
    if (!value || typeof value !== 'object') return clean;
    Object.keys(limits).forEach(k => { if (Number.isInteger(value[k]) && value[k]>=0 && value[k]<=limits[k]) clean[k]=value[k]; });
    if (value.profile==='custom' || Object.hasOwn(presets,value.profile)) clean.profile=value.profile;
    return clean;
  }
  let state;
  try { state=sanitize(JSON.parse(localStorage.getItem(key))); } catch (_) { state=defaults(); }
  let opened=false, previousFocus=null, inertStates=[], previousOverflow='', maskY=innerHeight/2;
  const originals=new Map();
  const cursorStyle=document.createElement('style');
  document.head.append(cursorStyle);
  function resizeText() {
    // Restablecer primero evita multiplicar el tamaño heredado en cada clic.
    originals.forEach((v,el) => { if(el.isConnected) { if(v.value) el.style.setProperty('font-size',v.value,v.priority); else el.style.removeProperty('font-size'); } else originals.delete(el); });
    if (!state.text) return;
    const factor=[1,1.25,1.5,2][state.text];
    const entries=[];
    document.body.querySelectorAll('*').forEach(el => {
      if (el.closest('#rc-a11y,svg,script,style') || el.matches('i,[class*="bi-"]')) return;
      if (![...el.childNodes].some(n=>n.nodeType===Node.TEXT_NODE && n.textContent.trim()) && !el.matches('input,select,textarea,button')) return;
      if (!originals.has(el)) originals.set(el,{value:el.style.getPropertyValue('font-size'),priority:el.style.getPropertyPriority('font-size')});
      entries.push([el,parseFloat(getComputedStyle(el).fontSize)*factor]);
    });
    entries.forEach(([el,size])=>el.style.setProperty('font-size',`${size}px`,'important'));
  }
  function positionMask() {
    const visible=!!state.mask && !opened;
    maskTop.hidden=maskBottom.hidden=!visible;
    const half=65;
    maskY=Math.max(0,Math.min(innerHeight,maskY));
    maskTop.style.height=`${Math.max(0,maskY-half)}px`;
    maskBottom.style.top=`${Math.min(innerHeight,maskY+half)}px`;
  }
  function apply() {
    if(state.contrast) root.dataset.rcContrast=state.contrast; else delete root.dataset.rcContrast;
    if(state.line) root.dataset.rcLine=state.line; else delete root.dataset.rcLine;
    root.classList.toggle('rc-a11y-dyslexia',!!state.dyslexia);
    // Cursor SVG local: hotspot válido y alternativa nativa si no se admite.
    const size=state.cursor===2?56:40;
    const arrow=`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 32 32"><path d="M3 2L27 20L16 21L10 30Z" fill="white" stroke="black" stroke-width="2"/></svg>`;
    cursorStyle.textContent=state.cursor?`html,html body,html body *:not(#rc-a11y):not(#rc-a11y *) {cursor:url("data:image/svg+xml,${encodeURIComponent(arrow)}") 4 3,auto!important;}`:'';
    resizeText(); positionMask();
    widget.querySelectorAll('[data-setting]').forEach(button=>{
      const k=button.dataset.setting;
      button.setAttribute('aria-pressed',String(state[k]>0));
      document.getElementById(`rc-state-${k}`).textContent=labels[k][state[k]];
      button.querySelectorAll('.rc-a11y-meter i').forEach((bar,i)=>bar.classList.toggle('active',i<state[k]));
    });
    profile.value=state.profile;
    document.getElementById('rc-profile-summary').textContent=state.profile==='custom'?'':` · ${profile.selectedOptions[0].textContent}`;
  }
  function save(message) {
    apply();
    try { localStorage.setItem(key,JSON.stringify(state)); status.textContent=message; }
    catch (_) { status.textContent=message+' El navegador no permite guardar; los ajustes durarán en esta página.'; }
  }
  function setOpen(value) {
    if(opened===value) return;
    opened=value; panel.hidden=!value;
    launcher.setAttribute('aria-expanded',String(value));
    if(value) {
      previousFocus=document.activeElement;
      previousOverflow=document.body.style.overflow;
      document.body.style.overflow='hidden';
      inertStates=[...document.body.children].filter(el=>el!==widget && !el.classList.contains('rc-a11y-mask')).map(el=>[el,el.inert]);
      inertStates.forEach(([el])=>el.inert=true);
      launcher.hidden=true;
      document.getElementById('rc-a11y-close').focus();
    } else {
      inertStates.forEach(([el,was])=>el.inert=was);
      document.body.style.overflow=previousOverflow;
      launcher.hidden=false;
      (previousFocus?.isConnected?previousFocus:launcher).focus();
    }
    positionMask();
  }
  // Evita que el control de foco de un modal Bootstrap abierto capture el panel.
  document.addEventListener('focusin',event=>{if(opened && widget.contains(event.target)) event.stopImmediatePropagation();},true);
  launcher.addEventListener('click',()=>setOpen(true));
  document.getElementById('rc-a11y-close').addEventListener('click',()=>setOpen(false));
  widget.querySelectorAll('[data-setting]').forEach(button=>button.addEventListener('click',()=>{
    const k=button.dataset.setting; state[k]=(state[k]+1)%(limits[k]+1); state.profile='custom';
    save(`${button.querySelector('span').textContent}: ${labels[k][state[k]]}.`);
  }));
  profile.addEventListener('change',()=>{ state={...defaults(),...(presets[profile.value]||{}),profile:profile.value}; save('Perfil aplicado.'); });
  document.getElementById('rc-a11y-reset').addEventListener('click',()=>{ state=defaults(); save('Se restablecieron todas las preferencias.'); });
  document.addEventListener('keydown',event=>{
    if(opened) {
      if(event.key==='Escape') { event.preventDefault(); setOpen(false); }
      if(event.key==='Tab') {
        const items=[...panel.querySelectorAll('button,summary,select')].filter(el=>el.getClientRects().length && !el.disabled);
        const first=items[0],last=items.at(-1);
        if(event.shiftKey && document.activeElement===first) {event.preventDefault();last.focus();}
        else if(!event.shiftKey && document.activeElement===last) {event.preventDefault();first.focus();}
      }
    } else if(state.mask && !event.defaultPrevented && ['ArrowUp','ArrowDown'].includes(event.key) && !event.target.closest('input,select,textarea,[contenteditable], [role="slider"],[role="spinbutton"],[role="listbox"],[role="combobox"],[role="menu"],[role="menubar"],[role="tablist"],[role="tree"],[role="grid"],[aria-expanded="true"]') && !event.altKey && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();maskY+=event.key==='ArrowUp'?-35:35;positionMask();
    }
  });
  document.addEventListener('pointermove',event=>{ if(state.mask && !opened) {maskY=event.clientY;positionMask();} },{passive:true});
  document.addEventListener('focusin',event=>{if(state.mask && !opened && !widget.contains(event.target)){const box=event.target.getBoundingClientRect(); maskY=box.top+box.height/2;positionMask();}});
  // Recalcula el texto al cambiar el ancho, para respetar los estilos adaptables.
  let resizePending=false;
  window.addEventListener('resize',()=>{
    positionMask();
    if(!state.text || resizePending) return;
    resizePending=true;
    requestAnimationFrame(()=>{resizePending=false;resizeText();});
  });
  window.addEventListener('storage',event=>{if(event.key===key || event.key===null){try{state=sanitize(JSON.parse(event.newValue));apply();}catch(_){}}});
  // Contenido agregado por tablas/formularios después de cargar la página.
  let scheduled=false;
  new MutationObserver(records=>{
    if(!state.text || scheduled || !records.some(r=>!widget.contains(r.target))) return;
    scheduled=true; requestAnimationFrame(()=>{scheduled=false;resizeText();});
  }).observe(document.body,{childList:true,subtree:true});
  apply();
})();
