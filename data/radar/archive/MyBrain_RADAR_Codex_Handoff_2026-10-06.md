# MyBrain / LeoBarra.it --- Handoff per Codex

> **Data snapshot:** 2026-10-06\
> **Scopo:** trasferire a un'istanza Codex che gestisce LeoBarra.it il
> contesto operativo dei progetti personali di Leonardo, in modo che
> sito, ChatGPT e Codex possano convergere su una fonte di verità
> condivisa.
>
> Questo documento privilegia informazioni utili ai progetti,
> all'architettura e allo sviluppo. Evita volutamente dati
> personali/sensibili non necessari al sito.

------------------------------------------------------------------------

## 1. Obiettivo: memoria condivisa ChatGPT ↔ Codex

Leonardo vuole evitare che ChatGPT e Codex abbiano due contesti
separati.

Architettura desiderata:

``` text
ChatGPT  <---->  Source of Truth / RADAR  <---->  Codex
                         |
                         v
                    LeoBarra.it
```

L'idea iniziale era usare un repository GitHub (`my-radar` o
equivalente) come source of truth versionata. Successivamente è emersa
la possibilità di usare **LeoBarra.it come frontend/dashboard del
RADAR**, mantenendo preferibilmente dati/versioning in una forma
facilmente leggibile e modificabile dagli agenti.

### Requisiti della source of truth

Per ogni progetto devono essere disponibili almeno:

-   codename/nome;
-   stato;
-   descrizione e obiettivo;
-   decisioni già prese;
-   attività completate;
-   next action;
-   backlog;
-   dipendenze da altri progetti;
-   timeline/changelog;
-   eventuali asset/documentazione collegati.

Codex dovrebbe considerare questo file come **bootstrap context** e, una
volta implementato RADAR sul sito/repository, usare il RADAR persistente
come fonte canonica.

------------------------------------------------------------------------

# 2. Protocollo RADAR

**RADAR = Registra → Articola → Decidi → Avanza → Riesamina**

Leonardo può usare espressioni come:

-   `RADAR`
-   `mettilo nel radar`
-   `Fammi il RADAR`
-   `RADAR review`

Gli stati concordati sono:

-   💡 **Idea**
-   🔎 **Esplorazione**
-   🛠 **In corso**
-   ⏸ **Pausa**
-   ✅ **Fatto**
-   ❌ **Scartato**

Approccio temporale:

1.  acquisizione del progetto a T0;
2.  primo controllo tipicamente dopo 7/14 giorni;
3.  aggiornamento durante le conversazioni;
4.  review RADAR mensile;
5.  checkpoint specifici per progetto quando utili.

Leonardo preferisce **codenames memorabili**, non ID numerici.

------------------------------------------------------------------------

# 3. Mappa progetti RADAR

## HEARTH --- HomeHub

**Stato:** 🛠 In corso

HomeHub è l'ecosistema/portale centrale della casa.

### Concetto architetturale

L'ecosistema LeoBarra/HomeHub è composto da **webapp indipendenti
collegate a HomeHub**.

Home Assistant / HAOS resta esterno all'ecosistema applicativo e può
visualizzare HomeHub nelle dashboard.

HomeHub è pensato come portale/orchestratore per:

-   profili e permessi;
-   registro applicazioni;
-   health/version check;
-   notifiche/inbox unificate;
-   ricerca globale;
-   quick actions;
-   stato del sistema;
-   backup e diagnostica coordinati;
-   deep-link stabili verso le app;
-   UI responsive/kiosk.

La logica e i dati delle singole applicazioni possono restare
distribuiti.

### Idee già discusse

-   dashboard "Oggi";
-   notifiche unificate;
-   ricerca globale / quick-add;
-   entità collegate;
-   sicurezza/permessi;
-   backup verificabili;
-   manutenzione casa;
-   progetti/giardino;
-   inventario selettivo;
-   media importer;
-   integrazione futura con ORACLE.

### Media importer HomeHub

Idea già definita per importare media da:

-   iPhone;
-   SD GoPro;
-   SD DSLR/reflex.

Workflow desiderato:

``` text
detect source
→ preview quantità/dimensione
→ import NAS
→ verifica
→ solo dopo offrire cancellazione/liberazione sorgente
```

Preservare correttamente:

-   HEIC/MOV/Live Photos iPhone;
-   MP4/LRV/THM GoPro;
-   coppie RAW+JPG DSLR.

------------------------------------------------------------------------

## ORACLE --- HomeHub AI / MCP / Voice

**Stato:** 🔎 Esplorazione

Obiettivo: aggiungere un layer AI/agent-friendly a HomeHub.

Visione:

``` text
speaker / terminale
        ↓
     ORACLE
        ↓
 ChatGPT / LLM
        ↓
 HomeHub / MCP / API
        ↓
 dati e dispositivi della casa
```

Esempio desiderato per LabHub:

> "Dove ho messo i convertitori buck?"

ORACLE dovrebbe interrogare l'inventario e rispondere con
quantità/posizione.

Possibili endpoint fisici: vecchi smartphone PHOENIX con
microfono/speaker/display.

------------------------------------------------------------------------

## PACER --- Running Dashboard

**Stato:** 🛠 In corso

Dashboard personale running.

Funzioni previste/discusse:

-   monitoraggio allenamenti;
-   analisi allenamenti tramite ChatGPT;
-   feedback sui progressi;
-   generazione piano per la settimana successiva;
-   calendario gare/eventi;
-   piano che tenga conto delle gare per evitare sovraccarico
    pre-evento.

Possibile relazione futura con PELOTON.

------------------------------------------------------------------------

## PELOTON --- Synopsys Running 2027

**Stato:** 💡 Idea

Idea discussa con il Site Manager Matteo:

-   allenamenti collettivi nel 2027;
-   partecipazione a gare come team;
-   possibile maglia team;
-   possibile uso di PACER/dashboard running.

------------------------------------------------------------------------

## BACKBONE --- Infrastruttura rete casa

**Stato:** 🛠 In corso

Obiettivo:

-   migliorare infrastruttura rete;
-   nuovo/i nodi mesh;
-   cablaggio Ethernet;
-   topologia;
-   percorsi;
-   punti rete;
-   shopping list;
-   rack.

### Rete esistente nota

-   FTTH TIM;
-   ONT separato;
-   TIM Hub+ ZXHN H2740;
-   mesh TP-Link Deco X50, 5 nodi.

È esistito anche un progetto `wifi-heatmapper` nel workspace Codex:

``` text
~/Documents/Codex/homehub-source/home-dashboard-stack/wifi-heatmapper/wifi-heatmapper
```

Mac usato: Intel x86_64.

Una precedente heatmap indicava copertura complessivamente buona, con
zone più deboli verso camera 1/balcone destro.

### Acquisti recenti BACKBONE

-   **TP-Link TL-SG608E**, Easy Smart, 8 porte Gigabit\
    → destinato al **RACK**.
-   **TP-Link LS1005G**, 5 porte Gigabit unmanaged\
    → destinato a una **cassetta di derivazione** per creare una
    diramazione locale.
-   **Mr. Tronic Cat6 50 m**, AWG24 UTP CCA\
    → già acquistato; Leonardo ha deciso di usarlo.
-   4 × **UGREEN HDMI Dummy Plug 4K60**\
    → per sistemi headless/remote use.

Topologia concettuale di una diramazione:

``` text
RACK
  |
  | Ethernet
  v
cassetta di derivazione
  |
LS1005G
  ├── tratta
  ├── tratta
  ├── tratta
  └── ...
```

### RACK

Il RACK è un deliverable fisico di BACKBONE, non un progetto separato al
momento.

Lo switch TL-SG608E 8 porte è destinato al rack.

------------------------------------------------------------------------

# 4. LabHub --- Garage / laboratorio maker

**Stato:** 🛠 In corso

LabHub è la trasformazione del garage in laboratorio efficiente per:

-   elettronica;
-   maker;
-   Home Automation;
-   networking;
-   stampa 3D;
-   inventario componenti;
-   progetti hardware.

## Stato fisico

Il garage possiede già:

-   banco lungo;
-   strumentazione elettronica;
-   saldatore;
-   alimentazione/strumenti;
-   PC/monitor;
-   pegboard;
-   cassettiere;
-   cassettini piccoli;
-   contenitori TROFAST/scatole;
-   molti componenti, moduli, cavi e utensili.

Non è un garage "da creare da zero": è già un laboratorio cresciuto per
stratificazione.

## Zonizzazione desiderata del banco

``` text
ELECTRONICS | BUILD | COMPUTING | FOUNDRY
```

Principi:

-   zona centrale BUILD da mantenere libera quando non c'è un progetto
    attivo;
-   strumenti frequenti sui pegboard;
-   materiale raro non deve occupare spazio premium;
-   separare componentistica piccola, moduli medi e materiale
    voluminoso.

## Pegboard

Idea:

-   pegboard elettronica: sonde, puntali, Dupont, USB, pinze, strumenti
    frequenti;
-   altra pegboard: IT/general tools;
-   evitare di comprare ganci IKEA costosi: **stampare ganci/supporti
    con P1S**.

## Inventario LabHub

Leonardo vuole inventariare componenti, utensili, materiali e ricambi.

Schema minimo:

``` text
categoria
descrizione
quantità
posizione
note
```

### Codifica posizioni

Possibile schema:

-   `E01...` elettronica/cassettini;
-   `M01...` moduli medi;
-   `T01...` TROFAST;
-   `P01...` pegboard;
-   `F01...` FOUNDRY.

Oppure schema gerarchico tipo:

``` text
A-03-07
```

= scaffale A → cassettiera 3 → cassetto 7.

Obiettivo finale:

``` text
ESP32 DevKit | 4 | E17
```

e ORACLE/HomeHub deve poter rispondere:

> "Sì, hai 4 ESP32, sono in LabHub E17."

## Etichettatrice

Acquistata:

**CLABEL 221B**, termica Bluetooth, bundle con 3 rotoli.

Uso previsto:

-   etichette cassetti;
-   codici posizione;
-   testo componente;
-   eventuale QR code verso scheda inventario.

------------------------------------------------------------------------

# 5. FOUNDRY --- Stampa 3D

**Stato:** 🛠 In corso

Inizialmente Leonardo stava valutando Bambu Lab A1/A1 Combo/P1S.

### Acquisto effettuato

-   **Bambu Lab P1S**
-   **PLA Basic Pumpkin Orange 10301, 1 kg**
-   **CyberBrick Time-lapse Kit**
    -   serie H2/P1/X1
    -   cavo 4-pin 260 mm
    -   ZH074

FOUNDRY è quindi passato dalla fase di scelta alla fase di
setup/ramp-up.

### Milestone iniziale

``` text
consegna
→ montaggio/setup
→ calibrazione
→ test/Benchy
→ Bambu Studio
→ prime stampe funzionali
→ primi progetti CAD personalizzati
```

## Print Queue iniziale

Questa lista è importante e va mantenuta nel RADAR.

### 1. Pegboard Kit LabHub

Prime stampe semplici:

-   ganci singoli;
-   ganci doppi;
-   supporti pinze;
-   supporti cacciaviti;
-   passacavi;
-   supporti sagomati per strumenti.

Motivazione: prime stampe funzionali economiche e utili per imparare la
macchina.

### 2. Case ESP8266 Solar Monitor

Creare un case per rendere **self-contained** il progetto ESP8266 che
monitora il pannello solare.

Requisiti da definire:

-   fissaggio PCB;
-   passaggi cavi/connettori;
-   ventilazione;
-   apertura/manutenzione;
-   eventuale fissaggio a parete/superficie.

### 3. Frame Huawei P9 / PHOENIX

Supporto a parete per il P9 usato come pulsantiera garage.

Requisiti desiderati:

-   alimentazione USB nascosta;
-   telefono estraibile;
-   accesso al power se necessario;
-   look da pannello domotico integrato.

### 4. COCKPIT --- Case Honor 90 + supporto auto

Case/supporto dedicato all'Honor 90 usato come CarPlay.

Obiettivo estetico:

-   non sembrare un portatelefono universale;
-   integrazione tipo infotainment OEM;
-   gestione cavo USB-C;
-   telefono removibile;
-   inclinazione corretta;
-   attacco specifico per la Panda.

### 5. Cable management LabHub

-   clip sotto banco;
-   fermacavi;
-   passacavi;
-   supporti alimentatori;
-   supporti ciabatte.

### 6. Organizer cassetti LabHub

Vaschette/divisori modulari progettati sulle dimensioni dei cassetti già
posseduti.

Principio: stampare dove serve geometria personalizzata, **non**
sprecare kg di PLA per sostituire economiche scatole generiche.

### 7. Supporti strumenti pegboard

Supporti custom per:

-   multimetro;
-   calibro;
-   tronchesine;
-   cavetti;
-   rotoli;
-   utensili specifici.

### 8. Accessori FOUNDRY

Dopo aver installato P1S:

-   porta utensili;
-   porta build plate;
-   contenitori nozzle/ricambi;
-   organizzazione bobine;
-   eventuali accessori per il mobile FOUNDRY.

### Ordine suggerito delle prime stampe

``` text
gancio pegboard
→ case ESP8266
→ frame P9
→ COCKPIT
```

------------------------------------------------------------------------

# 6. FOUNDRY Station --- mobile P1S

Nel garage è stato identificato uno spazio **a destra della scrivania
con monitor**.

Misure disponibili:

-   larghezza totale fino al muro: **97 cm**
-   profondità disponibile: **70 cm**

Dimensionamento desiderato indicativo:

``` text
larghezza: 80–90 cm
profondità: ~60 cm
altezza: ~75–80 cm
```

Preferenze:

-   mobile stabile e robusto;
-   non usare il banco elettronica principale;
-   storage sotto per filamenti, piastre, ricambi e utensili;
-   possibilità di usare parete soprastante;
-   evitare strutture leggere che oscillano durante le accelerazioni
    della P1S.

Leonardo non è convinto di:

-   IKEA BROR: troppo costoso;
-   IKEA METOD: estetica non gradita.

Preferenza per soluzioni Amazon / OBI / bricolage/officina, perché IKEA
non è comoda da raggiungere.

Budget discusso indicativamente: circa **80--150 €**, se possibile.

------------------------------------------------------------------------

# 7. PHOENIX --- recupero vecchi smartphone

**Stato:** 🛠 In corso

Obiettivo generale: recuperare vecchi smartphone di Silvia e
trasformarli in dispositivi utili per casa/HomeHub/LabHub.

## Inventario identificato

### Huawei P40 --- ANA-NX9

**Stato:** 🟢 funzionante e sbloccato.

Inizialmente era apparso Huawei Activation Lock, associato al numero di
Silvia; successivamente il dispositivo è stato sbloccato.

È il dispositivo più potente/pregiato del lotto e non va sprecato come
semplice pulsantiera.

Possibili ruoli:

-   pannello HomeHub premium;
-   terminale ORACLE;
-   Echo Show DIY;
-   videocitofono/monitor telecamere;
-   dashboard avanzata;
-   endpoint voice/AI.

Per ora **non assegnato definitivamente**.

Hardware noto: famiglia Huawei P40 / Kirin 990 5G, 8 GB RAM (da
verificare sulla variante se necessario).

### Huawei P9 --- EVA-L09

**Stato:** 🟢 funzionante, sbloccato.

Android/EMUI vecchi, ma questo non è un problema per il ruolo assegnato.

**Ruolo deciso: pulsantiera luci del garage/LabHub.**

Leonardo ha **già creato la dashboard** dedicata.

Approccio software:

-   thin client web;
-   pagina HomeHub/Home Assistant molto semplice;
-   kiosk/fullscreen;
-   niente notifiche;
-   niente UI Android superflua;
-   idealmente boot → dashboard;
-   niente blocco schermo;
-   comportamento robusto dopo perdita alimentazione/reboot.

Approccio hardware:

-   alimentazione permanente;
-   frame/supporto a parete stampato con P1S;
-   USB nascosta.

### Huawei P30 --- ELE-L29

**Stato:** ⏸ in stallo.

Aspetto: quello iridescente.

Problemi:

-   display interno completamente KO;
-   touch non risponde.

Scoperta importante:

-   collegato accidentalmente a una docking station USB-C collegata a
    monitor, **produce uscita video**;
-   mostra schermata Huawei Desktop/Projection grigia con ora e
    lucchetto;
-   quindi motherboard/SoC/USB-C video sono vivi.

Mouse/tastiera sulla dock non hanno consentito lo sblocco nella prova
effettuata.

È stato individuato su AliExpress un possibile:

-   AMOLED + frame;
-   circa **39 €**.

Decisione attuale:

> **non comprare ancora il display.** Prima sistemare/assegnare gli
> altri telefoni, poi decidere se investire 39 €.

Possibile uso se lasciato senza display:

-   Android box per TV garage;
-   HomeHub su monitor;
-   media box;
-   nodo headless;
-   terminale di laboratorio.

L'idea Android box TV garage è considerata interessante se si riesce a
configurarlo/sbloccarlo.

### Huawei P10 Plus --- VRY-L09

**Stato:** 🔴 da diagnosticare.

Aspetto: blu scuro.

Sintomi:

-   in carica mostra righe rosse;
-   non funziona con la stessa dock del P30;
-   non è ancora chiaro se sia solo display o problema più grave.

### Samsung Galaxy S3 Neo --- GT-I9301I

**Stato:** ☠️ sacrificabile / laboratorio.

Non vale la pena investire denaro per ripararlo.

Possibili usi:

-   teardown;
-   esperimenti;
-   donor;
-   reverse engineering;
-   test ROM/modding.

------------------------------------------------------------------------

# 8. COCKPIT --- CarPlay DIY

**Stato:** 🛠 In corso, funzionalmente riuscito.

Hardware:

-   **Honor 90**

Software:

-   **DiPlay** per trasformare Android in ricevitore CarPlay.

Risultato:

> Il proof-of-concept ha funzionato "alla perfezione".

Quindi il rischio software principale è eliminato.

## Stato corrente

``` text
Honor 90
+ DiPlay
+ iPhone
= CarPlay funzionante
```

Rimane soprattutto la parte estetico/meccanica:

-   case;
-   supporto auto;
-   gestione alimentazione/cavo;
-   integrazione con plancia;
-   look OEM.

Questa parte dipende da **FOUNDRY/P1S**.

Nota: inizialmente "case COCKPIT" e "case CarPlay Honor90 con supporto
auto" erano stati elencati separatamente; concettualmente possono essere
gestiti come un unico progetto meccanico composto da case + mounting
system.

------------------------------------------------------------------------

# 9. Relazioni fra progetti

I progetti non sono isolati.

``` text
                     ┌─────────────┐
                     │   RADAR     │
                     └──────┬──────┘
                            │
         ┌──────────────────┼───────────────────┐
         │                  │                   │
      HEARTH             LabHub             BACKBONE
         │                  │                   │
      ORACLE        ┌───────┼───────┐          RACK
         │          │       │       │
      PHOENIX    FOUNDRY  Inventory  P9 panel
                    │
              ┌─────┴──────┐
              │            │
           COCKPIT     ESP8266 case
```

Esempi concreti:

-   FOUNDRY stampa il frame del P9 di PHOENIX;
-   P9 controlla il garage/LabHub;
-   FOUNDRY stampa il case COCKPIT;
-   FOUNDRY stampa il case ESP8266 Solar Monitor;
-   CLABEL + inventario LabHub alimentano ORACLE;
-   ORACLE usa HomeHub/HEARTH;
-   BACKBONE fornisce rete affidabile a tutto l'ecosistema;
-   RACK è infrastruttura BACKBONE.

------------------------------------------------------------------------

# 10. Hardware / Home Automation rilevante

Informazioni tecniche utili per il contesto HomeHub:

## Home Assistant

Evoluzione:

-   inizialmente Raspberry Pi 3, percepito lento;
-   poi laptop con SSD.

Problemi affrontati in passato:

-   Solarman timeout;
-   SQLite;
-   riavvii;
-   backup su Drive.

## Zigbee

-   Sonoff SNZB-02P ×2;
-   segnale debole su due piani.

## Dispositivi citati

-   Shelly 1 Plus;
-   Shelly 1 Mini Gen3;
-   Shelly EM Gen3;
-   Sonoff Mini R4;
-   Sonoff Basic;
-   Vimar 03991;
-   Imou CE1P / CE2P;
-   Ezviz C6N / C8C / HP4;
-   condizionatori SmartThings;
-   Roomba / REST980;
-   inverter ZCS / Solarman.

## Dashboard

È presente anche un iPad 2018 a muro con pagine tipo:

-   Home;
-   Energia;
-   Todo;
-   Planimetrie.

------------------------------------------------------------------------

# 11. Fotovoltaico / ESP8266 Solar Monitor

Impianto noto:

-   inverter **ZCS Azzurro 1PH 1600 TL-V3**;
-   RS-232;
-   logger LSW-3 / Solarman;
-   fotovoltaico plug-in \~1,5 kW;
-   valutata in passato espansione verso 5 kW.

Esiste un progetto ESP8266 che monitora il pannello solare.

Task FOUNDRY associato:

> progettare un case che renda il progetto ESP8266 completamente
> self-contained.

------------------------------------------------------------------------

# 12. Garage: filosofia organizzativa

Principi concordati:

1.  **Non comprare organizer prima dell'inventario**, salvo esigenze
    chiare.
2.  Evitare cassetti "elettronica varia".
3.  Ogni oggetto deve avere una famiglia e, idealmente, un indirizzo.
4.  Microcomponenti → cassetti piccoli/densi.
5.  Moduli medi → cassetti/scatole medie.
6.  Materiale voluminoso/progetti → contenitori grandi.
7.  Pegboard → solo strumenti ad alta frequenza.
8.  Banco centrale → torna libero a fine progetto.
9.  Stampare organizer solo quando la geometria custom porta valore.
10. Etichette e inventario devono essere pensati insieme.

------------------------------------------------------------------------

# 13. LeoBarra.it --- direzione desiderata

LeoBarra.it può diventare la **faccia web di RADAR/MyBrain**.

Possibile prima evoluzione:

``` text
LeoBarra.it
└── RADAR
    ├── HEARTH
    ├── ORACLE
    ├── PACER
    ├── PELOTON
    ├── BACKBONE
    ├── LabHub
    ├── FOUNDRY
    ├── PHOENIX
    └── COCKPIT
```

Per ogni card/progetto potrebbe mostrare:

-   stato;
-   ultimo aggiornamento;
-   descrizione;
-   progressi;
-   prossimo passo;
-   backlog;
-   dipendenze;
-   timeline.

Possibili moduli futuri:

-   **FOUNDRY print queue**;
-   **LabHub inventory**;
-   **BACKBONE topology**;
-   **PHOENIX device inventory**;
-   stato HomeHub;
-   documentazione progetti.

### Principio importante

LeoBarra.it può essere il frontend, ma il formato dati sottostante
dovrebbe restare:

-   versionabile;
-   machine-readable;
-   facilmente modificabile da Codex;
-   facilmente leggibile da ChatGPT;
-   esportabile;
-   non legato in modo irreversibile alla UI.

Una possibile implementazione è tenere YAML/JSON/Markdown nel repository
del sito e generare la dashboard da questi dati.

------------------------------------------------------------------------

# 14. Schema dati RADAR suggerito

Esempio YAML:

``` yaml
projects:
  - id: foundry
    name: FOUNDRY
    title: Stampa 3D / maker
    status: in_progress
    updated: 2026-10-06
    objective: >
      Rendere la stampa 3D una capacità produttiva stabile del LabHub.
    completed:
      - Scelta stampante
      - Acquisto Bambu Lab P1S
    next_action:
      - Ricevere e installare P1S
      - Calibrazione e prima stampa
    dependencies:
      - labhub
    queues:
      print:
        - Pegboard hooks
        - ESP8266 solar monitor enclosure
        - Huawei P9 wall frame
        - COCKPIT Honor 90 enclosure/mount
```

Codex può cambiare lo schema, ma deve preservare la semantica.

------------------------------------------------------------------------

# 15. Snapshot operativo --- 2026-10-06

## FOUNDRY

**🛠 In corso**

-   P1S acquistata.
-   Filamento PLA Basic Pumpkin Orange acquistato.
-   CyberBrick Time-lapse Kit acquistato.
-   Print queue definita.
-   Da scegliere mobile/stazione P1S.
-   Spazio disponibile: 97 × 70 cm.

**Next:** consegna/setup P1S + mobile FOUNDRY.

## COCKPIT

**🛠 In corso**

-   Honor 90 disponibile.
-   DiPlay installato/provato.
-   CarPlay funzionante.
-   Software proof-of-concept superato.

**Next:** case/supporto auto stampato 3D.

## PHOENIX / P9

**🛠 In corso**

-   P9 funzionante e sbloccato.
-   Ruolo assegnato: pulsantiera luci garage.
-   Dashboard già creata.

**Next:** kiosk/appliance setup + frame P9 stampato 3D.

## PHOENIX / P40

**🟢 disponibile**

-   funzionante;
-   sbloccato;
-   non ancora assegnato.

**Next:** decidere ruolo premium (HomeHub/ORACLE).

## PHOENIX / P30

**⏸ Pausa**

-   motherboard viva;
-   HDMI/desktop mode funziona;
-   display/touch KO;
-   ricambio AMOLED+frame individuato \~39 €.

**Decisione:** non comprare ancora.

## PHOENIX / P10 Plus

**🔴 Diagnosi**

-   righe rosse durante carica;
-   nessuna uscita dock osservata.

**Next:** determinare se motherboard è viva.

## BACKBONE

**🛠 In corso**

Acquistati:

-   Cat6 50 m;
-   TL-SG608E 8 porte → rack;
-   LS1005G 5 porte → cassetta derivazione.

**Next:** installazione/cablaggio/topologia.

## LabHub

**🛠 In corso**

-   foto garage analizzate;
-   zonizzazione concettuale definita;
-   CLABEL 221B acquistata;
-   inventario da avviare;
-   FOUNDRY station da scegliere.

**Next:** mobile P1S + standard etichette/indirizzi + inventario.

## HEARTH

**🛠 In corso**

HomeHub rimane hub software centrale.

## ORACLE

**🔎 Esplorazione**

AI/MCP/voice layer da progettare.

## PACER

**🛠 In corso**

Running dashboard personale.

## PELOTON

**💡 Idea**

Running/team Synopsys 2027.

------------------------------------------------------------------------

# 16. Istruzioni operative per Codex

Quando lavori su LeoBarra.it:

1.  **Non inventare lo stato dei progetti.**
2.  Usa questo documento come snapshot iniziale.
3.  Se viene introdotto un datastore RADAR, migra queste informazioni
    mantenendo lo storico.
4.  Mantieni gli aggiornamenti atomici e leggibili anche senza UI.
5.  Preferisci file/schema semplici e versionabili.
6.  Non accoppiare la source of truth esclusivamente al frontend.
7.  Prevedi export Markdown/JSON/YAML.
8.  Conserva `updated_at` e, idealmente, changelog per progetto.
9.  Permetti a un agente di modificare un singolo progetto senza
    riscrivere tutto.
10. Considera in futuro accesso autenticato per dati privati/non
    pubblici.

### Prima milestone suggerita per LeoBarra.it

Creare una pagina **RADAR** che:

-   carica i progetti da dati strutturati;
-   mostra card ordinate per stato;
-   apre dettaglio progetto;
-   mostra next action e dipendenze;
-   espone timeline/changelog;
-   include FOUNDRY print queue;
-   è progettata in modo che i dati possano essere aggiornati da Codex
    senza modificare componenti UI.

------------------------------------------------------------------------

# 17. Note su stile e collaborazione

Leonardo preferisce:

-   sistemi pratici, non burocratici;
-   codenames memorabili;
-   automazione reale invece di aggiornamenti manuali duplicati;
-   riuso hardware;
-   integrazione tra progetti;
-   prototipare prima di spendere;
-   evitare soluzioni costose quando una soluzione maker è ragionevole;
-   dashboard funzionali e non decorative.

Quando un progetto cambia stato, RADAR dovrebbe rifletterlo subito.

------------------------------------------------------------------------

# 18. Backlog immediato consolidato

-   [ ] Implementare RADAR condiviso su LeoBarra.it/repository.
-   [ ] Definire schema dati canonico RADAR.
-   [ ] Migrare i progetti di questo handoff.
-   [ ] Ricevere/installare/calibrare Bambu Lab P1S.
-   [ ] Scegliere mobile FOUNDRY per spazio 97 × 70 cm.
-   [ ] Stampare primi ganci pegboard.
-   [ ] Progettare case ESP8266 Solar Monitor.
-   [ ] Rendere P9 kiosk/appliance.
-   [ ] Progettare frame P9.
-   [ ] Progettare case/supporto COCKPIT Honor 90.
-   [ ] Avviare inventario LabHub con CLABEL 221B.
-   [ ] Definire codifica fisica posizioni LabHub.
-   [ ] Installare BACKBONE: rack/switch/cablaggio/diramazione.
-   [ ] Decidere ruolo definitivo del P40.
-   [ ] Diagnosticare P10 Plus.
-   [ ] Lasciare P30 in stallo finché non emerge un bisogno concreto.
-   [ ] Evolvere ORACLE verso accesso agent-friendly ai dati
    HomeHub/LabHub.

------------------------------------------------------------------------

## Fine handoff

Questo file è uno **snapshot**, non la futura fonte canonica.\
Una volta che RADAR è implementato nel repository/sito, gli
aggiornamenti dovrebbero avvenire lì e questo documento può rimanere
come bootstrap/archive.
