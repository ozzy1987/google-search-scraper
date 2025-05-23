#!/usr/bin/env python3
"""
Google Search Scraper - Servidor MCP
Servidor MCP para realizar búsquedas en Google sin limitaciones usando web scraping
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
import re

import aiohttp
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# User agents rotativos para evadir detección
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

# Dominios de Google para rotación
GOOGLE_DOMAINS = [
    "www.google.com",
    "www.google.es",
    "www.google.co.uk",
    "www.google.ca",
    "www.google.com.au",
    "www.google.de",
    "www.google.fr"
]

class GoogleScraper:
    def __init__(self):
        self.session = None
        self.last_request_time = 0
        self.request_count = 0
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                ssl=False
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self.session
    
    def get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    async def delay_request(self):
        """Implementa delay aleatorio entre requests para evitar detección"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Delay base + aleatorio
        min_delay = 1.5 + random.uniform(0.5, 2.0)
        
        # Aumentar delay si hacemos muchas requests
        if self.request_count > 10:
            min_delay += random.uniform(1.0, 3.0)
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def clean_text(self, text: str) -> str:
        """Limpia y normaliza texto extraído"""
        if not text:
            return ""
        # Remover espacios extra y caracteres especiales
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\.,!?;:\-()\'\"áéíóúñü]', '', text, flags=re.IGNORECASE)
        return text
    
    def parse_search_results(self, html: str) -> List[Dict[str, Any]]:
        """Extrae resultados de búsqueda del HTML de Google"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Buscar contenedores de resultados
        result_containers = soup.find_all('div', class_='g') or soup.find_all('div', {'data-ved': True})
        
        for container in result_containers[:15]:  # Limitar a 15 resultados
            try:
                # Extraer título
                title_elem = container.find('h3') or container.find('a', {'data-ved': True})
                title = self.clean_text(title_elem.get_text()) if title_elem else ""
                
                # Extraer URL
                link_elem = container.find('a', href=True)
                url = ""
                if link_elem and link_elem.get('href'):
                    href = link_elem['href']
                    if href.startswith('/url?q='):
                        url = href.split('/url?q=')[1].split('&')[0]
                    elif href.startswith('http'):
                        url = href
                
                # Extraer snippet/descripción
                snippet_elem = container.find('span', {'data-ved': True}) or container.find('div', class_='s')
                if not snippet_elem:
                    snippet_elem = container.find_all('div')[-1] if container.find_all('div') else None
                
                snippet = self.clean_text(snippet_elem.get_text()) if snippet_elem else ""
                
                # Extraer fecha si está disponible
                date_elem = container.find('span', string=re.compile(r'\d{1,2}\s+\w+\s+\d{4}'))
                date = date_elem.get_text() if date_elem else ""
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'date': date,
                        'position': len(results) + 1
                    })
                    
            except Exception as e:
                continue
        
        return results
    
    async def search(self, query: str, num_results: int = 10, lang: str = 'es') -> Dict[str, Any]:
        """Realiza búsqueda en Google"""
        await self.delay_request()
        
        session = await self.get_session()
        domain = random.choice(GOOGLE_DOMAINS)
        
        # Construir URL de búsqueda
        params = {
            'q': query,
            'num': min(num_results, 20),
            'hl': lang,
            'lr': f'lang_{lang}',
            'safe': 'off'
        }
        
        query_string = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"https://{domain}/search?{query_string}"
        
        try:
            headers = self.get_headers()
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self.parse_search_results(html)
                    
                    return {
                        'success': True,
                        'query': query,
                        'results_count': len(results),
                        'results': results[:num_results],
                        'timestamp': datetime.now().isoformat(),
                        'source': domain
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status}',
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Instancia global del scraper
scraper = GoogleScraper()

# Crear servidor MCP
app = Server("google-scraper")

@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Lista las herramientas disponibles"""
    return [
        types.Tool(
            name="google_search",
            description="Realiza búsquedas en Google sin limitaciones usando web scraping",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Término de búsqueda"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Número de resultados a obtener (default: 10, máximo: 20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "language": {
                        "type": "string",
                        "description": "Idioma de búsqueda (default: 'es')",
                        "default": "es"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="google_search_advanced",
            description="Búsqueda avanzada en Google con filtros adicionales",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Término de búsqueda"
                    },
                    "site": {
                        "type": "string",
                        "description": "Buscar solo en un sitio específico (ej: site:reddit.com)"
                    },
                    "filetype": {
                        "type": "string", 
                        "description": "Tipo de archivo (pdf, doc, etc.)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Rango de fechas (day, week, month, year)"
                    },
                    "num_results": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Maneja las llamadas a las herramientas"""
    
    if name == "google_search":
        query = arguments.get("query", "")
        num_results = arguments.get("num_results", 10)
        language = arguments.get("language", "es")
        
        if not query:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": "Query parameter is required"}, indent=2)
            )]
        
        result = await scraper.search(query, num_results, language)
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "google_search_advanced":
        query = arguments.get("query", "")
        site = arguments.get("site", "")
        filetype = arguments.get("filetype", "")
        date_range = arguments.get("date_range", "")
        num_results = arguments.get("num_results", 10)
        
        if not query:
            return [types.TextContent(
                type="text", 
                text=json.dumps({"error": "Query parameter is required"}, indent=2)
            )]
        
        # Construir query avanzada
        advanced_query = query
        if site:
            advanced_query += f" site:{site}"
        if filetype:
            advanced_query += f" filetype:{filetype}"
        
        result = await scraper.search(advanced_query, num_results)
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        )]

async def main():
    # Configurar opciones de inicialización
    options = InitializationOptions(
        server_name="google-scraper",
        server_version="1.0.0",
        capabilities={}
    )
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                options
            )
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())