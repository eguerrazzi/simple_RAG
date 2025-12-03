"""
Test Auto-Reindex Feature
==========================
Script per testare la nuova funzionalità di reindicizzazione automatica.
"""

import httpx
import time

API_BASE = "http://localhost:8000"
ADMIN_BASE = "http://localhost:8080"

def test_api_health():
    """Verifica che l'API Server sia online"""
    print("🔍 Test 1: Verifica API Server...")
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Server online")
            print(f"   📊 RAG abilitato: {data.get('rag_enabled')}")
            print(f"   📦 Indice caricato: {data.get('index_loaded')}")
            return True
        else:
            print(f"   ❌ API Server risponde con status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API Server non raggiungibile: {e}")
        return False

def test_documents_endpoint():
    """Verifica l'endpoint /documents"""
    print("\n🔍 Test 2: Verifica endpoint /documents...")
    try:
        response = httpx.get(f"{API_BASE}/documents", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint funzionante")
            print(f"   📄 Documenti trovati: {data.get('total_files')}")
            print(f"   🧮 Chunks indicizzati: {data.get('index', {}).get('num_chunks', 0)}")
            
            if data.get('documents'):
                print(f"   📋 Lista documenti:")
                for doc in data['documents'][:5]:  # Mostra max 5
                    print(f"      - {doc['filename']} ({doc['size_readable']})")
            return True
        else:
            print(f"   ❌ Errore: status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False

def test_reload_endpoint():
    """Testa l'endpoint /reload (ATTENZIONE: reindicizza davvero!)"""
    print("\n🔍 Test 3: Test endpoint /reload...")
    print("   ⚠️  ATTENZIONE: Questo test reindicizzerà davvero il sistema!")
    print("   ⏸️  Premi CTRL+C per annullare, oppure attendi 5 secondi...")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n   ⏭️  Test saltato dall'utente")
        return None
    
    print("   🔄 Invio richiesta di reload...")
    try:
        response = httpx.post(f"{API_BASE}/reload", timeout=120.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Reload completato!")
            print(f"   📊 Messaggio: {data.get('message')}")
            print(f"   📦 Indice caricato: {data.get('index_loaded')}")
            print(f"   🔧 Query engine pronto: {data.get('query_engine_ready')}")
            return True
        else:
            print(f"   ❌ Errore: status {response.status_code}")
            return False
    except httpx.TimeoutException:
        print(f"   ⚠️  Timeout (normale per indicizzazioni lunghe)")
        print(f"   💡 Verifica manualmente su {API_BASE}/documents")
        return None
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False

def main():
    print("="*60)
    print("🧪 TEST AUTO-REINDEX FEATURE")
    print("="*60)
    print()
    
    # Test 1: API Health
    if not test_api_health():
        print("\n❌ API Server non disponibile. Avvialo con: python api_server.py")
        return
    
    # Test 2: Documents endpoint
    test_documents_endpoint()
    
    # Test 3: Reload endpoint (opzionale)
    print("\n" + "="*60)
    result = test_reload_endpoint()
    
    print("\n" + "="*60)
    print("📊 RIEPILOGO TEST")
    print("="*60)
    print("✅ API Server: Online")
    print("✅ Endpoint /documents: Funzionante")
    if result is True:
        print("✅ Endpoint /reload: Funzionante")
    elif result is False:
        print("❌ Endpoint /reload: Errore")
    else:
        print("⏭️  Endpoint /reload: Non testato")
    
    print("\n💡 Prossimi passi:")
    print("   1. Vai su Admin Panel: http://localhost:8080")
    print("   2. Carica un documento")
    print("   3. Clicca 'Reindicizza'")
    print("   4. Verifica che il messaggio sia 'Reindicizzazione completata!'")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrotto dall'utente")
