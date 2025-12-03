# 🚀 Guida Operativa Completa - Sistema RAG

## 📖 Indice
1. [Come Funziona il Sistema](#come-funziona)
2. [Prerequisiti](#prerequisiti)
3. [Setup Iniziale](#setup-iniziale)
4. [Avvio del Sistema](#avvio-sistema)
5. [Uso Quotidiano](#uso-quotidiano)
6. [Troubleshooting](#troubleshooting)

---

## 🧠 Come Funziona il Sistema {#come-funziona}

### Schema Architetturale Semplificato

```
┌─────────────────────────────────────────────────────────────────┐
│                         TU (UTENTE)                             │
└────────────┬────────────────────────────┬──────────────────────┘
             │                            │
             │ Browser                    │ Browser
             │ localhost:3000             │ localhost:8080
             ↓                            ↓
    ┌────────────────┐          ┌──────────────────┐
    │  OPEN WEBUI    │          │  ADMIN PANEL     │
    │  💬 Chat UI    │          │  📤 Upload Docs  │
    └────────┬───────┘          └────────┬─────────┘
             │                           │
             │ HTTP Request              │ HTTP Request
             │ "Cos'è RAG?"              │ POST /reindex
             ↓                           ↓
    ┌────────────────────────────────────────────┐
    │         RAG API SERVER (porta 8000)        │
    │  ┌──────────────────────────────────────┐  │
    │  │  FastAPI - Gestisce le richieste     │  │
    │  └──────────────┬───────────────────────┘  │
    │                 ↓                           │
    │  ┌──────────────────────────────────────┐  │
    │  │  QUERY ENGINE (LlamaIndex)           │  │
    │  │  ┌────────────┐    ┌──────────────┐  │  │
    │  │  │ RETRIEVER  │    │ GOOGLE GEMINI│  │  │
    │  │  │ Cerca docs │───→│ Genera       │  │  │
    │  │  │ rilevanti  │    │ risposta     │  │  │
    │  │  └────────────┘    └──────────────┘  │  │
    │  └──────────────────────────────────────┘  │
    └────────────────┬───────────────────────────┘
                     │
                     │ Legge/Scrive
                     ↓
         ┌───────────────────────────┐
         │   STORAGE (File System)   │
         ├───────────────────────────┤
         │ 📁 ./documents/           │ ← PDF, TXT, DOCX caricati
         │ 📁 ./storage/             │ ← Indice vettoriale
         │ 📁 admin.db               │ ← Database SQLite
         │ 📁 .env                   │ ← API Key Google
         └───────────────────────────┘
```

### Flusso di una Query (Domanda dell'Utente)

```
1. UTENTE scrive domanda su Open WebUI
   "Come faccio a configurare il sistema?"
   
2. OPEN WEBUI invia richiesta HTTP
   POST http://localhost:8000/v1/chat/completions
   
3. API SERVER riceve la domanda
   ↓
   
4. RETRIEVER cerca nei documenti
   - Converte domanda in vettore (embedding)
   - Cerca i 5 chunk più simili nell'indice
   - Trova: chunk da "manuale_utente.pdf" pagina 12
   
5. GEMINI LLM genera risposta
   - Riceve: domanda + chunk rilevanti
   - Genera: risposta basata solo sui documenti
   
6. API SERVER restituisce risposta
   {
     "answer": "Per configurare il sistema...",
     "sources": ["manuale_utente.pdf, pag. 12"]
   }
   
7. OPEN WEBUI mostra risposta all'utente
   💬 "Per configurare il sistema..."
   📚 Fonti: manuale_utente.pdf (pag. 12)
```

### Cosa Succede Durante l'Indicizzazione

```
1. ADMIN carica PDF su Admin Panel
   ↓
2. File salvato in ./documents/
   ↓
3. ADMIN clicca "Reindicizza"
   ↓
4. ADMIN PANEL chiama API Server
   POST http://localhost:8000/reload
   ↓
5. API SERVER:
   a) Legge tutti i PDF da ./documents/
   b) Divide ogni PDF in "chunk" (pezzi di 512 caratteri)
      Esempio: manuale.pdf (100 pagine) → 500 chunk
   c) Per ogni chunk, chiede a Gemini l'embedding (vettore)
      Chunk 1: "Il sistema RAG..." → [0.23, 0.45, 0.12, ...]
      Chunk 2: "Per configurare..." → [0.67, 0.21, 0.89, ...]
   d) Salva tutti i vettori in ./storage/
   ↓
6. INDICE PRONTO!
   Ora le query possono trovare chunk rilevanti
```

---

## 🔧 Prerequisiti {#prerequisiti}

### Software Necessario

| Software | Versione | Download | Scopo |
|----------|----------|----------|-------|
| **Python** | 3.9+ | [python.org](https://www.python.org/downloads/) | Eseguire API Server e Admin Panel |
| **Docker Desktop** | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) | Eseguire Open WebUI |
| **Git** (opzionale) | Latest | [git-scm.com](https://git-scm.com/) | Clonare repository |

### Account Necessari

| Servizio | Cosa serve | Come ottenerlo |
|----------|------------|----------------|
| **Google AI Studio** | API Key gratuita | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |

### Verifica Prerequisiti

```cmd
# Verifica Python
python --version
# Output atteso: Python 3.9.x o superiore

# Verifica pip
pip --version

# Verifica Docker
docker --version
# Output atteso: Docker version 24.x.x o superiore

# Verifica che Docker sia in esecuzione
docker ps
# Se vedi una tabella (anche vuota), Docker è attivo
# Se vedi errore, avvia Docker Desktop
```

---

## ⚙️ Setup Iniziale {#setup-iniziale}

### Passo 1: Ottieni API Key di Google Gemini

```
1. Vai su: https://aistudio.google.com/app/apikey
2. Accedi con il tuo account Google
3. Clicca "Create API Key"
4. Copia la chiave (es: AIzaSyC_xxxxxxxxxxxxxxxxxxxxxxxxxx)
5. CONSERVALA! La userai dopo
```

### Passo 2: Prepara il Progetto

```cmd
# Apri CMD nella cartella del progetto
cd "C:\Users\e.guerrazzi\OneDrive - Scuola Superiore Sant'Anna\DEDAGROUP"

# Verifica che ci siano i file
dir
# Dovresti vedere: api_server.py, admin_panel.py, requirements.txt, ecc.
```

### Passo 3: Installa Dipendenze Python

```cmd
# Installa tutte le librerie necessarie
pip install -r requirements.txt

# Questo installerà:
# - llama-index (framework RAG)
# - google-generativeai (API Gemini)
# - fastapi (server web)
# - streamlit (interfaccia web)
# - pypdf (lettura PDF)
# - e altre...

# ⏱️ Tempo: 2-5 minuti
```

### Passo 4: Configura API Key

**Opzione A: File .env (Consigliata)**

```cmd
# Crea file .env nella cartella del progetto
notepad .env

# Scrivi dentro (sostituisci con la TUA chiave):
GOOGLE_API_KEY=AIzaSyC_xxxxxxxxxxxxxxxxxxxxxxxxxx

# Salva e chiudi
```

**Opzione B: Variabile d'Ambiente**

```cmd
# Imposta temporaneamente (valida solo per questa sessione CMD)
set GOOGLE_API_KEY=AIzaSyC_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Passo 5: Prepara Cartelle

```cmd
# Crea cartelle se non esistono
mkdir documents
mkdir storage

# La struttura finale sarà:
# DEDAGROUP/
# ├── documents/        ← Qui metterai i PDF
# ├── storage/          ← Qui verrà salvato l'indice
# ├── api_server.py
# ├── admin_panel.py
# ├── .env              ← La tua API Key
# └── ...
```

---

## 🚀 Avvio del Sistema {#avvio-sistema}

### Metodo 1: Avvio Automatico (Consigliato)

```cmd
# 1. Assicurati che Docker Desktop sia APERTO e IN ESECUZIONE
#    (icona Docker nella system tray deve essere verde)

# 2. Esegui lo script di avvio
start_all.bat

# 3. Si apriranno 2 finestre CMD:
#    - "RAG API Server" (porta 8000)
#    - "Admin Panel" (porta 8080)

# 4. Attendi ~10-15 secondi

# 5. Vedrai i messaggi:
#    ✅ Server pronto!
#    ✅ Admin Panel pronto su http://localhost:8080
```

**Cosa fa `start_all.bat`:**

```
1. Avvia API Server (porta 8000)
   ↓
2. Avvia Admin Panel (porta 8080)
   ↓
3. Verifica che Docker sia attivo
   ↓
4. Avvia container Open WebUI (porta 3000)
   ↓
5. Mostra riepilogo porte e credenziali
```

### Metodo 2: Avvio Manuale (Per Debug)

**Finestra CMD 1 - API Server:**
```cmd
cd "C:\Users\e.guerrazzi\OneDrive - Scuola Superiore Sant'Anna\DEDAGROUP"
python api_server.py

# Output atteso:
# 🔑 API Key trovata: AIzaSyC...
# 🤖 Configurazione modello: gemini-2.0-flash
# ✅ LLM configurato
# ✅ Embedding model configurato
# ✅ Server pronto!
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**Finestra CMD 2 - Admin Panel:**
```cmd
cd "C:\Users\e.guerrazzi\OneDrive - Scuola Superiore Sant'Anna\DEDAGROUP"
python admin_panel.py

# Output atteso:
# ✅ Admin Panel pronto su http://localhost:8080
#    Username: admin
#    Password: admin123
# INFO: Uvicorn running on http://0.0.0.0:8080
```

**Finestra CMD 3 - Open WebUI (Docker):**
```cmd
# Ferma eventuali container precedenti
docker stop open-webui
docker rm open-webui

# Avvia nuovo container
docker run -d --name open-webui ^
    -p 3000:8080 ^
    -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 ^
    -e OPENAI_API_KEY=not-needed ^
    -e WEBUI_AUTH=true ^
    -e DEFAULT_MODELS=rag-gemini ^
    -v open-webui-data:/app/backend/data ^
    --add-host=host.docker.internal:host-gateway ^
    --restart unless-stopped ^
    ghcr.io/open-webui/open-webui:main

# Output atteso:
# [container ID lungo]

# Verifica che sia in esecuzione:
docker ps
# Dovresti vedere "open-webui" con status "Up"
```

### Verifica che Tutto Funzioni

**Test 1: API Server**
```
Apri browser: http://localhost:8000
Dovresti vedere: {"status":"ok","service":"RAG API Server",...}
```

**Test 2: Admin Panel**
```
Apri browser: http://localhost:8080
Dovresti vedere: Pagina di login
Username: admin
Password: admin123
```

**Test 3: Open WebUI**
```
Apri browser: http://localhost:3000
Dovresti vedere: Pagina di registrazione/login Open WebUI
```

---

## 📝 Uso Quotidiano {#uso-quotidiano}

### Workflow Completo: Dalla Configurazione alla Chat

#### FASE 1: Caricamento Documenti

```
1. Apri browser → http://localhost:8080
   
2. Login Admin Panel
   Username: admin
   Password: admin123
   
3. Sezione "Carica Documenti"
   - Trascina i tuoi PDF nella zona "drop"
   - Oppure clicca e seleziona file
   - Formati supportati: PDF, TXT, DOCX, MD
   
4. Clicca "Carica Documenti"
   ✅ Vedrai: "3 documento/i caricato/i con successo!"
   
5. I file ora sono in ./documents/
```

#### FASE 2: Indicizzazione

```
6. Nella sezione "Azioni"
   Clicca "Reindicizza Tutti i Documenti"
   
7. Attendi 30-120 secondi
   (dipende dalla dimensione dei documenti)
   
8. Vedrai messaggio:
   ✅ "Reindicizzazione completata! Sistema pronto!"
   
9. Nella sezione "Stato Indice RAG"
   Dovresti vedere:
   - Stato indice: ✓ Online
   - Chunks indicizzati: > 0 (es: 245)
   - File nella cartella: 3
```

#### FASE 3: Chat con i Documenti

```
10. Apri nuovo tab → http://localhost:3000
    
11. Prima volta? Crea account Open WebUI
    - Email: tua@email.com
    - Password: [scegli una password]
    - Nome: [tuo nome]
    
12. Seleziona modello "rag-gemini"
    (in alto a sinistra, dropdown)
    
13. Scrivi la tua domanda:
    "Riassumi i contenuti principali dei documenti"
    
14. Premi Invio
    
15. Vedrai la risposta con le fonti:
    💬 "I documenti trattano principalmente..."
    
    📚 Fonti:
    - manuale_utente.pdf (pag. 5) - Rilevanza: 0.89
    - guida_tecnica.pdf (pag. 12) - Rilevanza: 0.76
```

### Operazioni Comuni

#### Aggiungere Nuovi Documenti

```
1. Admin Panel → Carica nuovi PDF
2. Clicca "Reindicizza"
3. Attendi conferma
4. Torna su Open WebUI e chatta!
```

#### Eliminare Documenti

```
1. Admin Panel → Sezione "Documenti Caricati"
2. Trova il documento da eliminare
3. Clicca icona 🗑️ (cestino)
4. Conferma eliminazione
5. Clicca "Reindicizza" per aggiornare
```

#### Vedere Statistiche

```
Admin Panel → Sezione "Statistiche"
- Documenti totali
- Documenti indicizzati
- Dimensione totale (MB)

Admin Panel → Sezione "Stato Indice RAG"
- Chunks indicizzati
- Lista file nel sistema
- Stato online/offline
```

---

## 🐛 Troubleshooting {#troubleshooting}

### Problema: "Docker non è in esecuzione"

**Sintomo:**
```
docker: error during connect: This error may indicate that the docker daemon is not running
```

**Soluzione:**
```
1. Apri Docker Desktop
2. Attendi che l'icona diventi verde
3. Riprova: docker ps
```

---

### Problema: "API Key non trovata"

**Sintomo:**
```
❌ GOOGLE_API_KEY non trovata!
```

**Soluzione:**
```
1. Verifica che esista il file .env
   dir .env

2. Apri .env e controlla:
   notepad .env
   
3. Deve contenere:
   GOOGLE_API_KEY=AIzaSyC_xxxxxxxxxxxxxxxxxxxxxxxxxx
   
4. Riavvia api_server.py
```

---

### Problema: "Porta già in uso"

**Sintomo:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Soluzione:**
```
# Trova processo che usa la porta 8000
netstat -ano | findstr :8000

# Output: TCP 0.0.0.0:8000 ... LISTENING 12345
# Il numero finale (12345) è il PID

# Termina il processo
taskkill /PID 12345 /F

# Riavvia api_server.py
```

---

### Problema: "Open WebUI non si connette all'API"

**Sintomo:**
- Open WebUI si apre ma non vede il modello "rag-gemini"
- Errore "Connection refused"

**Soluzione:**
```
1. Verifica che API Server sia attivo:
   http://localhost:8000
   Deve rispondere con JSON

2. Verifica configurazione Docker:
   docker inspect open-webui | findstr OPENAI_API_BASE_URL
   Deve mostrare: http://host.docker.internal:8000/v1

3. Se necessario, ricrea container:
   docker stop open-webui
   docker rm open-webui
   start_all.bat
```

---

### Problema: "Reindicizzazione fallisce"

**Sintomo:**
```
⚠️ Errore durante il reload automatico
```

**Soluzione:**
```
1. Controlla log API Server (finestra CMD)
   Cerca errori in rosso

2. Verifica quota Gemini:
   https://aistudio.google.com/app/apikey
   Controlla "Usage"

3. Riavvia manualmente:
   - Chiudi finestra "RAG API Server"
   - python api_server.py
   - Riprova reindicizzazione
```

---

### Problema: "Documenti non trovati nelle risposte"

**Sintomo:**
- Chat funziona ma dice "Non trovo informazioni"
- Anche se i documenti sono stati caricati

**Soluzione:**
```
1. Verifica indicizzazione:
   http://localhost:8000/documents
   
   Controlla:
   - "total_files" > 0
   - "index.loaded" = true
   - "index.num_chunks" > 0

2. Se num_chunks = 0:
   - Admin Panel → Reindicizza
   - Attendi conferma
   - Ricontrolla /documents

3. Prova query più specifica:
   Invece di: "Dimmi tutto"
   Prova: "Come si configura il parametro X?"
```

---

## 📊 Riepilogo Porte e Servizi

| Servizio | Porta | URL | Credenziali |
|----------|-------|-----|-------------|
| **API Server** | 8000 | http://localhost:8000 | - |
| **Admin Panel** | 8080 | http://localhost:8080 | admin / admin123 |
| **Open WebUI** | 3000 | http://localhost:3000 | [crea account] |

---

## 🔄 Comandi Rapidi

```cmd
# AVVIO COMPLETO
start_all.bat

# STOP COMPLETO
# 1. Chiudi finestre CMD "RAG API Server" e "Admin Panel"
# 2. Ferma Docker:
docker stop open-webui

# RIAVVIO SOLO API SERVER
# Chiudi finestra "RAG API Server", poi:
python api_server.py

# RIAVVIO SOLO ADMIN PANEL
# Chiudi finestra "Admin Panel", poi:
python admin_panel.py

# VERIFICA STATO
docker ps                    # Container Docker
netstat -ano | findstr :8000 # API Server
netstat -ano | findstr :8080 # Admin Panel
netstat -ano | findstr :3000 # Open WebUI

# LOGS
# Guarda le finestre CMD per i log in tempo reale
```

---

## 📚 File Importanti

| File | Scopo |
|------|-------|
| `.env` | API Key Google (NON committare su Git!) |
| `documents/` | PDF e documenti caricati |
| `storage/` | Indice vettoriale (cache) |
| `admin.db` | Database SQLite (tracking documenti) |
| `start_all.bat` | Script avvio automatico |
| `requirements.txt` | Dipendenze Python |

---

## ✅ Checklist Avvio Giornaliero

```
□ Docker Desktop aperto e verde
□ File .env con API Key presente
□ Esegui: start_all.bat
□ Attendi 15 secondi
□ Verifica http://localhost:8000 → JSON OK
□ Verifica http://localhost:8080 → Login OK
□ Verifica http://localhost:3000 → Open WebUI OK
□ Pronto per chattare! 🎉
```

---

**Creato**: 2025-12-03  
**Versione**: 1.0  
**Per supporto**: Controlla i log nelle finestre CMD
