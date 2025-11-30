"""
RAG Prototype - NotebookLM-style Document Chat
===============================================
Sistema RAG completo per chattare con documenti PDF usando Google Gemini API e LlamaIndex.

Autore: Prototipo per DEDAGROUP
Data: 2025-11-27
"""

import os
from typing import List, Dict, Any
from pathlib import Path

# ============================================================================
# STEP 1: SETUP - Importazioni e Configurazione
# ============================================================================

print("📦 Installazione dipendenze necessarie...")
print("""
Per eseguire questo script, assicurati di aver installato:
    pip install llama-index
    pip install llama-index-llms-gemini
    pip install llama-index-embeddings-gemini
    pip install google-generativeai
    pip install pypdf
""")

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
        StorageContext,
        load_index_from_storage,
    )
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.response.pprint_utils import pprint_response
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Errore di importazione: {e}")
    print("Esegui: pip install llama-index llama-index-llms-google-genai llama-index-embeddings-google-genai google-generativeai pypdf")
    exit(1)

print("✅ Importazioni completate con successo!\n")


# ============================================================================
# STEP 2: CONFIGURAZIONE API
# ============================================================================

def setup_api_key() -> str:
    """
    Configura la chiave API di Google Gemini.
    In produzione, usa variabili d'ambiente per maggiore sicurezza.
    
    Returns:
        str: La chiave API configurata
    """
    print("🔑 Configurazione API Key...")
    
    # Prova a ottenere la chiave da variabile d'ambiente
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("⚠️  GOOGLE_API_KEY non trovata nelle variabili d'ambiente")
        print("Per configurarla:")
        print("  - Windows: set GOOGLE_API_KEY=your_api_key_here")
        print("  - Linux/Mac: export GOOGLE_API_KEY=your_api_key_here")
        print("\nPer questo prototipo, inserisci la chiave manualmente:")
        api_key = input("Inserisci la tua Google API Key: ").strip()
    
    if not api_key:
        raise ValueError("❌ API Key non fornita. Impossibile continuare.")
    
    # Configura l'API
    genai.configure(api_key=api_key)
    os.environ["GOOGLE_API_KEY"] = api_key
    
    print("✅ API Key configurata correttamente!\n")
    return api_key


# ============================================================================
# STEP 3: CONFIGURAZIONE MODELLI LLM ED EMBEDDINGS
# ============================================================================

def setup_models():
    """
    Configura i modelli Gemini per LLM e Embeddings.
    Imposta le configurazioni globali di LlamaIndex.
    """
    print("🤖 Configurazione modelli Gemini...")
    
    # Modello LLM per la generazione delle risposte
    llm = GoogleGenAI(
        model="gemini-2.0-flash",  # Modello stabile con buone quote gratuite
        temperature=0.1,  # Bassa temperatura per risposte più precise e deterministiche
        max_tokens=2048,  # Limite token per la risposta
    )
    
    # Modello di Embedding per la vettorizzazione
    embed_model = GoogleGenAIEmbedding(
        model_name="models/text-embedding-004",  # Modello di embedding più recente
    )
    
    # Configurazione globale di LlamaIndex
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 512  # Dimensione dei chunk di testo
    Settings.chunk_overlap = 50  # Sovrapposizione tra chunk per mantenere contesto
    
    print(f"  ✓ LLM: {llm.model}")
    print(f"  ✓ Embedding: {embed_model.model_name}")
    print(f"  ✓ Chunk size: {Settings.chunk_size}")
    print(f"  ✓ Chunk overlap: {Settings.chunk_overlap}\n")
    
    return llm, embed_model


# ============================================================================
# STEP 4: CARICAMENTO E PROCESSAMENTO DOCUMENTI
# ============================================================================

def load_documents(documents_path: str) -> List[Any]:
    """
    Carica i documenti dalla directory specificata.
    Supporta PDF, TXT, DOCX, e altri formati.
    
    Args:
        documents_path: Percorso alla directory contenente i documenti
        
    Returns:
        Lista di documenti caricati
    """
    print(f"📄 Caricamento documenti da: {documents_path}")
    
    if not os.path.exists(documents_path):
        print(f"⚠️  Directory non trovata. Creazione di: {documents_path}")
        os.makedirs(documents_path, exist_ok=True)
        print(f"📝 Inserisci i tuoi documenti PDF in: {documents_path}")
        return []
    
    # SimpleDirectoryReader carica automaticamente vari formati
    reader = SimpleDirectoryReader(
        input_dir=documents_path,
        recursive=True,  # Cerca anche nelle sottodirectory
        required_exts=[".pdf", ".txt", ".docx", ".md"],  # Formati supportati
    )
    
    try:
        documents = reader.load_data()
        print(f"✅ Caricati {len(documents)} documenti\n")
        
        # Mostra informazioni sui documenti caricati
        for i, doc in enumerate(documents, 1):
            filename = doc.metadata.get('file_name', 'Unknown')
            print(f"  {i}. {filename}")
        
        print()
        return documents
        
    except Exception as e:
        print(f"❌ Errore nel caricamento dei documenti: {e}")
        return []


# ============================================================================
# STEP 5: CREAZIONE INDICE VETTORIALE
# ============================================================================

def create_vector_index(documents: List[Any], persist_dir: str = "./storage") -> VectorStoreIndex:
    """
    Crea un indice vettoriale dai documenti caricati.
    L'indice viene salvato su disco per riutilizzo futuro.
    
    Args:
        documents: Lista di documenti da indicizzare
        persist_dir: Directory dove salvare l'indice
        
    Returns:
        VectorStoreIndex: Indice vettoriale creato
    """
    print("🔍 Creazione indice vettoriale...")
    
    # Verifica se esiste già un indice salvato
    if os.path.exists(persist_dir):
        try:
            print(f"  ℹ️  Trovato indice esistente in: {persist_dir}")
            print("  Vuoi riutilizzarlo? (s/n): ", end="")
            choice = input().strip().lower()
            
            if choice == 's':
                print("  📂 Caricamento indice esistente...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
                print("  ✅ Indice caricato con successo!\n")
                return index
        except Exception as e:
            print(f"  ⚠️  Errore nel caricamento dell'indice esistente: {e}")
            print("  Creazione di un nuovo indice...\n")
    
    # Crea un nuovo indice
    if not documents:
        raise ValueError("❌ Nessun documento da indicizzare!")
    
    print("  🔄 Parsing documenti in chunk...")
    # Il parser divide i documenti in chunk gestibili
    parser = SentenceSplitter(
        chunk_size=Settings.chunk_size,
        chunk_overlap=Settings.chunk_overlap
    )
    
    print("  🧮 Generazione embeddings (questo può richiedere qualche minuto)...")
    # Crea l'indice vettoriale
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[parser],
        show_progress=True,
    )
    
    # Salva l'indice su disco
    print(f"  💾 Salvataggio indice in: {persist_dir}")
    index.storage_context.persist(persist_dir=persist_dir)
    
    print("  ✅ Indice vettoriale creato e salvato!\n")
    return index


# ============================================================================
# STEP 6: CREAZIONE QUERY ENGINE
# ============================================================================

def create_query_engine(index: VectorStoreIndex, top_k: int = 3) -> RetrieverQueryEngine:
    """
    Crea il query engine per interrogare l'indice.
    
    Args:
        index: Indice vettoriale
        top_k: Numero di chunk più rilevanti da recuperare
        
    Returns:
        RetrieverQueryEngine: Engine per le query
    """
    print("⚙️  Configurazione Query Engine...")
    
    # Retriever per trovare i chunk più rilevanti
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,  # Numero di chunk da recuperare
    )
    
    # Query engine che combina retrieval e generation
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
    )
    
    print(f"  ✓ Top-K chunks: {top_k}")
    print("  ✅ Query Engine pronto!\n")
    
    return query_engine


# ============================================================================
# STEP 7: FUNZIONE DI QUERY CON RIFERIMENTI
# ============================================================================

def query_with_sources(query_engine: RetrieverQueryEngine, question: str) -> Dict[str, Any]:
    """
    Esegue una query e restituisce la risposta con i riferimenti alle fonti.
    
    Args:
        query_engine: Engine per le query
        question: Domanda dell'utente
        
    Returns:
        Dict contenente risposta e fonti
    """
    print(f"💬 Domanda: {question}\n")
    print("🔍 Ricerca nei documenti...")
    
    # Esegui la query
    response = query_engine.query(question)
    
    # Estrai la risposta
    answer = str(response)
    
    # Estrai le fonti (chunk utilizzati)
    sources = []
    if hasattr(response, 'source_nodes'):
        for i, node in enumerate(response.source_nodes, 1):
            source_info = {
                'chunk_id': i,
                'text': node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text,
                'score': node.score,
                'metadata': node.node.metadata
            }
            sources.append(source_info)
    
    return {
        'question': question,
        'answer': answer,
        'sources': sources
    }


def print_response_with_sources(result: Dict[str, Any]):
    """
    Stampa la risposta in modo formattato con i riferimenti alle fonti.
    
    Args:
        result: Dizionario con risposta e fonti
    """
    print("\n" + "="*80)
    print("📝 RISPOSTA")
    print("="*80)
    print(result['answer'])
    print("\n" + "="*80)
    print("📚 FONTI UTILIZZATE")
    print("="*80)
    
    if result['sources']:
        for source in result['sources']:
            print(f"\n🔖 Fonte #{source['chunk_id']} (Rilevanza: {source['score']:.3f})")
            
            # Mostra metadata del documento
            metadata = source['metadata']
            if 'file_name' in metadata:
                print(f"   📄 File: {metadata['file_name']}")
            if 'page_label' in metadata:
                print(f"   📖 Pagina: {metadata['page_label']}")
            
            # Mostra estratto del testo
            print(f"   📋 Estratto: {source['text']}")
    else:
        print("⚠️  Nessuna fonte specifica trovata.")
    
    print("\n" + "="*80 + "\n")


# ============================================================================
# STEP 8: INTERFACCIA CHAT INTERATTIVA
# ============================================================================

def interactive_chat(query_engine: RetrieverQueryEngine):
    """
    Avvia una sessione di chat interattiva con i documenti.
    
    Args:
        query_engine: Engine per le query
    """
    print("\n" + "="*80)
    print("💬 CHAT INTERATTIVA CON I DOCUMENTI")
    print("="*80)
    print("Digita le tue domande sui documenti caricati.")
    print("Comandi speciali:")
    print("  - 'exit' o 'quit': Esci dalla chat")
    print("  - 'clear': Pulisci lo schermo")
    print("="*80 + "\n")
    
    chat_history = []
    
    while True:
        try:
            # Input utente
            question = input("👤 Tu: ").strip()
            
            if not question:
                continue
            
            # Comandi speciali
            if question.lower() in ['exit', 'quit', 'esci']:
                print("\n👋 Arrivederci!")
                break
            
            if question.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            # Esegui la query
            result = query_with_sources(query_engine, question)
            
            # Stampa la risposta
            print(f"\n🤖 Assistente: {result['answer']}\n")
            
            # Mostra fonti in modo compatto
            if result['sources']:
                print("📚 Fonti:")
                for source in result['sources']:
                    filename = source['metadata'].get('file_name', 'Unknown')
                    page = source['metadata'].get('page_label', '?')
                    print(f"  • {filename} (pag. {page}) - Rilevanza: {source['score']:.2f}")
                print()
            
            # Salva nella cronologia
            chat_history.append(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrotta. Arrivederci!")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}\n")


# ============================================================================
# STEP 9: FUNZIONE PRINCIPALE
# ============================================================================

def main():
    """
    Funzione principale che orchestra l'intera pipeline RAG.
    """
    print("\n" + "="*80)
    print("🚀 RAG PROTOTYPE - NotebookLM Style")
    print("="*80)
    print("Sistema di chat con documenti usando Google Gemini API\n")
    
    try:
        # 1. Setup API
        api_key = setup_api_key()
        
        # 2. Configura modelli
        llm, embed_model = setup_models()
        
        # 3. Carica documenti
        documents_path = "./documents"  # Modifica questo percorso se necessario
        documents = load_documents(documents_path)
        
        if not documents:
            print("⚠️  Nessun documento trovato!")
            print(f"Inserisci i tuoi PDF in: {os.path.abspath(documents_path)}")
            print("Poi riavvia lo script.")
            return
        
        # 4. Crea indice vettoriale
        index = create_vector_index(documents)
        
        # 5. Crea query engine
        query_engine = create_query_engine(index, top_k=3)
        
        # 6. Esempio di query singola
        print("="*80)
        print("📋 ESEMPIO DI QUERY")
        print("="*80 + "\n")
        
        example_question = "Riassumi i contenuti principali dei documenti"
        result = query_with_sources(query_engine, example_question)
        print_response_with_sources(result)
        
        # 7. Avvia chat interattiva
        print("Vuoi avviare la chat interattiva? (s/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 's':
            interactive_chat(query_engine)
        else:
            print("\n✅ Prototipo completato con successo!")
            print("Per avviare la chat, esegui nuovamente lo script.\n")
        
    except Exception as e:
        print(f"\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
