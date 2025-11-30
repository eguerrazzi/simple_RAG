"""
Admin Panel - Gestione Documenti RAG
=====================================
Interfaccia web per amministratori per:
- Upload documenti (drag & drop)
- Visualizzare documenti caricati
- Eliminare documenti
- Reindicizzare

Porta: 8080
"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

# Carica variabili d'ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

DOCUMENTS_PATH = Path("./documents")
STORAGE_PATH = Path("./storage")
DATABASE_PATH = Path("./admin.db")
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}

# Credenziali admin (in produzione usare hash + database)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ============================================================================
# DATABASE
# ============================================================================

def init_db():
    """Inizializza il database SQLite"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            indexed BOOLEAN DEFAULT FALSE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS index_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            documents_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_db():
    """Ottieni connessione database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# APP FASTAPI
# ============================================================================

app = FastAPI(title="RAG Admin Panel", version="1.0.0")

# Security
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica credenziali admin"""
    is_valid_user = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_valid_pass = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_valid_user and is_valid_pass):
        raise HTTPException(
            status_code=401,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ============================================================================
# TEMPLATES HTML
# ============================================================================

# Template HTML inline (per semplicità, senza file esterni)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .drop-zone {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            transition: all 0.3s;
            cursor: pointer;
        }
        .drop-zone:hover, .drop-zone.dragover {
            background: #e8ebff;
            border-color: #764ba2;
        }
        .drop-zone i { font-size: 3rem; color: #667eea; }
        .doc-item {
            display: flex;
            align-items: center;
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }
        .doc-item:last-child { border-bottom: none; }
        .doc-icon { font-size: 1.5rem; margin-right: 15px; }
        .pdf-icon { color: #dc3545; }
        .txt-icon { color: #6c757d; }
        .md-icon { color: #0d6efd; }
        .docx-icon { color: #0d6efd; }
        .status-badge { font-size: 0.75rem; }
        .btn-reindex {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        .alert-float {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 1050;
            min-width: 300px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1">
                <i class="bi bi-gear-fill me-2"></i>RAG Admin Panel
            </span>
            <div class="d-flex align-items-center text-white">
                <span class="me-3"><i class="bi bi-person-circle me-1"></i>{{ username }}</span>
                <a href="/logout" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        {% if message %}
        <div class="alert alert-{{ message_type }} alert-dismissible fade show alert-float" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endif %}

        <div class="row">
            <!-- Upload Section -->
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-cloud-upload me-2"></i>Carica Documenti</h5>
                    </div>
                    <div class="card-body">
                        <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
                            <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                                <i class="bi bi-file-earmark-arrow-up mb-3"></i>
                                <p class="mb-2"><strong>Trascina qui i file</strong></p>
                                <p class="text-muted small mb-0">oppure clicca per selezionare</p>
                                <p class="text-muted small">PDF, TXT, DOCX, MD</p>
                                <input type="file" id="fileInput" name="files" multiple accept=".pdf,.txt,.docx,.md" hidden>
                            </div>
                            <div id="fileList" class="mt-3"></div>
                            <button type="submit" class="btn btn-primary w-100 mt-3" id="uploadBtn" disabled>
                                <i class="bi bi-upload me-2"></i>Carica Documenti
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Stats & Actions -->
            <div class="col-md-6 mb-4">
                <div class="card mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-bar-chart me-2"></i>Statistiche</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h3 class="text-primary">{{ stats.total_docs }}</h3>
                                <small class="text-muted">Documenti</small>
                            </div>
                            <div class="col-4">
                                <h3 class="text-success">{{ stats.indexed_docs }}</h3>
                                <small class="text-muted">Indicizzati</small>
                            </div>
                            <div class="col-4">
                                <h3 class="text-info">{{ "%.1f"|format(stats.total_size_mb) }} MB</h3>
                                <small class="text-muted">Dimensione</small>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="bi bi-arrow-repeat me-2"></i>Azioni</h5>
                    </div>
                    <div class="card-body">
                        <form action="/reindex" method="post" class="mb-2">
                            <button type="submit" class="btn btn-reindex text-white w-100" 
                                    onclick="this.innerHTML='<span class=\\'spinner-border spinner-border-sm me-2\\'></span>Indicizzazione in corso...'">
                                <i class="bi bi-arrow-clockwise me-2"></i>Reindicizza Tutti i Documenti
                            </button>
                        </form>
                        <p class="text-muted small mb-0">
                            <i class="bi bi-info-circle me-1"></i>
                            La reindicizzazione può richiedere alcuni minuti
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Documents List -->
        <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="bi bi-files me-2"></i>Documenti Caricati</h5>
                <span class="badge bg-secondary">{{ documents|length }} file</span>
            </div>
            <div class="card-body p-0">
                {% if documents %}
                <div class="list-group list-group-flush">
                    {% for doc in documents %}
                    <div class="doc-item">
                        {% if doc.file_type == '.pdf' %}
                        <i class="bi bi-file-earmark-pdf doc-icon pdf-icon"></i>
                        {% elif doc.file_type == '.txt' %}
                        <i class="bi bi-file-earmark-text doc-icon txt-icon"></i>
                        {% elif doc.file_type == '.md' %}
                        <i class="bi bi-file-earmark-code doc-icon md-icon"></i>
                        {% else %}
                        <i class="bi bi-file-earmark-word doc-icon docx-icon"></i>
                        {% endif %}
                        
                        <div class="flex-grow-1">
                            <strong>{{ doc.original_name }}</strong>
                            <br>
                            <small class="text-muted">
                                {{ "%.2f"|format(doc.file_size / 1024) }} KB · 
                                {{ doc.uploaded_at }}
                            </small>
                        </div>
                        
                        {% if doc.indexed %}
                        <span class="badge bg-success status-badge me-3">
                            <i class="bi bi-check-circle me-1"></i>Indicizzato
                        </span>
                        {% else %}
                        <span class="badge bg-warning status-badge me-3">
                            <i class="bi bi-clock me-1"></i>In attesa
                        </span>
                        {% endif %}
                        
                        <form action="/delete/{{ doc.id }}" method="post" class="d-inline" 
                              onsubmit="return confirm('Eliminare {{ doc.original_name }}?')">
                            <button type="submit" class="btn btn-outline-danger btn-sm">
                                <i class="bi bi-trash"></i>
                            </button>
                        </form>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="text-center py-5 text-muted">
                    <i class="bi bi-folder2-open" style="font-size: 3rem;"></i>
                    <p class="mt-3">Nessun documento caricato</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');

        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            fileInput.files = dt.files;
            updateFileList();
        });

        fileInput.addEventListener('change', updateFileList);

        function updateFileList() {
            const files = fileInput.files;
            if (files.length > 0) {
                let html = '<ul class="list-group">';
                for (let file of files) {
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-file-earmark me-2"></i>${file.name}</span>
                        <span class="badge bg-secondary">${(file.size / 1024).toFixed(1)} KB</span>
                    </li>`;
                }
                html += '</ul>';
                fileList.innerHTML = html;
                uploadBtn.disabled = false;
            } else {
                fileList.innerHTML = '';
                uploadBtn.disabled = true;
            }
        }

        // Auto-hide alerts
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert-float');
            alerts.forEach(alert => {
                new bootstrap.Alert(alert).close();
            });
        }, 5000);
    </script>
</body>
</html>
"""

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup():
    """Inizializzazione"""
    init_db()
    DOCUMENTS_PATH.mkdir(exist_ok=True)
    STORAGE_PATH.mkdir(exist_ok=True)
    print("✅ Admin Panel pronto su http://localhost:8080")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, username: str = Depends(verify_admin)):
    """Pagina principale admin"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Ottieni documenti
    cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
    documents = [dict(row) for row in cursor.fetchall()]
    
    # Statistiche
    cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN indexed THEN 1 ELSE 0 END) as indexed, COALESCE(SUM(file_size), 0) as size FROM documents")
    row = cursor.fetchone()
    stats = {
        "total_docs": row["total"] or 0,
        "indexed_docs": row["indexed"] or 0,
        "total_size_mb": (row["size"] or 0) / (1024 * 1024)
    }
    
    conn.close()
    
    # Render template
    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    html = template.render(
        username=username,
        documents=documents,
        stats=stats,
        message=request.query_params.get("message"),
        message_type=request.query_params.get("type", "info")
    )
    return HTMLResponse(content=html)


@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    username: str = Depends(verify_admin)
):
    """Upload multiplo di documenti"""
    uploaded = 0
    errors = []
    
    conn = get_db()
    cursor = conn.cursor()
    
    for file in files:
        # Verifica estensione
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"{file.filename}: formato non supportato")
            continue
        
        try:
            # Salva file
            file_path = DOCUMENTS_PATH / file.filename
            
            # Se esiste già, aggiungi timestamp
            if file_path.exists():
                stem = file_path.stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = DOCUMENTS_PATH / f"{stem}_{timestamp}{ext}"
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Registra nel database
            cursor.execute("""
                INSERT INTO documents (filename, original_name, file_size, file_type, indexed)
                VALUES (?, ?, ?, ?, FALSE)
            """, (file_path.name, file.filename, len(content), ext))
            
            uploaded += 1
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    # Messaggio di risposta
    if uploaded > 0 and not errors:
        message = f"✅ {uploaded} documento/i caricato/i con successo! Esegui la reindicizzazione."
        msg_type = "success"
    elif uploaded > 0 and errors:
        message = f"⚠️ {uploaded} caricato/i, {len(errors)} errori: {', '.join(errors)}"
        msg_type = "warning"
    else:
        message = f"❌ Errore: {', '.join(errors)}"
        msg_type = "danger"
    
    return RedirectResponse(url=f"/?message={message}&type={msg_type}", status_code=303)


@app.post("/delete/{doc_id}")
async def delete_document(doc_id: int, username: str = Depends(verify_admin)):
    """Elimina un documento"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Ottieni info documento
    cursor.execute("SELECT filename FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    
    if not row:
        return RedirectResponse(url="/?message=Documento non trovato&type=danger", status_code=303)
    
    # Elimina file
    file_path = DOCUMENTS_PATH / row["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Elimina dal database
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    return RedirectResponse(
        url=f"/?message=✅ Documento eliminato. Esegui reindicizzazione per aggiornare.&type=success",
        status_code=303
    )


@app.post("/reindex")
async def reindex(username: str = Depends(verify_admin)):
    """Reindicizza tutti i documenti"""
    
    try:
        # Crea un file flag che indica di reindicizzare
        # Il server API lo leggerà al prossimo avvio
        flag_file = Path("./REINDEX_REQUIRED")
        flag_file.write_text(f"Reindicizzazione richiesta il {datetime.now()}")
        
        # Aggiorna stato documenti nel database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET indexed = FALSE")
        cursor.execute("""
            INSERT INTO index_history (action, documents_count)
            SELECT 'reindex_requested', COUNT(*) FROM documents
        """)
        conn.commit()
        conn.close()
        
        message = "✅ Reindicizzazione programmata! Riavvia api_server.py per applicare le modifiche."
        msg_type = "success"
        
    except Exception as e:
        message = f"❌ Errore: {str(e)}"
        msg_type = "danger"
    
    return RedirectResponse(url=f"/?message={message}&type={msg_type}", status_code=303)


@app.get("/logout")
async def logout():
    """Logout (invalida sessione browser)"""
    response = RedirectResponse(url="/")
    response.status_code = 401
    response.headers["WWW-Authenticate"] = "Basic"
    return response


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "admin-panel"}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n🔧 Avvio Admin Panel su http://localhost:8080\n")
    print(f"   Username: {ADMIN_USERNAME}")
    print(f"   Password: {ADMIN_PASSWORD}\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)
