# 🔄 Reindicizzazione Automatica - Guida

## ✨ Novità Implementata

Ora quando clicchi **"Reindicizza Tutti i Documenti"** dall'Admin Panel (porta 8080), il sistema:

1. ✅ Crea il flag di reindicizzazione
2. ✅ **Chiama automaticamente l'API Server** su `POST /reload`
3. ✅ L'API Server **reindicizza in tempo reale** senza riavvio
4. ✅ Aggiorna il database con lo stato "indicizzato"
5. ✅ Ti mostra un messaggio di conferma

**Non devi più riavviare manualmente l'API Server!** 🎉

---

## 🚀 Come Usare

### 1. Installa la nuova dipendenza

```bash
pip install httpx>=0.25.0
```

Oppure reinstalla tutte le dipendenze:

```bash
pip install -r requirements.txt
```

### 2. Riavvia i servizi (solo la prima volta)

```bash
# Chiudi i vecchi processi e rilancia
start_all.bat
```

### 3. Workflow Completo

```
┌─────────────────────────────────────────────────┐
│ 1. Vai su Admin Panel (localhost:8080)         │
│    Username: admin                              │
│    Password: admin123                           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. Carica documenti (drag & drop)              │
│    - Trascina PDF/TXT/DOCX/MD                   │
│    - Clicca "Carica Documenti"                  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Clicca "Reindicizza Tutti i Documenti"      │
│    ⏳ Attendi 30-120 secondi...                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. ✅ Messaggio di conferma appare             │
│    "Reindicizzazione completata! Sistema        │
│     pronto!"                                    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 5. Vai su Open WebUI (localhost:3000)          │
│    e inizia a chattare con i documenti!         │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Dettagli Tecnici

### Nuovo Endpoint API Server

**`POST http://localhost:8000/reload`**

Questo endpoint:
- Legge il flag `REINDEX_REQUIRED`
- Elimina il vecchio indice in `./storage`
- Ricarica tutti i documenti da `./documents`
- Genera nuovi embeddings con Gemini
- Salva il nuovo indice
- Ricrea il query engine

**Timeout**: 120 secondi (2 minuti) per permettere l'indicizzazione di documenti grandi

### Gestione Errori

| Scenario | Messaggio | Azione |
|----------|-----------|--------|
| ✅ Successo | "Reindicizzazione completata! Sistema pronto!" | Tutto OK, puoi chattare |
| ⚠️ API Server offline | "API Server non raggiungibile..." | Avvia `python api_server.py` |
| ⚠️ Timeout | "Reindicizzazione in corso..." | Attendi e ricarica la pagina |
| ❌ Errore generico | "Errore durante il reload..." | Controlla i log dell'API Server |

---

## 📊 Monitoraggio

### Controlla lo stato in tempo reale

1. **Admin Panel** → Sezione "Stato Indice RAG (API Server)"
   - Mostra numero di chunks indicizzati
   - Stato online/offline
   - Lista documenti nel sistema

2. **API Server Console**
   - Vedrai i log in tempo reale:
   ```
   ============================================================
   🔄 RELOAD RICHIESTO - Reindicizzazione in corso...
   ============================================================
   
   🗑️ Vecchio indice eliminato
   📄 Caricati 3 documenti
   🧮 Generazione embeddings...
   ✅ Nuovo indice creato e salvato
   
   ============================================================
   ✅ RELOAD COMPLETATO - Sistema pronto!
   ============================================================
   ```

3. **Browser API** → `http://localhost:8000/documents`
   - JSON con tutti i documenti indicizzati
   - Info su chunks e stato indice

---

## 🎯 Vantaggi

| Prima | Dopo |
|-------|------|
| ❌ Chiudi finestra API Server | ✅ Clicca "Reindicizza" |
| ❌ Riapri CMD | ✅ Attendi 30-120 secondi |
| ❌ Esegui `python api_server.py` | ✅ Fatto! |
| ❌ Attendi avvio | |
| ⏱️ **Tempo**: ~2-3 minuti | ⏱️ **Tempo**: ~30-120 secondi |
| 🔧 **Complessità**: Media | 🔧 **Complessità**: Zero |

---

## 🐛 Troubleshooting

### Problema: "API Server non raggiungibile"

**Soluzione**:
```bash
# Verifica che API Server sia in esecuzione
# Dovresti vedere una finestra CMD con "RAG API Server"

# Se non c'è, avvialo manualmente:
python api_server.py
```

### Problema: "Timeout durante reindicizzazione"

**Causa**: Documenti molto grandi o tanti documenti

**Soluzione**: È normale! L'indicizzazione continua in background. Aspetta 1-2 minuti e:
1. Ricarica la pagina Admin Panel
2. Controlla "Stato Indice RAG" → dovrebbe mostrare chunks > 0
3. Prova a fare una query su Open WebUI

### Problema: Documenti non vengono trovati nelle query

**Soluzione**:
1. Vai su Admin Panel
2. Controlla che i documenti abbiano badge "✓ Indicizzato" verde
3. Se no, clicca di nuovo "Reindicizza"
4. Verifica su `http://localhost:8000/documents` che l'indice sia caricato

---

## 📝 Note Importanti

1. **Prima indicizzazione**: Può richiedere 1-2 minuti per documenti grandi
2. **Indicizzazioni successive**: Più veloci grazie alla cache di Gemini
3. **Limite API Gemini**: 15 richieste/minuto (tier gratuito)
4. **Documenti supportati**: PDF, TXT, DOCX, MD
5. **Dimensione massima**: Nessun limite tecnico, ma più documenti = più tempo

---

## 🚀 Prossimi Passi

Ora che hai la reindicizzazione automatica, puoi:

1. ✅ Caricare più documenti senza preoccuparti
2. ✅ Testare con documentazione reale
3. ✅ Aggiornare documenti esistenti (elimina + ricarica + reindicizza)
4. ✅ Monitorare le performance con documenti di diverse dimensioni

---

**Implementato**: 2025-12-03  
**Versione**: 2.0 - Auto-Reindex Feature
