"""
RAG API Server - OpenAI Compatible
===================================
Server FastAPI che espone il sistema RAG come API compatibile con OpenAI.
Può essere usato con Open WebUI o qualsiasi client OpenAI-compatible.

Per eseguire:
    python api_server.py
"""

import os
import time
import uuid
import traceback
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Carica variabili d'ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ File .env caricato")
except ImportError:
    print("⚠️ python-dotenv non installato, uso variabili d'ambiente di sistema")

# Importazioni LlamaIndex
try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
        StorageContext,
        load_index_from_storage,
    )
    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    import google.generativeai as genai
    print("✅ Librerie LlamaIndex importate")
except ImportError as e:
    print(f"❌ Errore: {e}")
    print("Esegui: pip install llama-index llama-index-llms-google-genai llama-index-embeddings-google-genai google-generativeai fastapi uvicorn")
    exit(1)


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

DOCUMENTS_PATH = "./documents"
PERSIST_DIR = "./storage"
MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL = "models/text-embedding-004"

# Variabili globali per il query engine
query_engine = None
index = None
llm = None
executor = ThreadPoolExecutor(max_workers=4)


# ============================================================================
# MODELLI PYDANTIC (OpenAI-compatible)
# ============================================================================

class Message(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="rag-gemini", description="Model ID")
    messages: List[Message] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(default=0.1, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=2048, ge=1)
    stream: Optional[bool] = Field(default=False)
    top_p: Optional[float] = Field(default=1.0)


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:8]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage = Field(default_factory=Usage)


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "dedagroup"


class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ============================================================================
# SETUP RAG
# ============================================================================

def setup_rag():
    """Inizializza il sistema RAG"""
    global query_engine, index, llm
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY non trovata!")
        print("   Crea un file .env con: GOOGLE_API_KEY=la_tua_chiave")
        raise ValueError("GOOGLE_API_KEY non configurata nel file .env")
    
    print(f"🔑 API Key trovata: {api_key[:10]}...")
    
    # Controlla se è richiesta reindicizzazione
    reindex_flag = Path("./REINDEX_REQUIRED")
    force_reindex = False
    if reindex_flag.exists():
        print("🔄 Reindicizzazione richiesta dall'Admin Panel!")
        force_reindex = True
        # Elimina vecchio indice
        if os.path.exists(PERSIST_DIR):
            import shutil
            shutil.rmtree(PERSIST_DIR)
            os.makedirs(PERSIST_DIR)
            print("🗑️ Vecchio indice eliminato")
        # Rimuovi il flag
        reindex_flag.unlink()
    
    # Configura API
    genai.configure(api_key=api_key)
    
    # Setup modelli
    print(f"🤖 Configurazione modello: {MODEL_NAME}")
    try:
        llm = GoogleGenAI(
            model=MODEL_NAME,
            api_key=api_key,
        )
        print("✅ LLM configurato")
    except Exception as e:
        print(f"❌ Errore configurazione LLM: {e}")
        traceback.print_exc()
        raise
    
    try:
        embed_model = GoogleGenAIEmbedding(
            model_name=EMBEDDING_MODEL,
            api_key=api_key,
        )
        print("✅ Embedding model configurato")
    except Exception as e:
        print(f"❌ Errore configurazione Embedding: {e}")
        traceback.print_exc()
        raise
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50
    
    print(f"✅ Modelli configurati: {MODEL_NAME}")
    
    # Carica o crea indice
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        try:
            print(f"📂 Caricamento indice da: {PERSIST_DIR}")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            print("✅ Indice caricato dalla cache")
        except Exception as e:
            print(f"⚠️ Errore caricamento indice: {e}")
            traceback.print_exc()
            index = None
    
    if index is None:
        # Carica documenti
        if not os.path.exists(DOCUMENTS_PATH):
            os.makedirs(DOCUMENTS_PATH, exist_ok=True)
            print(f"📁 Cartella documenti creata: {DOCUMENTS_PATH}")
        
        try:
            reader = SimpleDirectoryReader(
                input_dir=DOCUMENTS_PATH,
                recursive=True,
                required_exts=[".pdf", ".txt", ".docx", ".md"],
            )
            documents = reader.load_data()
            
            if documents:
                print(f"📄 Caricati {len(documents)} documenti")
                for doc in documents:
                    print(f"   - {doc.metadata.get('file_name', 'unknown')}")
                index = VectorStoreIndex.from_documents(documents, show_progress=True)
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                print("✅ Nuovo indice creato e salvato")
            else:
                print("⚠️ Nessun documento trovato nella cartella")
        except Exception as e:
            print(f"⚠️ Errore caricamento documenti: {e}")
            traceback.print_exc()
    
    # Crea query engine
    if index is not None:
        retriever = VectorIndexRetriever(index=index, similarity_top_k=5)  # Aumentato da 3 a 5
        
        # Prompt personalizzato per risposte più dettagliate
        from llama_index.core import PromptTemplate
        
        qa_prompt_str = (
            "Sei un assistente helpdesk esperto e cordiale. "
            "Rispondi sempre in italiano in modo chiaro, dettagliato e professionale.\n\n"
            "Informazioni di contesto dai documenti:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n\n"
            "Usando SOLO le informazioni di contesto sopra (non conoscenze esterne), "
            "rispondi alla seguente domanda in modo completo e ben formattato.\n"
            "Se la risposta contiene passaggi o istruzioni, usa elenchi numerati.\n"
            "Se non trovi informazioni sufficienti nel contesto, dillo chiaramente.\n\n"
            "Domanda: {query_str}\n\n"
            "Risposta dettagliata:"
        )
        qa_prompt = PromptTemplate(qa_prompt_str)
        
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            text_qa_template=qa_prompt,
        )
        print("✅ Query engine pronto (con prompt personalizzato)")
    else:
        print("⚠️ Query engine non disponibile (nessun documento)")


# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inizializzazione all'avvio"""
    print("\n" + "="*60)
    print("🚀 RAG API Server - Avvio")
    print("="*60 + "\n")
    try:
        setup_rag()
        print("\n" + "="*60)
        print("✅ Server pronto!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Errore durante l'avvio: {e}")
        traceback.print_exc()
    yield
    print("👋 Server in chiusura...")


app = FastAPI(
    title="RAG API Server",
    description="API compatibile OpenAI per sistema RAG con Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS per Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "RAG API Server",
        "model": MODEL_NAME,
        "rag_enabled": query_engine is not None
    }


@app.get("/v1/models", response_model=ModelsResponse)
@app.get("/api/models", response_model=ModelsResponse)
async def list_models():
    """Lista dei modelli disponibili (OpenAI-compatible)"""
    models = [
        ModelInfo(id="rag-gemini", owned_by="dedagroup"),
        ModelInfo(id="gemini-2.0-flash", owned_by="google"),
    ]
    return ModelsResponse(data=models)


def run_query_sync(user_message: str, conversation_context: str = ""):
    """Esegue la query in modo sincrono (per thread separato)"""
    # Se c'è contesto conversazione, lo aggiungiamo alla query
    if conversation_context:
        full_query = f"""Contesto della conversazione precedente:
{conversation_context}

Nuova domanda dell'utente: {user_message}

Rispondi alla nuova domanda tenendo conto del contesto precedente."""
    else:
        full_query = user_message
    
    if query_engine is not None:
        response = query_engine.query(full_query)
        answer = str(response)
        
        sources_text = ""
        if hasattr(response, 'source_nodes') and response.source_nodes:
            sources_text = "\n\n---\n📚 **Fonti:**\n"
            for i, node in enumerate(response.source_nodes, 1):
                filename = node.node.metadata.get('file_name', 'Documento')
                score = node.score if node.score else 0
                sources_text += f"- {filename} (rilevanza: {score:.2f})\n"
        
        return answer + sources_text, len(response.source_nodes) if hasattr(response, 'source_nodes') and response.source_nodes else 0
    elif llm is not None:
        response = llm.complete(full_query)
        return str(response) + "\n\n⚠️ *Risposta senza RAG (nessun documento caricato)*", 0
    else:
        return "❌ Sistema non inizializzato. Riavvia il server.", 0


@app.post("/v1/chat/completions")
@app.post("/api/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    Chat completions endpoint (OpenAI-compatible)
    Usa il sistema RAG per rispondere alle domande
    Supporta memoria conversazione tramite i messaggi precedenti
    """
    print(f"\n{'='*60}")
    print(f"📨 Nuova richiesta chat")
    print(f"{'='*60}")
    
    # Estrai messaggi e costruisci contesto conversazione
    user_message = None
    system_prompt = None
    conversation_history = []
    
    for msg in request.messages:
        if msg.role == "user":
            user_message = msg.content
            conversation_history.append(f"Utente: {msg.content}")
        elif msg.role == "assistant":
            # Rimuovi le fonti dal contesto per non inquinare
            content = msg.content.split("\n\n---\n📚 **Fonti:**")[0] if msg.content else ""
            conversation_history.append(f"Assistente: {content}")
        elif msg.role == "system":
            system_prompt = msg.content
    
    if not user_message:
        print("❌ Nessun messaggio utente trovato")
        raise HTTPException(status_code=400, detail="Nessun messaggio utente trovato")
    
    # Costruisci contesto (escludi l'ultimo messaggio che è la domanda attuale)
    # Prendi solo gli ultimi 6 messaggi per non superare limiti token
    context_messages = conversation_history[:-1][-6:] if len(conversation_history) > 1 else []
    conversation_context = "\n".join(context_messages)
    
    print(f"💬 Domanda: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
    if context_messages:
        print(f"📝 Contesto conversazione: {len(context_messages)} messaggi precedenti")
    
    try:
        print("🔍 Esecuzione query...")
        
        # Esegui la query in un thread separato per evitare conflitti asyncio
        loop = asyncio.get_event_loop()
        full_response, num_sources = await loop.run_in_executor(
            executor, 
            run_query_sync, 
            user_message,
            conversation_context
        )
        
        print(f"✅ Risposta ricevuta ({len(full_response)} caratteri)")
        if num_sources > 0:
            print(f"📚 Fonti trovate: {num_sources}")
        
        result = ChatCompletionResponse(
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=full_response),
                    finish_reason="stop"
                )
            ]
        )
        
        print(f"✅ Risposta inviata con successo")
        return result.model_dump()
        
    except Exception as e:
        print(f"❌ Errore durante la generazione: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Errore nella generazione: {str(e)}")


@app.post("/v1/embeddings")
async def create_embeddings(request: dict):
    """Endpoint embeddings (placeholder)"""
    return {"object": "list", "data": [], "model": EMBEDDING_MODEL}


@app.get("/health")
async def health_check():
    """Health check dettagliato"""
    return {
        "status": "healthy",
        "rag_enabled": query_engine is not None,
        "documents_path": DOCUMENTS_PATH,
        "index_loaded": index is not None,
        "model": MODEL_NAME
    }


@app.get("/documents")
async def list_documents():
    """Lista dei documenti indicizzati nel sistema RAG"""
    documents_list = []
    
    # Leggi documenti dalla cartella
    if os.path.exists(DOCUMENTS_PATH):
        for filename in os.listdir(DOCUMENTS_PATH):
            filepath = os.path.join(DOCUMENTS_PATH, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.pdf', '.txt', '.docx', '.md']:
                    stat = os.stat(filepath)
                    documents_list.append({
                        "filename": filename,
                        "extension": ext,
                        "size_bytes": stat.st_size,
                        "size_readable": f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024*1024 else f"{stat.st_size / (1024*1024):.1f} MB",
                        "modified": stat.st_mtime
                    })
    
    # Info sull'indice
    index_info = None
    if index is not None:
        try:
            # Ottieni info sui nodi nell'indice
            docstore = index.storage_context.docstore
            num_nodes = len(docstore.docs)
            index_info = {
                "loaded": True,
                "num_chunks": num_nodes
            }
        except:
            index_info = {"loaded": True, "num_chunks": "unknown"}
    else:
        index_info = {"loaded": False, "num_chunks": 0}
    
    return {
        "documents": documents_list,
        "total_files": len(documents_list),
        "index": index_info,
        "supported_extensions": [".pdf", ".txt", ".docx", ".md"]
    }


@app.post("/reload")
async def reload_index():
    """
    Reindicizza il sistema RAG senza riavviare il server.
    Chiamato dall'Admin Panel dopo l'upload o la reindicizzazione.
    """
    print("\n" + "="*60)
    print("🔄 RELOAD RICHIESTO - Reindicizzazione in corso...")
    print("="*60 + "\n")
    
    try:
        # Crea il flag di reindicizzazione
        reindex_flag = Path("./REINDEX_REQUIRED")
        reindex_flag.write_text(f"Reindicizzazione richiesta il {time.time()}")
        
        # Esegui setup_rag in un thread separato per non bloccare
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, setup_rag)
        
        print("\n" + "="*60)
        print("✅ RELOAD COMPLETATO - Sistema pronto!")
        print("="*60 + "\n")
        
        return {
            "status": "success",
            "message": "Reindicizzazione completata con successo",
            "index_loaded": index is not None,
            "query_engine_ready": query_engine is not None
        }
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE RELOAD: {e}\n")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la reindicizzazione: {str(e)}"
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Avvio server su http://0.0.0.0:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
