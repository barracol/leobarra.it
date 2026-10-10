'use strict';
const states = {in_progress:'🛠 In corso', exploration:'🔎 Esplorazione', idea:'💡 Idea', paused:'⏸ Pausa', done:'✅ Fatto', discarded:'❌ Scartato'};
const queueStates = {queued:'In coda', in_progress:'In stampa / lavorazione', done:'Completato', paused:'In pausa', discarded:'Scartato'};
const $ = selector => document.querySelector(selector);
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
let projects = [], context;
function listSection(title, values) {
  const section = el('section'); section.append(el('h3',title));
  if (!values.length) section.append(el('p','Non specificato nello snapshot.'));
  else { const list = el('ul'); values.forEach(v=>list.append(el('li',v))); section.append(list); }
  return section;
}
function renderCards() {
  const term = $('#search').value.toLocaleLowerCase('it');
  const filter = $('#status').value;
  const visible = projects.filter(p => (filter === 'all' || p.status === filter || (filter === 'active' && ['in_progress','exploration'].includes(p.status))) && `${p.codename} ${p.name} ${p.description}`.toLocaleLowerCase('it').includes(term));
  $('#projects').replaceChildren();
  for (const p of visible) {
    const card=el('a',undefined,'radar-card'); card.href=`#${p.id}`;
    card.append(el('span',states[p.status],'badge'),el('h2',p.codename),el('p',p.name,'name'),el('p',p.description,'description'));
    const next=el('div',undefined,'next'); next.append(el('b','PROSSIMA AZIONE'),el('p',p.next_actions[0] || 'Da concordare'));
    if (p.extensions.gallery?.length) card.append(el('p', `📷 ${p.extensions.gallery.length} foto del laboratorio`, 'gallery-hint'));
    card.append(next,el('small',`Aggiornato ${p.updated_at} · Apri progetto →`)); $('#projects').append(card);
  }
  $('#feedback').textContent=visible.length ? `${visible.length} ${visible.length === 1 ? 'progetto visibile' : 'progetti visibili'} · ${projects.filter(p=>p.status==='in_progress').length} in corso` : 'Nessun progetto corrisponde ai filtri.';
}
function renderDetail() {
  const detail=$('#detail'); detail.replaceChildren();
  const id=location.hash.slice(1);
  if (!id) {detail.hidden=true;return;}
  detail.hidden=false;
  const close=el('a','← Torna ai progetti'); close.href='#'; detail.append(close);
  const p=projects.find(p=>p.id===id);
  if (!p) {detail.append(el('h2','Progetto non trovato'));detail.focus();return;}
  detail.append(el('h2',`${p.codename} / ${p.name}`),el('p',`${states[p.status]} · Aggiornato ${p.updated_at}`),el('p',p.description),el('h3','Obiettivo'),el('p',p.objective));
  if (p.extensions.gallery?.length) {
    const gallery=el('section',undefined,'project-gallery');
    gallery.append(el('h3','Il laboratorio, in foto'));
    const grid=el('div',undefined,'gallery-grid');
    for (const photo of p.extensions.gallery) {
      // Only repository-owned assets; no arbitrary external or script URLs.
      if (!/^assets\/[a-zA-Z0-9_./-]+$/.test(photo.src) || photo.src.includes('..')) continue;
      const figure=el('figure');const link=el('a');link.href=`../${photo.src}`;
      link.target='_blank';link.rel='noopener';link.setAttribute('aria-label',`${photo.alt} — Apri foto completa`);
      const img=el('img');img.src=link.href;img.alt=photo.alt;img.loading='lazy';img.decoding='async';
      link.append(img);figure.append(link,el('figcaption',photo.caption));grid.append(figure);
    }
    gallery.append(grid);detail.append(gallery);
  }
  const columns=el('div',undefined,'detail-columns');
  for (const [key,label] of [['next_actions','Prossime azioni'],['completed','Attività completate'],['backlog','Backlog'],['decisions','Decisioni']]) columns.append(listSection(label,p[key]));
  const deps=el('section'); deps.append(el('h3','Dipendenze e relazioni'));
  if (!p.dependencies.length) deps.append(el('p','Nessuna dipendenza esplicita registrata.'));
  else {const list=el('ul');p.dependencies.forEach(d=>{const li=el('li');const link=el('a',projects.find(x=>x.id===d.project)?.codename || d.project);link.href=`#${d.project}`;li.append(link,document.createTextNode(` — ${d.description}`));list.append(li);});deps.append(list);}
  columns.append(deps,listSection('Cronologia',p.changelog.map(c=>`${c.date} — ${c.text}`))); detail.append(columns);
  if(p.ambiguities?.length) detail.append(listSection('Da chiarire',p.ambiguities));
  for(const [key,value] of Object.entries(p.extensions)) {
    if(key==='gallery') continue;
    if(key==='print_queue') {detail.append(el('h3','FOUNDRY / Print queue')); const list=el('ol',undefined,'queue');value.forEach((q,i)=>{const item=el('li');item.append(el('strong',`${i+1}. ${q.name}`),el('span',queueStates[q.status] || q.status),el('pre',q.details));list.append(item);});detail.append(list);}
    else {const extra=el('details');extra.append(el('summary',key),el('pre',JSON.stringify(value,null,2)));detail.append(extra);}
  }
  const notes=el('details');notes.append(el('summary','Contesto integrale dello snapshot · 6 ottobre 2026'),el('p','Contesto storico importato. Gli aggiornamenti successivi sono nei campi operativi e nella cronologia.'),el('pre',p.context_markdown));detail.append(notes);
  const raw=el('a','Leggi JSON del progetto ↗');raw.href=`../data/radar/projects/${p.id}.json`;detail.append(raw);
  detail.focus({preventScroll:true});detail.scrollIntoView({block:'start'});
}
async function getJSON(path) {
  const response=await fetch(path,{cache:'no-cache'});
  if(!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
async function init() {
  try {
    const index=await getJSON('../data/radar/index.json');
    if(index.schema_version!==1 || !Array.isArray(index.projects) || index.projects.some(id=>!(/^[a-z][a-z0-9-]*$/).test(id))) throw new Error('Indice non valido');
    [projects,context]=await Promise.all([Promise.all(index.projects.map(id=>getJSON(`../data/radar/projects/${id}.json`))),getJSON('../data/radar/context.json')]);
    projects.sort((a,b)=>Object.keys(states).indexOf(a.status)-Object.keys(states).indexOf(b.status) || a.codename.localeCompare(b.codename));
    for(const [key,label] of Object.entries(states)) {
      const stat=el('div');stat.append(el('strong',String(projects.filter(p=>p.status===key).length)),el('span',label));$('#summary').append(stat);
      const option=el('option',label);option.value=key;$('#status').append(option);
    }
    $('#search').addEventListener('input',renderCards);$('#status').addEventListener('change',renderCards);
    window.addEventListener('hashchange',renderDetail);
    $('#export').disabled=false;$('#export').addEventListener('click',()=>{
      const blob=new Blob([JSON.stringify({schema_version:1,projects,context},null,2)+'\n'],{type:'application/json'});
      const url=URL.createObjectURL(blob),link=el('a');link.href=url;link.download='radar-export.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
    renderCards();renderDetail();
  } catch(error) {
    $('#feedback').textContent='Impossibile caricare RADAR. Ricarica la pagina o verifica i file dati e la connessione.';
    console.error('RADAR load failed',error);
  }
}
init();
