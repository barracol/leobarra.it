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
let projects = [], context, supplies;
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
function networkTable(headers, rows) {
  const wrap=el('div',undefined,'network-table-wrap'), table=el('table');
  const head=el('thead'), tr=el('tr');
  headers.forEach(label=>{const th=el('th',label);th.scope='col';tr.append(th);});head.append(tr);table.append(head);
  const body=el('tbody');rows.forEach(row=>{const tr=el('tr');row.forEach(value=>tr.append(el('td',value ?? 'Da censire')));body.append(tr);});
  table.append(body);wrap.append(table);return wrap;
}
const supplyStates={to_evaluate:'Da valutare',to_buy:'Da acquistare',ordered:'Ordinato · in attesa di consegna',received:'Disponibile / ricevuto',in_use:'Installato / in uso',excluded:'Escluso'};
const money=value=>value==null?'Non disponibile':new Intl.NumberFormat('it-IT',{style:'currency',currency:'EUR'}).format(value);
function renderSupplies(projectId) {
  const section=el('section',undefined,'network-section');
  section.append(el('h3','BOM e inventario condiviso'));
  const items=supplies.items.filter(i=>i.projects.includes(projectId));
  for(const [title,filter] of [
    ['BOM · acquisti in corso',i=>['to_evaluate','to_buy','ordered'].includes(i.status)],
    ['Inventario · già disponibili',i=>['received','in_use'].includes(i.status)],
    ['Esclusi dagli acquisti',i=>i.status==='excluded']]) {
    const selected=items.filter(filter);if(!selected.length)continue;
    section.append(el('h4',title));
    const rows=selected.map(i=>{
      const order=supplies.orders.find(o=>o.id===i.order_id);
      return [i.name,i.category==='equipment'?'Attrezzatura riutilizzabile':'Materiale di consumo',i.quantity==null?'Da censire':`${i.quantity} ${i.unit}`,supplyStates[i.status],i.projects.map(id=>projects.find(p=>p.id===id)?.codename||id).join(', '),order?.store||'Non registrato',order?.ordered_at||'Non registrata',i.expected_delivery||'Non indicata',i.actual_delivery||'Non registrata',money(i.cost_eur),i.notes];
    });
    section.append(networkTable(['Articolo','Categoria','Quantità','Stato','Progetti','Negozio','Ordine','Consegna prevista','Consegna effettiva','Costo articolo','Note'],rows));
    const links=el('ul');for(const i of selected) {
      if(!i.product_url?.startsWith('https://'))continue;
      const li=el('li'),a=el('a',i.name+' ↗');a.href=i.product_url;a.target='_blank';a.rel='noopener noreferrer';li.append(a);links.append(li);
    }if(links.children.length)section.append(links);
  }
  section.append(el('p','Gli articoli condivisi sono registrati una sola volta. Date previste non equivalgono a consegne confermate.'));
  const ordersLink=el('a','Vedi registro ordini e totale condiviso');ordersLink.href='#orders';section.append(ordersLink);
  return section;
}
function renderOrders() {
  const section=$('#orders');section.append(el('h2','Ordini condivisi'));
  section.append(el('p','Totali degli ordini, conteggiati una sola volta. Non sono costi per progetto; i prezzi dei singoli articoli non sono disponibili.'));
  section.append(networkTable(['Negozio','Data ordine','Stato','Totale ordine','Articoli'],supplies.orders.map(o=>[o.store,o.ordered_at,{ordered:'Ordinato · in attesa di consegna',partially_received:'Ricevuto parzialmente',received:'Ricevuto'}[o.status],money(o.total_eur),supplies.items.filter(i=>i.order_id===o.id).map(i=>i.name).join('; ')])));
}

function renderNetwork(network, inventory) {
  const section=el('section',undefined,'network-section');section.append(el('h3','Rete domestica'));
  const types={wired_main:'Ethernet · principale',ethernet:'Ethernet',wifi:'Wi-Fi'};
  const grid=el('div',undefined,'network-nodes');
  for(const node of [...network.nodes,...network.planned_nodes]) {
    const planned=node.status==='planned';
    const card=el('article',undefined,`network-node ${node.connection==='wifi'?'wireless':'wired'}${planned?' planned':''}`);
    card.append(el('strong',node.name),el('p',types[node.connection]||'Da valutare'),el('small',planned?(node.purchase_status==='ordered'?'Ordinato · in attesa di consegna · non installato':'Pianificato · non acquistato/installato'):node.id==='cantina'?'Ethernet confermato dall’app Deco':'Operativo · confermato dall’utente'));
    grid.append(card);
  }
  const count=network.nodes.filter(n=>['wired_main','ethernet'].includes(n.connection)).length;
  section.append(el('p',`${count}/${network.nodes.length} nodi attuali cablati, incluso il principale. Studio pianificato escluso; questo conteggio non indica il completamento del progetto.`),grid);
  section.append(el('p','Ethernet: bordo ciano · Wi-Fi: bordo rosa · pianificato: bordo tratteggiato. Sono stati dei nodi, non collegamenti fisici tra dispositivi.'));
  if(!inventory)return section;
  section.append(el('h3','Network Inventory'),el('p',`Censimento da completare. ${inventory.phase}.`));
  section.append(networkTable(['ID fisico','Nome','Tipo','Modello','Posizione','Stato','Porte','Note'],inventory.devices.map(d=>[d.identifier,d.name,d.type==='mesh_node'?'Nodo mesh':d.type,d.model,d.location,d.status==='planned'?'Pianificato':'Operativo',d.port_count,d.notes])));
  section.append(el('h4','Collegamenti e topologia fisica'));
  if(inventory.connections.length) {
    const names=Object.fromEntries(inventory.devices.map(d=>[d.ref,d.name]));
    const status={verified:'Verificato',hypothesized:'Ipotizzato',planned:'Pianificato'};
    section.append(networkTable(['Cavo','Sorgente','Porta','Destinazione','Porta','Tipo','Verifica'],inventory.connections.map(c=>[c.cable_id,names[c.source_device]||c.source_device,c.source_port,names[c.destination_device]||c.destination_device,c.destination_port,c.type==='ethernet'?'Ethernet':'Wi-Fi',status[c.verification_status]])));
  } else section.append(el('p','Nessun collegamento fisico ancora censito: sorgenti, destinazioni e porte da rilevare. La topologia interattiva è prevista come evoluzione futura.'));
  section.append(listSection('Convenzioni proposte',Object.values(inventory.identifier_conventions)),listSection('Note inventario',inventory.notes));return section;
}

function renderDetail() {
  const detail=$('#detail'); detail.replaceChildren();
  const id=location.hash.slice(1);
  if (!id || id==='orders') {detail.hidden=true;return;}
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
  if (p.extensions.network) detail.append(renderNetwork(p.extensions.network,p.extensions.network_inventory));
  if(supplies.items.some(i=>i.projects.includes(p.id))) detail.append(renderSupplies(p.id));
  const columns=el('div',undefined,'detail-columns');
  for (const [key,label] of [['next_actions','Prossime azioni'],['completed','Attività completate'],['backlog','Backlog'],['decisions','Decisioni']]) columns.append(listSection(label,p[key]));
  const deps=el('section'); deps.append(el('h3','Dipendenze e relazioni'));
  if (!p.dependencies.length) deps.append(el('p','Nessuna dipendenza esplicita registrata.'));
  else {const list=el('ul');p.dependencies.forEach(d=>{const li=el('li');const link=el('a',projects.find(x=>x.id===d.project)?.codename || d.project);link.href=`#${d.project}`;li.append(link,document.createTextNode(` — ${d.description}`));list.append(li);});deps.append(list);}
  columns.append(deps,listSection('Cronologia',p.changelog.map(c=>`${c.date} — ${c.text}`))); detail.append(columns);
  if(p.ambiguities?.length) detail.append(listSection('Da chiarire',p.ambiguities));
  for(const [key,value] of Object.entries(p.extensions)) {
    if(['gallery','network','network_inventory'].includes(key)) continue;
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
    [projects,context,supplies]=await Promise.all([Promise.all(index.projects.map(id=>getJSON(`../data/radar/projects/${id}.json`))),getJSON('../data/radar/context.json'),getJSON('../data/radar/supplies.json')]);
    projects.sort((a,b)=>Object.keys(states).indexOf(a.status)-Object.keys(states).indexOf(b.status) || a.codename.localeCompare(b.codename));
    for(const [key,label] of Object.entries(states)) {
      const stat=el('div');stat.append(el('strong',String(projects.filter(p=>p.status===key).length)),el('span',label));$('#summary').append(stat);
      const option=el('option',label);option.value=key;$('#status').append(option);
    }
    $('#search').addEventListener('input',renderCards);$('#status').addEventListener('change',renderCards);
    window.addEventListener('hashchange',renderDetail);
    $('#export').disabled=false;$('#export').addEventListener('click',()=>{
      const blob=new Blob([JSON.stringify({schema_version:1,projects,context,supplies},null,2)+'\n'],{type:'application/json'});
      const url=URL.createObjectURL(blob),link=el('a');link.href=url;link.download='radar-export.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
    renderOrders();renderCards();renderDetail();
  } catch(error) {
    $('#feedback').textContent='Impossibile caricare RADAR. Ricarica la pagina o verifica i file dati e la connessione.';
    console.error('RADAR load failed',error);
  }
}
init();
