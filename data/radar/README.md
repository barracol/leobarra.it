# RADAR — source of truth v1

La fonte canonica dei progetti è `data/radar/projects/<id>.json`: un file per progetto, indipendente dalla UI. `supplies.json` conserva ordini e inventario condivisi. `index.json` contiene solo gli identificatori, non copie degli stati. `project.schema.json` documenta il formato JSON Schema 2020-12; `context.json` conserva protocollo, relazioni e backlog storico condiviso. Tutto è versionabile con Git e trasferibile in un repository separato senza modificare il modello dati.

`archive/MyBrain_RADAR_Codex_Handoff_2026-10-06.md` è il bootstrap integrale, immutabile, non il database corrente. `context_markdown` conserva gli estratti storici senza perdita di dettaglio: i campi operativi e il changelog hanno precedenza sugli estratti quando un progetto evolve. Non aggiornare lo snapshot per simulare avanzamenti.

## Lettura e aggiornamento da agenti

1. Leggere `index.json`, quindi il singolo `projects/<id>.json` e lo schema. Non ricostruire lo stato dai componenti HTML o dalla conversazione.
2. Modificare solo il progetto interessato, preservando campi non coinvolti, contesto e stati non confermati. Identificatori e codename devono restare stabili.
3. Aggiornare `updated_at` (data reale dell'aggiornamento, `YYYY-MM-DD`) e appendere una voce datata al `changelog`, spiegando il cambiamento. Non dichiarare completato il progetto solo perché una sua attività è completata.
4. Validare, controllare il diff, quindi salvare in Git seguendo il normale processo del repository. Usare file temporaneo + rinomina atomica per scritture automatiche. In caso di concorrenza, rileggere la versione corrente e risolvere i conflitti; non sovrascrivere alla cieca.
5. Per nuovi progetti creare un JSON conforme e aggiungerne l'id all'indice. Per semplici aggiornamenti l'indice non cambia.

Comandi dalla root del repository (Python 3, libreria standard):

```sh
python3 scripts/radar.py validate
python3 scripts/radar.py export --format json > /tmp/radar-export.json
python3 scripts/radar.py export --format markdown > /tmp/radar-export.md
python3 -m unittest discover -s tests -v
python3 -m http.server 8000
# Aprire http://localhost:8000/radar/
```

L'export contiene tutti i campi dei progetti e il contesto condiviso. È una vista derivata, non una seconda fonte da aggiornare. Nessuna build o installazione npm richiesta. La dashboard usa fetch HTTP: non aprirla con file://.

## Esempio: “il case ESP8266 è stato stampato”

In `projects/foundry.json`, cercare `extensions.print_queue` per `id == "esp8266-case"`, impostare `status: "done"`, aggiungere “Case ESP8266 Solar Monitor stampato” a `completed`, aggiornare data e changelog. Rimuovere dal backlog solo attività effettivamente concluse; non dedurre che installazione/elettronica siano completate. Conservare FOUNDRY `in_progress` salvo indicazione esplicita. Non duplicare il case come nuovo progetto.

## Stati e campi

- Stati progetto: `idea`, `exploration`, `in_progress`, `paused`, `done`, `discarded` (💡 Idea, 🔎 Esplorazione, 🛠 In corso, ⏸ Pausa, ✅ Fatto, ❌ Scartato). Nessuna transizione automatica.
- `next_actions`: lista ordinata, la prima appare sulla card; lista vuota significa non definita.
- `completed`, `backlog`, `decisions`: liste testuali; non inferire risultati dalle intenzioni.
- `dependencies`: riferimenti a progetti con descrizione del rapporto. Include relazioni possibili: non è un grafo di blocchi obbligatori.
- `extensions`: oggetto estensibile per dati specifici (inventario, topologia, code). La UI mostra estensioni sconosciute come JSON, senza richiedere cambi allo schema base.
- `extensions.print_queue`: elementi con id stabile, nome, dettagli, stato `queued|in_progress|done|paused|discarded`. L'ordine dell'array è quello della coda.
- `ambiguities`: dubbi da preservare e risolvere con Leonardo.

## Migrazione e limiti

Nove progetti principali: HEARTH, ORACLE, PACER, PELOTON, BACKBONE, LabHub, FOUNDRY, PHOENIX, COCKPIT. Otto elementi print queue. RACK è deliverable BACKBONE; FOUNDRY Station ed ESP8266 Solar Monitor sono conservati nel contesto FOUNDRY. I cinque dispositivi PHOENIX conservano ruoli, diagnosi e stati nell'estratto completo; tali stati non sostituiscono quello del progetto. Inventory e media importer rimangono sotto LabHub e HEARTH. Il riferimento storico wifi-heatmapper resta in BACKBONE. Non è stato inventato uno stato autonomo per questi elementi. Le next action mancanti di HEARTH, ORACLE, PACER e PELOTON sono esplicitamente da concordare.

Le sezioni condivise e l'archivio conservano anche le indicazioni di processo e il backlog iniziale: non sono un registro vivo di completamenti della milestone RADAR.

## ChatGPT ↔ Codex ↔ sito

Oggi Codex o un altro agente con accesso al repository può leggere e modificare direttamente questi JSON. ChatGPT potrà usare lo stesso repository tramite un'integrazione Git autenticata, con lettura dei file e scrittura tramite commit/PR. Contratto consigliato: leggere progetto + revisione Git, proporre aggiornamento del solo file, validare e applicare solo se la revisione non è cambiata. Per sola lettura sono disponibili i JSON statici e gli export.

Questa milestone **non collega automaticamente ChatGPT e non espone API di scrittura**. La dashboard è di lettura; nessun dato canonico vive in localStorage. La pubblicazione avviene con il normale deploy statico del sito. Tutti i file distribuiti insieme al sito saranno pubblicamente leggibili, incluso l'archivio: per dati privati servirà un repository/storage privato con accesso autenticato e una proiezione pubblica separata; non basta nascondere una card. Nessuna credenziale deve essere inserita nel frontend.

## Gallerie fotografiche

`extensions.gallery` è una lista di oggetti con `src` (percorso dalla root del sito, sotto `assets/`), `alt`, `caption` e `source` (nome originale per tracciabilità). La dashboard mostra le foto nel dettaglio e un richiamo sulla card. Usare JPEG ottimizzati senza metadati EXIF/GPS; conservare gli originali fuori dal repository. Ogni foto si apre a dimensione completa.

## Network Inventory (BACKBONE)

`extensions.network` conserva nodi e misure dichiarati. `extensions.network_inventory` prepara il censimento fisico, senza dedurre collegamenti dal backhaul.

- `devices`: `ref` (riferimento logico stabile), `identifier` (etichetta fisica, null prima dell’assegnazione), `name`, `type`, `model`, `location`, `status`, `port_count` (null se sconosciuto), `notes`.
- `connections`: `cable_id`, `source_device`, `source_port`, `destination_device`, `destination_port`, `type` (`ethernet|wifi`), `verification_status` (`verified|hypothesized|planned`). Gli estremi referenziano `devices[].ref`; cavo e porte sconosciuti possono essere null.
- `identifier_conventions`: proposte, non etichette già assegnate.

La vista distingue tipi e stati tramite etichette; le card dei nodi usano anche colori e bordi. La lista collegamenti è inizialmente vuota: nessun grafo fisico inventato. Topologia interattiva nel backlog. Validare con `python3 scripts/radar.py validate`.

## BOM, ordini e inventario condiviso

`supplies.json` è la fonte canonica trasversale per acquisti e disponibilità: non copiare gli stessi articoli nei JSON dei progetti. Dashboard e export JSON/Markdown includono questo registro. Le milestone restano nei progetti; una consegna non completa automaticamente un’installazione.

- `orders`: `id` interno (non il numero commerciale), `store`, `ordered_at`, `status` (`ordered|partially_received|received`), `notes`.
- `items`: `id` stabile, `name`, `quantity` (null se ignota), `unit`, `category` (`consumable|equipment`), `projects` (uno o più ID progetto), `status`, `order_id` (null per disponibilità preesistenti o esclusioni), `product_url`, `expected_delivery`, `actual_delivery`, `location` (posizione fisica, null se ignota), `supplier` (fornitore quando non esiste un ordine associato), `notes`. Negozio e data ordine si leggono tramite `order_id`.
- Stati articoli: `to_buy`, `ordered`, `received`, `available`, `installed`, `excluded`. La BOM attiva mostra i primi due; l’inventario i successivi tre; gli esclusi restano separati per evitare di riproporli. `available` indica disponibilità preesistente confermata, senza inventare la data di consegna; `received` una ricezione confermata e `installed` l’installazione/uso confermato.
- Gli articoli condivisi, ad esempio P1S e calibro, hanno un solo record con più progetti; nessuna quantità viene duplicata. Le quantità ordinate sono quantità della riga, non giacenze residue misurate.
- I nodi di rete possono referenziare l’articolo con `supply_item_id`. `status: planned` descrive l’installazione non eseguita; `purchase_status: ordered` descrive l’acquisto, senza includere il nodo nella copertura operativa.

Per confermare una consegna: rileggere il registro corrente, aggiornare solo l’articolo ricevuto a `received` con `actual_delivery`, ricalcolare lo stato dell’ordine (parziale finché manca almeno una consegna), aggiornare `updated_at` e `changelog`. Non trasformare automaticamente date previste in consegne. Aggiornare esplicitamente anche azioni, cronologia e riferimenti operativi del progetto coinvolto; installazione e collaudo richiedono conferme distinte. Validare e salvare insieme in un commit atomico. Prima di creare una nuova riga, cercare nome/ID e disponibilità esistente: prima inventariare, poi acquistare.

Il registro iniziale copre l’ordine del 21 ottobre 2026 e le disponibilità confermate nello stesso aggiornamento: non è un censimento completo di tutti gli acquisti storici. Nessun numero ordine personale è pubblicato.

La BOM è esclusivamente tecnica e operativa: nessun campo economico viene registrato, mostrato o esportato. Il validatore rifiuta campi non previsti negli ordini e negli articoli. Nome e note conservano descrizione e specifiche tecniche note; le posizioni sconosciute restano null.
