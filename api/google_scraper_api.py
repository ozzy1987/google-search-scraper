#!/usr/bin/env python3
"""
Google Search Scraper - API REST
API REST para realizar búsquedas en Google sin limitaciones usando web scraping
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import random
import time
import re
from datetime import datetime
from urllib.parse import quote_plus
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User agents rotativos
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

GOOGLE_DOMAINS = [
    "www.google.com",
    "www.google.es", 
    "www.google.co.uk",
    "www.google.ca",
    "www.google.com.au",
    "www.google.de",
    "www.google.fr"
]

# Modelos Pydantic
class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    date: str = ""
    position: int

class SearchResponse(BaseModel):
    success: bool
    query: str
    results_count: int
    results: List[SearchResult]
    timestamp: str
    source: str
    error: Optional[str] = None

class AdvancedSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda")
    site: Optional[str] = Field(None, description="Sitio específico (ej: reddit.com)")
    filetype: Optional[str] = Field(None, description="Tipo de archivo (pdf, doc, etc.)")
    date_range: Optional[str] = Field(None, description="Rango de fechas (day, week, month, year)")
    language: str = Field("es", description="Idioma de búsqueda")
    num_results: int = Field(10, ge=1, le=50, description="Número de resultados")
    safe_search: bool = Field(False, description="Activar búsqueda segura")

class GoogleScraper:
    def __init__(self):
        self.session = None
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset = time.time()
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=20,
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
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
    
    async def smart_delay(self):
        """Sistema inteligente de delays para evitar detección"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Reset contador cada hora
        if current_time - self.rate_limit_reset > 3600:
            self.request_count = 0
            self.rate_limit_reset = current_time
        
        # Calcular delay dinámico
        base_delay = 2.0
        random_delay = random.uniform(0.5, 2.5)
        
        # Aumentar delay progresivamente con más requests
        if self.request_count > 20:
            base_delay += 2.0
        elif self.request_count > 10:
            base_delay += 1.0
        
        total_delay = base_delay + random_delay
        
        if time_since_last < total_delay:
            sleep_time = total_delay - time_since_last
            logger.info(f"Aplicando delay de {sleep_time:.2f}s (requests: {self.request_count})")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\.,!?;:\-()\'\"áéíóúñüÁÉÍÓÚÑÜ@]', '', text, flags=re.IGNORECASE)
        return text[:500]  # Limitar longitud
    
    def extract_url(self, href: str) -> str:
        """Extrae URL real de los enlaces de Google"""
        if not href:
            return ""
        
        if href.startswith('/url?q='):
            try:
                url = href.split('/url?q=')[1].split('&')[0]
                return url
            except:
                return ""
        elif href.startswith('http'):
            return href
        elif href.startswith('/search'):
            return ""
        else:
            return href
    
    def parse_search_results(self, html: str) -> List[Dict[str, Any]]:
        """Parser mejorado para resultados de Google"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Múltiples selectores para diferentes layouts de Google
        selectors = [
            'div[data-ved] h3',
            'div.g h3', 
            'div.rc h3',
            'div[data-hveid] h3',
            '.g .r h3'
        ]
        
        found_results = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                found_results = elements
                break
        
        for idx, title_elem in enumerate(found_results[:20]):
            try:
                # Encontrar contenedor padre
                container = title_elem
                for _ in range(5):  # Buscar hasta 5 niveles arriba
                    container = container.parent
                    if container.name == 'div' and ('data-ved' in container.attrs or 'class' in container.attrs):
                        break
                
                # Extraer título
                title = self.clean_text(title_elem.get_text())
                if not title:
                    continue
                
                # Extraer URL
                link_elem = container.find('a', href=True)
                url = ""
                if link_elem:
                    url = self.extract_url(link_elem.get('href', ''))
                
                # Extraer snippet
                snippet = ""
                snippet_selectors = [
                    'span[data-ved]',
                    '.s',
                    '.st', 
                    'div[data-sncf]',
                    'div[style*="color"]'
                ]
                
                for sel in snippet_selectors:
                    snippet_elem = container.select_one(sel)
                    if snippet_elem and snippet_elem.get_text().strip():
                        snippet = self.clean_text(snippet_elem.get_text())
                        break
                
                # Extraer fecha si existe
                date = ""
                date_patterns = [
                    r'\d{1,2}\s+\w+\s+\d{4}',
                    r'\d{1,2}/\d{1,2}/\d{4}',
                    r'\w+\s+\d{1,2},\s+\d{4}'
                ]
                
                container_text = container.get_text()
                for pattern in date_patterns:
                    match = re.search(pattern, container_text)
                    if match:
                        date = match.group()
                        break
                
                if title and url and url.startswith('http'):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'date': date,
                        'position': len(results) + 1
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing result {idx}: {e}")
                continue
        
        return results
    
    async def search(self, query: str, num_results: int = 10, language: str = 'es', 
                    safe_search: bool = False, **kwargs) -> Dict[str, Any]:
        """Búsqueda principal en Google"""
        await self.smart_delay()
        
        session = await self.get_session()
        domain = random.choice(GOOGLE_DOMAINS)
        
        # Construir parámetros de búsqueda
        params = {
            'q': query,
            'num': min(num_results + 5, 50),  # Pedir más para compensar filtrados
            'hl': language,
            'lr': f'lang_{language}',
            'safe': 'active' if safe_search else 'off',
            'start': 0
        }
        
        # Agregar filtros adicionales
        if 'site' in kwargs and kwargs['site']:
            params['q'] += f" site:{kwargs['site']}"
        if 'filetype' in kwargs and kwargs['filetype']:
            params['q'] += f" filetype:{kwargs['filetype']}"
        if 'date_range' in kwargs and kwargs['date_range']:
            # Google usa parámetros específicos para fechas
            date_params = {
                'day': 'd',
                'week': 'w', 
                'month': 'm',
                'year': 'y'
            }
            if kwargs['date_range'] in date_params:
                params['tbs'] = f"qdr:{date_params[kwargs['date_range']]}"
        
        query_string = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"https://{domain}/search?{query_string}"
        
        logger.info(f"Searching: {query} on {domain}")
        
        try:
            headers = self.get_headers()
            
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Verificar si Google nos está bloqueando
                    if 'detected unusual traffic' in html.lower() or 'captcha' in html.lower():
                        logger.warning("Google detectó tráfico inusual - rotando dominio")
                        # Intentar con otro dominio
                        return await self._retry_with_different_domain(query, num_results, language, safe_search, **kwargs)
                    
                    results = self.parse_search_results(html)
                    
                    return {
                        'success': True,
                        'query': query,
                        'results_count': len(results),
                        'results': results[:num_results],
                        'timestamp': datetime.now().isoformat(),
                        'source': domain,
                        'total_found': len(results)
                    }
                else:
                    logger.error(f"HTTP {response.status} for query: {query}")
                    return {
                        'success': False,
                        'error': f'HTTP {response.status}',
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error searching '{query}': {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _retry_with_different_domain(self, query: str, num_results: int, 
                                         language: str, safe_search: bool, **kwargs):
        """Reintenta búsqueda con dominio diferente si hay bloqueo"""
        await asyncio.sleep(random.uniform(3, 7))  # Delay extra
        return await self.search(query, num_results, language, safe_search, **kwargs)
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Instancia global
scraper = GoogleScraper()

# Crear aplicación FastAPI
app = FastAPI(
    title="Google Search Scraper API",
    description="API para realizar búsquedas en Google sin limitaciones usando web scraping",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_event():
    await scraper.close()

@app.get("/", summary="Health Check")
async def root():
    return {
        "message": "Google Search Scraper API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/search",
            "advanced_search": "/search/advanced",
            "docs": "/docs"
        }
    }

@app.get("/search", response_model=SearchResponse, summary="Búsqueda Simple")
async def search_google(
    q: str = Query(..., description="Término de búsqueda"),
    num: int = Query(10, ge=1, le=50, description="Número de resultados"),
    lang: str = Query("es", description="Idioma de búsqueda"),
    safe: bool = Query(False, description="Búsqueda segura")
):
    """Realiza una búsqueda simple en Google"""
    try:
        result = await scraper.search(q, num, lang, safe)
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/advanced", response_model=SearchResponse, summary="Búsqueda Avanzada")
async def advanced_search(request: AdvancedSearchRequest):
    """Realiza una búsqueda avanzada con filtros adicionales"""
    try:
        result = await scraper.search(
            query=request.query,
            num_results=request.num_results,
            language=request.language,
            safe_search=request.safe_search,
            site=request.site,
            filetype=request.filetype,
            date_range=request.date_range
        )
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error in advanced search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/site/{site_domain}", response_model=SearchResponse, summary="Buscar en Sitio Específico")
async def search_in_site(
    site_domain: str,
    q: str = Query(..., description="Término de búsqueda"),
    num: int = Query(10, ge=1, le=50, description="Número de resultados"),
    lang: str = Query("es", description="Idioma")
):
    """Busca solo dentro de un dominio específico"""
    try:
        result = await scraper.search(
            query=q,
            num_results=num,
            language=lang,
            site=site_domain
        )
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error in site search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/filetype/{file_type}", response_model=SearchResponse, summary="Buscar Tipo de Archivo")
async def search_filetype(
    file_type: str,
    q: str = Query(..., description="Término de búsqueda"),
    num: int = Query(10, ge=1, le=50, description="Número de resultados"),
    lang: str = Query("es", description="Idioma")
):
    """Busca archivos de un tipo específico (pdf, doc, ppt, etc.)"""
    try:
        result = await scraper.search(
            query=q,
            num_results=num,
            language=lang,
            filetype=file_type
        )
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error in filetype search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", summary="Estadísticas del Scraper")
async def get_stats():
    """Obtiene estadísticas de uso del scraper"""
    return {
        "total_requests": scraper.request_count,
        "last_request": datetime.fromtimestamp(scraper.last_request_time).isoformat() if scraper.last_request_time > 0 else None,
        "rate_limit_reset": datetime.fromtimestamp(scraper.rate_limit_reset).isoformat(),
        "session_active": scraper.session is not None and not scraper.session.closed,
        "available_domains": len(GOOGLE_DOMAINS),
        "user_agents": len(USER_AGENTS)
    }

@app.post("/reset", summary="Reset Scraper")
async def reset_scraper():
    """Reinicia el scraper (útil si hay bloqueos)"""
    try:
        await scraper.close()
        scraper.session = None
        scraper.request_count = 0
        scraper.rate_limit_reset = time.time()
        return {"message": "Scraper reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función para ejecutar el servidor
async def run_server():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )