# ✅ Checklist Avvio Sistema RAG

## 📋 Prima Volta - Setup Completo

### Fase 1: Prerequisiti (15 minuti)

- [ ] **Python 3.9+ installato**
  ```cmd
  python --version
  # Deve mostrare: Python 3.9.x o superiore
  ```

- [ ] **Docker Desktop installato e APERTO**
  ```cmd
  docker --version
  # Deve mostrare: Docker version 24.x.x
  
  docker ps
  # Deve mostrare una tabella (anche vuota)
  ```

- [ ] **API Key Google Gemini ottenuta**
  - Vai su: https://aistudio.google.com/app/apikey
  - Crea API Key
  - Copia la chiave (es: AIzaSyC_xxx...)

---

### Fase 2: Installazione (10 minuti)

- [ ] **Apri CMD nella cartella progetto**
  ```cmd
  cd "C:\Users\e.guerrazzi\OneDrive - Scuola Superiore Sant'Anna\DEDAGROUP"
  ```

- [ ] **Installa dipendenze Python**
  ```cmd
  pip install -r requirements.txt
  # Attendi 2-5 minuti
  ```

- [ ] **Crea file .env con API Key**
  ```cmd
  notepad .env
  
  # Scrivi dentro:
  GOOGLE_API_KEY=AIzaSyC_xxxxxxxxxxxxxxxxxxxxxxxxxx
  
  # Salva e chiudi
  ```

- [ ] **Verifica file .env creato**
  ```cmd
  type .env
  # Deve mostrare: GOOGLE_API_KEY=AIza...
  ```

---

### Fase 3: Primo Avvio (5 minuti)

- [ ] **Docker Desktop è APERTO e VERDE**
  - Controlla icona nella system tray
  - Deve essere verde, non grigia

- [ ] **Esegui script di avvio**
  ```cmd
  start_all.bat
  ```

- [ ] **Verifica apertura 2 finestre CMD**
  - Finestra 1: "RAG API Server"
  - Finestra 2: "Admin Panel"

- [ ] **Attendi messaggi di conferma (~15 secondi)**
  - ✅ API Server: "Server pronto!"
  - ✅ Admin Panel: "Admin Panel pronto su http://localhost:8080"
  - ✅ Docker: Container "open-webui" in esecuzione

---

### Fase 4: Verifica Funzionamento (2 minuti)

- [ ] **Test API Server**
  - Apri browser: http://localhost:8000
  - Deve mostrare: `{"status":"ok","service":"RAG API Server",...}`

- [ ] **Test Admin Panel**
  - Apri browser: http://localhost:8080
  - Deve mostrare: Pagina di login
  - Login: admin / admin123
  - Deve mostrare: Dashboard admin

- [ ] **Test Open WebUI**
  - Apri browser: http://localhost:3000
  - Deve mostrare: Pagina di registrazione Open WebUI
  - Crea account con email e password

---

### Fase 5: Primo Documento (10 minuti)

- [ ] **Carica un PDF di test**
  - Admin Panel → Sezione "Carica Documenti"
  - Trascina un PDF (o clicca per selezionare)
  - Clicca "Carica Documenti"
  - Attendi: "✅ 1 documento/i caricato/i con successo!"

- [ ] **Reindicizza**
  - Admin Panel → Sezione "Azioni"
  - Clicca "Reindicizza Tutti i Documenti"
  - Attendi 30-120 secondi
  - Verifica: "✅ Reindicizzazione completata! Sistema pronto!"

- [ ] **Verifica indicizzazione**
  - Admin Panel → Sezione "Stato Indice RAG"
  - Controlla:
    - Stato indice: ✓ Online
    - Chunks indicizzati: > 0
    - File nella cartella: 1

- [ ] **Prima query di test**
  - Open WebUI (localhost:3000)
  - Seleziona modello: "rag-gemini"
  - Scrivi: "Riassumi i contenuti del documento"
  - Premi Invio
  - Verifica: Risposta con fonti

---

## 🔄 Avvio Quotidiano - Checklist Rapida

### Ogni Volta che Riavvii il Computer (2 minuti)

- [ ] **Docker Desktop aperto e verde**
  - Apri Docker Desktop
  - Attendi che l'icona diventi verde

- [ ] **Esegui start_all.bat**
  ```cmd
  cd "C:\Users\e.guerrazzi\OneDrive - Scuola Superiore Sant'Anna\DEDAGROUP"
  start_all.bat
  ```

- [ ] **Attendi 15 secondi**

- [ ] **Verifica 3 servizi attivi**
  - http://localhost:8000 → JSON OK
  - http://localhost:8080 → Login OK
  - http://localhost:3000 → Open WebUI OK

- [ ] **✅ Pronto per chattare!**

---

## 📤 Workflow Caricamento Nuovi Documenti

### Ogni Volta che Aggiungi Documenti (3-5 minuti)

- [ ] **Admin Panel (localhost:8080)**
  - Login: admin / admin123

- [ ] **Upload documenti**
  - Drag & drop PDF/TXT/DOCX/MD
  - Clicca "Carica Documenti"
  - Attendi conferma

- [ ] **Reindicizza**
  - Clicca "Reindicizza Tutti i Documenti"
  - Attendi 30-120 secondi (dipende dalla dimensione)
  - Verifica: "✅ Reindicizzazione completata!"

- [ ] **Testa su Open WebUI**
  - Vai su localhost:3000
  - Fai una domanda sui nuovi documenti
  - Verifica che le fonti includano i nuovi file

---

## 🛑 Shutdown Sistema

### Quando Hai Finito di Usare il Sistema

- [ ] **Chiudi finestre CMD**
  - Chiudi "RAG API Server" (X o Ctrl+C)
  - Chiudi "Admin Panel" (X o Ctrl+C)

- [ ] **Ferma container Docker (opzionale)**
  ```cmd
  docker stop open-webui
  ```
  - Se non lo fermi, ripartirà automaticamente al prossimo avvio

- [ ] **Chiudi Docker Desktop (opzionale)**
  - Se non lo usi per altro, puoi chiuderlo

---

## 🐛 Troubleshooting Checklist

### Se Qualcosa Non Funziona

#### Problema: API Server non parte

- [ ] Verifica API Key in .env
  ```cmd
  type .env
  # Deve mostrare: GOOGLE_API_KEY=AIza...
  ```

- [ ] Verifica che la porta 8000 sia libera
  ```cmd
  netstat -ano | findstr :8000
  # Se vedi output, la porta è occupata
  
  # Trova il PID (ultimo numero) e termina:
  taskkill /PID [numero] /F
  ```

- [ ] Riavvia manualmente
  ```cmd
  python api_server.py
  # Guarda gli errori in rosso
  ```

---

#### Problema: Admin Panel non si apre

- [ ] Verifica che la porta 8080 sia libera
  ```cmd
  netstat -ano | findstr :8080
  ```

- [ ] Riavvia manualmente
  ```cmd
  python admin_panel.py
  ```

---

#### Problema: Open WebUI non parte

- [ ] Verifica Docker in esecuzione
  ```cmd
  docker ps
  # Deve mostrare tabella
  ```

- [ ] Verifica container open-webui
  ```cmd
  docker ps | findstr open-webui
  # Deve mostrare una riga con "Up"
  ```

- [ ] Se non c'è, ricrea container
  ```cmd
  docker stop open-webui
  docker rm open-webui
  start_all.bat
  ```

---

#### Problema: Reindicizzazione fallisce

- [ ] Controlla log API Server
  - Guarda finestra CMD "RAG API Server"
  - Cerca errori in rosso

- [ ] Verifica quota Gemini
  - Vai su: https://aistudio.google.com/app/apikey
  - Controlla "Usage"
  - Limite gratuito: 15 richieste/minuto

- [ ] Riavvia API Server
  ```cmd
  # Chiudi finestra "RAG API Server"
  python api_server.py
  # Riprova reindicizzazione
  ```

---

#### Problema: Chat non trova documenti

- [ ] Verifica documenti indicizzati
  - Browser: http://localhost:8000/documents
  - Controlla:
    - "total_files" > 0
    - "index.loaded" = true
    - "index.num_chunks" > 0

- [ ] Se num_chunks = 0, reindicizza
  - Admin Panel → Reindicizza
  - Attendi conferma

- [ ] Verifica modello selezionato
  - Open WebUI → Dropdown in alto
  - Deve essere: "rag-gemini"

- [ ] Prova query più specifica
  - Invece di: "Dimmi tutto"
  - Prova: "Come si configura il parametro X?"

---

## 📊 Comandi Utili di Verifica

### Verifica Stato Sistema

```cmd
# Verifica processi Python
tasklist | findstr python
# Dovresti vedere 2 processi python.exe

# Verifica porte in uso
netstat -ano | findstr :8000
netstat -ano | findstr :8080
netstat -ano | findstr :3000

# Verifica container Docker
docker ps
# Dovresti vedere "open-webui" con status "Up"

# Verifica spazio disco
dir documents
dir storage
# Controlla dimensioni cartelle
```

### Test API Endpoints

```cmd
# Test API Server (con curl o browser)
curl http://localhost:8000/health

# Test documenti indicizzati
curl http://localhost:8000/documents

# Test modelli disponibili
curl http://localhost:8000/v1/models
```

---

## 📝 Note Importanti

### ⚠️ Da Ricordare

- **API Key**: Mai committare .env su Git!
- **Docker**: Deve essere aperto PRIMA di start_all.bat
- **Reindicizzazione**: Necessaria dopo ogni upload
- **Tempo indicizzazione**: 30-120 secondi (dipende da dimensione documenti)
- **Quota Gemini**: 15 richieste/minuto (tier gratuito)

### 💡 Best Practices

- Tieni Docker Desktop sempre aperto se usi spesso il sistema
- Carica documenti in batch e reindicizza una volta sola
- Usa query specifiche per risultati migliori
- Controlla periodicamente lo "Stato Indice RAG" nell'Admin Panel

---

## 🎯 Quick Reference

| Cosa | Dove | Credenziali |
|------|------|-------------|
| **Chat** | http://localhost:3000 | [tuo account] |
| **Admin** | http://localhost:8080 | admin / admin123 |
| **API** | http://localhost:8000 | - |
| **Documenti** | ./documents/ | - |
| **Indice** | ./storage/ | - |

---

**Ultima revisione**: 2025-12-03  
**Versione**: 1.0
