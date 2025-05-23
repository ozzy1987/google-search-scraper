#!/usr/bin/env python3
"""
Ejemplos de uso de la API REST de Google Scraper
"""

import requests
import json
from typing import Dict, Any

# URL base de la API (ajustar según tu configuración)
BASE_URL = "http://localhost:8000"

def test_connection():
    """Probar la conexión con la API"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ API Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

def search_basic_example():
    """Ejemplo básico de búsqueda"""
    print("\n=== Búsqueda Básica ===")
    
    params = {
        "query": "python programming tutorial",
        "num_results": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/search", params=params)
        data = response.json()
        
        print(f"Query: {data['query']}")
        print(f"Resultados encontrados: {len(data['results'])}")
        
        for i, result in enumerate(data['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def search_advanced_example():
    """Ejemplo con parámetros avanzados"""
    print("\n=== Búsqueda Avanzada ===")
    
    params = {
        "query": "machine learning frameworks",
        "num_results": 3,
        "lang": "es",
        "country": "mx"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/search", params=params)
        data = response.json()
        
        print(f"Query: {data['query']}")
        print(f"Idioma: {params['lang']}, País: {params['country']}")
        
        for result in data['results']:
            print(f"\n• {result['title']}")
            print(f"  {result['url']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def get_suggestions_example():
    """Ejemplo de sugerencias de búsqueda"""
    print("\n=== Sugerencias de Búsqueda ===")
    
    params = {"query": "artificial intel"}
    
    try:
        response = requests.get(f"{BASE_URL}/suggestions", params=params)
        data = response.json()
        
        print(f"Sugerencias para: '{data['query']}'")
        for suggestion in data['suggestions']:
            print(f"• {suggestion}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def post_search_example():
    """Ejemplo usando POST"""
    print("\n=== Búsqueda con POST ===")
    
    payload = {
        "query": "FastAPI tutorial",
        "num_results": 3,
        "safe_search": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/search", 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        print(f"Búsqueda segura para: {data['query']}")
        for result in data['results']:
            print(f"• {result['title']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Ejecutar todos los ejemplos"""
    print("🔍 Google Scraper API - Ejemplos de Uso")
    print("=" * 40)
    
    # Probar conexión
    if not test_connection():
        print("❌ No se puede conectar a la API. ¿Está ejecutándose?")
        print("💡 Ejecuta: uvicorn api.main:app --reload")
        return
    
    # Ejecutar ejemplos
    search_basic_example()
    search_advanced_example()
    get_suggestions_example()
    post_search_example()
    
    print("\n✅ Ejemplos completados!")

if __name__ == "__main__":
    main()