#!/usr/bin/env python3
"""
Ejemplos de uso del servidor MCP de Google Search Scraper
"""

import json
import asyncio
from typing import Dict, Any

# Simulación de cliente MCP (en un caso real usarías la librería MCP cliente)
class MCPClientExample:
    """Cliente MCP de ejemplo para demostrar el uso"""
    
    def __init__(self):
        print("🔧 Iniciando cliente MCP de ejemplo")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Simula una llamada a herramienta MCP"""
        print(f"📞 Llamando herramienta: {tool_name}")
        print(f"📝 Argumentos: {json.dumps(arguments, indent=2)}")
        
        # En un caso real, esto haría la llamada real al servidor MCP
        # Aquí simulamos la respuesta
        if tool_name == "google_search":
            return {
                "success": True,
                "query": arguments.get("query", ""),
                "results_count": 3,
                "results": [
                    {
                        "title": f"Resultado de ejemplo para '{arguments.get('query')}'",
                        "url": "https://example.com/result1",
                        "snippet": "Este es un resultado de ejemplo del scraper MCP...",
                        "position": 1
                    }
                ]
            }
        return {"error": "Herramienta no encontrada"}

async def example_basic_search():
    """Ejemplo de búsqueda básica via MCP"""
    print("\n🔍 Ejemplo 1: Búsqueda básica MCP")
    
    client = MCPClientExample()
    
    result = await client.call_tool("google_search", {
        "query": "python programming",
        "num_results": 5,
        "language": "es"
    })
    
    print("📋 Resultado:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

async def example_advanced_search():
    """Ejemplo de búsqueda avanzada via MCP"""
    print("\n🔍 Ejemplo 2: Búsqueda avanzada MCP") 
    
    client = MCPClientExample()
    
    result = await client.call_tool("google_search_advanced", {
        "query": "machine learning",
        "site": "github.com",
        "filetype": "py",
        "num_results": 10
    })
    
    print("📋 Resultado avanzado:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def show_mcp_configuration():
    """Muestra configuración para Claude Desktop"""
    print("\n⚙️ Configuración para Claude Desktop (claude_desktop_config.json):")
    
    config = {
        "mcpServers": {
            "google-scraper": {
                "command": "python",
                "args": ["path/to/google_scraper_mcp.py"],
                "env": {
                    "PYTHONPATH": "."
                }
            }
        }
    }
    
    print(json.dumps(config, indent=2))

def show_available_tools():
    """Muestra las herramientas disponibles en el servidor MCP"""
    print("\n🛠️ Herramientas disponibles en el servidor MCP:")
    
    tools = [
        {
            "name": "google_search",
            "description": "Búsqueda básica en Google",
            "parameters": {
                "query": "Término de búsqueda (requerido)",
                "num_results": "Número de resultados (1-20, default: 10)",
                "language": "Idioma (default: 'es')"
            }
        },
        {
            "name": "google_search_advanced", 
            "description": "Búsqueda avanzada con filtros",
            "parameters": {
                "query": "Término de búsqueda (requerido)",
                "site": "Sitio específico (ej: reddit.com)",
                "filetype": "Tipo de archivo (pdf, doc, etc.)",
                "date_range": "Rango de fechas (day, week, month, year)",
                "num_results": "Número de resultados (1-20, default: 10)"
            }
        }
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. {tool['name']}")
        print(f"   📝 {tool['description']}")
        print("   📋 Parámetros:")
        for param, desc in tool['parameters'].items():
            print(f"      • {param}: {desc}")

def show_usage_instructions():
    """Instrucciones de uso del servidor MCP"""
    print("\n📖 Cómo usar el servidor MCP:")
    print("1. Ejecutar el servidor: python mcp/google_scraper_mcp.py")
    print("2. Configurar en Claude Desktop (ver configuración arriba)")
    print("3. Usar las herramientas en conversaciones con Claude")
    print("\n💡 Ejemplos de uso en Claude:")
    print('- "Busca información sobre Python programming"')
    print('- "Encuentra PDFs sobre machine learning en arXiv"')
    print('- "Busca discusiones sobre React en Reddit"')

async def main():
    """Función principal de ejemplos"""
    print("🚀 Ejemplos del servidor MCP de Google Search Scraper")
    print("=" * 60)
    
    show_available_tools()
    show_mcp_configuration()
    show_usage_instructions()
    
    print("\n🔄 Simulando llamadas MCP:")
    await example_basic_search()
    await example_advanced_search()
    
    print("\n✅ Ejemplos completados!")
    print("💡 Para uso real, configura el servidor MCP en Claude Desktop")

if __name__ == "__main__":
    asyncio.run(main())