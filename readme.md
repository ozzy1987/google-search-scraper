# 🔍 Google Search Scraper

> **Búsquedas ilimitadas en Google sin restricciones ni costos de API**

Un sistema completo de web scraping para realizar búsquedas en Google de forma gratuita, implementado como servidor MCP y API REST con sistema anti-detección.

## 🚀 Características

- ✅ **Sin limitaciones**: Evita las restricciones y costos de Google Search API
- ✅ **Doble implementación**: Servidor MCP + API REST con FastAPI
- ✅ **Anti-detección**: Rotación automática de user agents y dominios
- ✅ **Búsqueda avanzada**: Filtros por sitio, tipo de archivo, rango de fechas
- ✅ **Rate limiting inteligente**: Sistema adaptativo de delays
- ✅ **Docker Ready**: Despliegue fácil con contenedores
- ✅ **Proxy Nginx**: Balanceador de carga y rate limiting

## 🛠️ Instalación Rápida

### Opción 1: Docker (Recomendado)
```bash
git clone https://github.com/tu-usuario/google-search-scraper.git
cd google-search-scraper/api
docker-compose up -d
```

### Opción 2: Instalación Manual
```bash
git clone https://github.com/tu-usuario/google-search-scraper.git
cd google-search-scraper
pip install -r requirements.txt

# Para API REST
cd api && python main.py

# Para servidor MCP
cd mcp && python google_scraper_mcp.py
```

## 📚 Uso Básico

### API REST
```bash
# Búsqueda simple
curl "http://localhost:8000/search?q=python+tutorial&num=5"

# Búsqueda en sitio específico
curl "http://localhost:8000/search/site/reddit.com?q=python+tips"

# Búsqueda por tipo de archivo
curl "http://localhost:8000/search/filetype/pdf?q=machine+learning"
```

### Respuesta de ejemplo
```json
{
  "success": true,
  "query": "python tutorial",
  "results_count": 5,
  "results": [
    {
      "title": "Python Tutorial - Learn Python Programming",
      "url": "https://example.com/python-tutorial",
      "snippet": "Complete guide to Python programming...",
      "date": "2024-01-15",
      "position": 1
    }
  ],
  "timestamp": "2024-01-20T10:30:00",
  "source": "www.google.com"
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```env
# .env
LOG_LEVEL=info
MAX_RESULTS=50
DELAY_MIN=1.5
DELAY_MAX=3.0
RATE_LIMIT_REQUESTS=100
```

### Búsqueda Avanzada (POST)
```json
{
  "query": "machine learning",
  "site": "arxiv.org",
  "filetype": "pdf",
  "date_range": "year",
  "language": "en",
  "num_results": 20,
  "safe_search": false
}
```

## 📖 Documentación

- [📋 Uso de la API](docs/API_USAGE.md)
- [⚙️ Configuración MCP](docs/MCP_SETUP.md)
- [🐳 Despliegue Docker](api/docker-compose.yml)
- [📝 Ejemplos Prácticos](examples/)

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cliente Web   │───▶│   Nginx Proxy    │───▶│   FastAPI App   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             │
                       │   MCP Server     │◀────────────┘
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │ Google Scraper   │
                       │ (Anti-Detection) │
                       └──────────────────┘
```

## 🛡️ Sistema Anti-Detección

- **Rotación de User Agents**: 8+ user agents realistas
- **Dominios múltiples**: 7 dominios de Google diferentes
- **Delays inteligentes**: Sistema adaptativo basado en uso
- **Headers realistas**: Simulación de navegador real
- **Manejo de errores**: Recovery automático ante bloqueos

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Health check y información |
| `/search` | GET | Búsqueda simple |
| `/search/advanced` | POST | Búsqueda con filtros avanzados |
| `/search/site/{domain}` | GET | Búsqueda en sitio específico |
| `/search/filetype/{type}` | GET | Búsqueda por tipo de archivo |
| `/stats` | GET | Estadísticas de uso |
| `/reset` | POST | Reiniciar scraper |
| `/docs` | GET | Documentación interactiva |

## 🚨 Consideraciones Legales

Este proyecto es para **uso educativo y personal**. Al usar este scraper:

- ✅ Respeta los términos de servicio de Google
- ✅ No hagas requests masivos o abusivos
- ✅ Implementa delays apropiados entre requests
- ✅ Considera las implicaciones legales en tu jurisdicción

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## ⭐ Support

Si este proyecto te resulta útil, considera darle una estrella ⭐ en GitHub.

---

**Nota**: Este proyecto no está afiliado con Google LLC. Es una implementación independiente para fines educativos.