# 🤖 Sistema RAG - Chat con Documenti PDF

Sistema completo di **Retrieval-Augmented Generation (RAG)** che permette di chattare con documenti PDF usando Google Gemini AI. Ispirato a NotebookLM.

---

## 🎯 Cosa Fa Questo Sistema

Permette di:
- 📤 **Caricare** documenti PDF, TXT, DOCX, Markdown
- 🔍 **Indicizzare** automaticamente i contenuti
- 💬 **Chattare** con i documenti tramite AI
- 📚 **Ottenere risposte** con riferimenti alle fonti
- 🎨 **Interfaccia web** moderna e intuitiva

---

## 📚 Documentazione

### 🚀 Per Iniziare

1. **[CHECKLIST_AVVIO.md](CHECKLIST_AVVIO.md)** ⭐ **INIZIA QUI!**
   - Checklist passo-passo per setup iniziale
   - Verifica prerequisiti
   - Primo avvio e test

2. **[GUIDA_OPERATIVA.md](GUIDA_OPERATIVA.md)**
   - Guida completa al funzionamento
   - Istruzioni operative dettagliate
   - Troubleshooting

3. **[SCHEMA_VISUALE.md](SCHEMA_VISUALE.md)**
   - Diagrammi ASCII del sistema
   - Flussi di lavoro visuali
   - Timeline e sequenze

### 🔧 Funzionalità Avanzate

4. **[AUTO_REINDEX_GUIDE.md](AUTO_REINDEX_GUIDE.md)**
   - Reindicizzazione automatica
   - Come funziona il reload
   - Test e verifica

5. **[ROADMAP.md](ROADMAP.md)**
   - Piano di sviluppo futuro
   - Funzionalità pianificate
   - Timeline implementazione

6. **[FIX_NOTES.md](FIX_NOTES.md)**
   - Fix applicati al sistema
   - Problemi risolti
   - Note tecniche

---

## ⚡ Quick Start (5 Minuti)

### 1. Prerequisiti

- ✅ Python 3.9+
- ✅ Docker Desktop (aperto e verde)
- ✅ API Key Google Gemini ([ottienila qui](https://aistudio.google.com/app/apikey))

### 2. Installazione

```cmd
# Installa dipendenze
pip install -r requirements.txt

# Crea file .env con la tua API Key
notepad .env
# Scrivi: GOOGLE_API_KEY=la_tua_chiave_qui
```

### 3. Avvio

```cmd
# Avvia tutto il sistema
start_all.bat

# Attendi 15 secondi
```

### 4. Usa il Sistema

| Servizio | URL | Credenziali |
|----------|-----|-------------|
| **💬 Chat** | http://localhost:3000 | [crea account] |
| **🔧 Admin** | http://localhost:8080 | admin / admin123 |
| **🔌 API** | http://localhost:8000 | - |

---

## 🏗️ Architettura

```
┌─────────────┐
│  Open WebUI │  ← Chat con i documenti
│ (porta 3000)│
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ API Server  │  ← Cervello RAG (Gemini + LlamaIndex)
│ (porta 8000)│
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Storage    │  ← Documenti + Indice vettoriale
│ (./documents│
│  ./storage) │
└─────────────┘

┌─────────────┐
│ Admin Panel │  ← Upload e gestione documenti
│ (porta 8080)│
└─────────────┘
```

---

## 📖 Come Funziona

### Flusso Semplificato

```
1. CARICA PDF
   Admin Panel → Upload → ./documents/

2. INDICIZZA
   Admin Panel → Reindicizza → Gemini genera embeddings → ./storage/

3. CHATTA
   Open WebUI → Domanda → API cerca chunk rilevanti → Gemini genera risposta → Risposta + Fonti
```

### Tecnologie Usate

| Componente | Tecnologia |
|------------|------------|
| **LLM** | Google Gemini 2.0 Flash |
| **Embeddings** | text-embedding-004 |
| **Framework RAG** | LlamaIndex |
| **API Server** | FastAPI + Uvicorn |
| **Admin UI** | FastAPI + Bootstrap 5 |
| **Chat UI** | Open WebUI (Docker) |
| **Vector Store** | LlamaIndex (file-based) |
| **Database** | SQLite |

---

## 📁 Struttura Progetto

```
DEDAGROUP/
├── 📄 README.md                    ← Questo file
├── 📄 CHECKLIST_AVVIO.md          ← ⭐ Inizia qui!
├── 📄 GUIDA_OPERATIVA.md          ← Guida completa
├── 📄 SCHEMA_VISUALE.md           ← Diagrammi
├── 📄 AUTO_REINDEX_GUIDE.md       ← Reindicizzazione automatica
├── 📄 ROADMAP.md                  ← Piano futuro
├── 📄 FIX_NOTES.md                ← Note tecniche
│
├── 🐍 api_server.py               ← Backend RAG (porta 8000)
├── 🐍 admin_panel.py              ← Admin UI (porta 8080)
├── 🐍 rag_prototype.py            ← Prototipo standalone
├── 🐍 test_auto_reindex.py        ← Test sistema
│
├── ⚙️ start_all.bat               ← Avvio automatico
├── 📋 requirements.txt            ← Dipendenze Python
├── 🔐 .env                        ← API Key (NON committare!)
│
├── 📁 documents/                  ← PDF caricati
├── 📁 storage/                    ← Indice vettoriale
└── 🗄️ admin.db                    ← Database SQLite
```

---

## 🎓 Tutorial Passo-Passo

### Primo Utilizzo Completo

#### 1. Setup Iniziale (10 minuti)

Segui **[CHECKLIST_AVVIO.md](CHECKLIST_AVVIO.md)** → Sezione "Prima Volta - Setup Completo"

#### 2. Carica il Tuo Primo Documento (5 minuti)

```
1. Apri http://localhost:8080
2. Login: admin / admin123
3. Trascina un PDF nella zona "Carica Documenti"
4. Clicca "Carica Documenti"
5. Clicca "Reindicizza Tutti i Documenti"
6. Attendi ~1 minuto
7. Verifica: "✅ Reindicizzazione completata!"
```

#### 3. Chatta con il Documento (2 minuti)

```
1. Apri http://localhost:3000
2. Crea account (prima volta)
3. Seleziona modello "rag-gemini"
4. Scrivi: "Riassumi i contenuti del documento"
5. Premi Invio
6. Vedi risposta con fonti!
```

---

## 💡 Esempi di Query

### Query Generiche
- "Riassumi i contenuti principali dei documenti"
- "Quali sono i temi trattati?"
- "Dammi una panoramica generale"

### Query Specifiche
- "Come si configura il parametro X?"
- "Quali sono i passaggi per installare il sistema?"
- "Cosa dice il documento riguardo alla sicurezza?"

### Query con Contesto
- "Nella sezione sulla configurazione, cosa dice riguardo ai backup?"
- "Secondo il manuale utente, come si risolve l'errore Y?"

---

## 🔧 Operazioni Comuni

### Aggiungere Nuovi Documenti

```
Admin Panel → Upload → Reindicizza → Fatto!
```

### Eliminare Documenti

```
Admin Panel → 🗑️ Elimina → Reindicizza → Fatto!
```

### Verificare Stato Sistema

```
Admin Panel → Sezione "Stato Indice RAG"
- Chunks indicizzati: [numero]
- Stato: Online/Offline
- File: [lista]
```

### Riavviare Dopo Riavvio Computer

```cmd
# Apri Docker Desktop (aspetta verde)
start_all.bat
# Attendi 15 secondi
# Fatto!
```

---

## 🐛 Problemi Comuni

| Problema | Soluzione |
|----------|-----------|
| Docker non parte | Apri Docker Desktop, attendi verde |
| API Key non trovata | Verifica file .env esista e contenga GOOGLE_API_KEY=... |
| Porta occupata | Chiudi processo che usa la porta (vedi GUIDA_OPERATIVA.md) |
| Reindicizzazione fallisce | Controlla quota Gemini, riavvia API Server |
| Chat non trova documenti | Verifica indicizzazione su /documents endpoint |

**Troubleshooting completo**: [GUIDA_OPERATIVA.md](GUIDA_OPERATIVA.md#troubleshooting)

---

## 📊 Requisiti di Sistema

### Hardware Minimo
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB (consigliati 8 GB)
- **Disco**: 2 GB liberi (più spazio per documenti)
- **Internet**: Connessione stabile (per API Gemini)

### Software
- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.9 o superiore
- **Docker**: Latest version
- **Browser**: Chrome, Firefox, Edge (moderni)

---

## 💰 Costi

### Tier Gratuito Google Gemini
- **15 richieste/minuto**
- **1,500 richieste/giorno**
- **1M token/minuto**

**Sufficiente per**:
- Sviluppo e test
- Uso personale
- Demo con clienti
- Piccoli team (5-10 utenti)

### Stima Costi Produzione
- ~€200-500/mese per 100 utenti attivi
- Vedi [ROADMAP.md](ROADMAP.md) per dettagli

---

## 🚀 Funzionalità

### ✅ Implementate

- [x] Upload documenti (PDF, TXT, DOCX, MD)
- [x] Indicizzazione automatica con Gemini
- [x] Chat interattiva con Open WebUI
- [x] Riferimenti alle fonti
- [x] Admin Panel per gestione
- [x] Reindicizzazione automatica (senza riavvio!)
- [x] API compatibile OpenAI
- [x] Persistenza indice su disco
- [x] Memoria conversazionale

### 🚧 In Sviluppo

- [ ] Multi-tenancy (utenti multipli)
- [ ] Supporto audio (trascrizione)
- [ ] OCR per PDF scansionati
- [ ] Export conversazioni
- [ ] Analytics e dashboard

Vedi [ROADMAP.md](ROADMAP.md) per piano completo

---

## 📞 Supporto

### Documentazione
- **Setup**: [CHECKLIST_AVVIO.md](CHECKLIST_AVVIO.md)
- **Uso**: [GUIDA_OPERATIVA.md](GUIDA_OPERATIVA.md)
- **Schemi**: [SCHEMA_VISUALE.md](SCHEMA_VISUALE.md)
- **Troubleshooting**: [GUIDA_OPERATIVA.md](GUIDA_OPERATIVA.md#troubleshooting)

### Risorse Esterne
- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Open WebUI Docs](https://docs.openwebui.com/)

---

## 🔐 Sicurezza

### ⚠️ Importante

- **NON committare** il file `.env` su Git
- **Cambia** le credenziali admin di default (admin/admin123)
- **Usa HTTPS** in produzione
- **Limita accesso** all'Admin Panel

### File .gitignore

```
.env
documents/
storage/
admin.db
*.pyc
__pycache__/
```

---

## 📝 Licenza

Prototipo per DEDAGROUP - Uso interno

---

## 🎯 Quick Links

| Cosa Vuoi Fare | Vai A |
|----------------|-------|
| **Primo setup** | [CHECKLIST_AVVIO.md](CHECKLIST_AVVIO.md) |
| **Capire come funziona** | [SCHEMA_VISUALE.md](SCHEMA_VISUALE.md) |
| **Usare il sistema** | [GUIDA_OPERATIVA.md](GUIDA_OPERATIVA.md) |
| **Risolvere problemi** | [GUIDA_OPERATIVA.md#troubleshooting](GUIDA_OPERATIVA.md#troubleshooting) |
| **Reindicizzazione automatica** | [AUTO_REINDEX_GUIDE.md](AUTO_REINDEX_GUIDE.md) |
| **Piano futuro** | [ROADMAP.md](ROADMAP.md) |

---

## 🏆 Caratteristiche Distintive

- ✨ **Setup in 5 minuti** con script automatico
- 🔄 **Reindicizzazione automatica** senza riavvio
- 📚 **Fonti sempre citate** in ogni risposta
- 🎨 **UI moderna** con Open WebUI
- 🔧 **Admin Panel** intuitivo
- 💾 **Persistenza** indice su disco
- 🌐 **API standard** OpenAI-compatible
- 🆓 **Tier gratuito** Gemini sufficiente per test

---

**Versione**: 2.0  
**Data**: 2025-12-03  
**Autore**: Prototipo DEDAGROUP  
**Status**: ✅ Produzione-ready per demo e test
