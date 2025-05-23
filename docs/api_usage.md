# 📋 Guía de Uso de la API

## 🚀 Inicio Rápido

### Ejecutar la API
```bash
# Método 1: Docker (Recomendado)
cd api/
docker-compose up -d

# Método 2: Python directo
cd api/
python main.py
```

La API estará disponible en: `http://localhost:8000`

## 📚 Endpoints Principales

### 1. Búsqueda Simple
```bash
GET /search?q={query}&num={results}&lang={language}&safe={boolean}
```

**Parámetros:**
- `q` (requerido): Término de búsqueda
- `num` (opcional, default=10): Número de resultados (1-50)
- `lang` (opcional, default="es"): Idioma de búsqueda
- `safe` (opcional, default=false): Búsqueda segura

**Ejemplo:**
```bash
curl "http://localhost:8000/search?q=python+programming&num=5&lang=en"
```

### 2. Búsqueda Avanzada
```bash
POST /search/advanced
Content-Type: application/json
```

**Body:**
```json
{
  "query": "machine learning",
  "site": "github.com",
  "filetype": "py",
  "date_range": "month",
  "language": "en",
  "num_results": 15,
  "safe_search": false
}
```

### 3. Búsqueda en Sitio Específico
```bash
GET /search/site/{domain}?q={query}&num={results}
```

**Ejemplo:**
```bash
curl "http://localhost:8000/search/site/stackoverflow.com?q=python+error&num=10"
```

### 4. Búsqueda por Tipo de Archivo
```bash
GET /search/filetype/{extension}?q={query}&num={results}
```

**Ejemplo:**
```bash
curl "http://localhost:8000/search/filetype/pdf?q=data+science&num=8"
```

## 📊 Respuesta de la API

### Estructura de Respuesta Exitosa
```json
{
  "success": true,
  "query": "python tutorial",
  "results_count": 5,
  "results": [
    {
      "title": "Learn Python Programming",
      "url": "https://example.com/python-guide",
      "snippet": "Complete Python tutorial for beginners...",
      "date": "2024-01-15",
      "position": 1
    }
  ],
  "timestamp": "2024-01-20T10:30:00.123456",
  "source": "www.google.com"
}
```

### Estructura de Respuesta de Error
```json
{
  "success": false,
  "error": "HTTP 429 - Too Many Requests",
  "query": "search term",
  "timestamp": "2024-01-20T10:30:00.123456"
}
```

## 🔧 Endpoints de Utilidad

### Estadísticas del Sistema
```bash
GET /stats
```

**Respuesta:**
```json
{
  "total_requests": 45,
  "last_request": "2024-01-20T10:29:45.123456",
  "rate_limit_reset": "2024-01-20T11:00:00.000000",
  "session_active": true,
  "available_domains": 7,
  "user_agents": 8
}
```

### Reiniciar Scraper
```bash
POST /reset
```

### Health Check
```bash
GET /
```

### Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛡️ Manejo de Errores

### Códigos de Estado HTTP
- `200`: Búsqueda exitosa
- `400`: Parámetros inválidos
- `429`: Demasiadas solicitudes
- `500`: Error interno del servidor

### Reintentos Automáticos
La API implementa reintentos automáticos en caso de:
- Detección de CAPTCHA
- Bloqueo temporal
- Error de red

## ⚡ Optimización de Rendimiento

### Rate Limiting
- Delay base: 2-4 segundos entre requests
- Delay adaptativo basado en uso
- Reset automático cada hora

### Mejores Prácticas
1. **Espaciar requests**: No hacer múltiples búsquedas simultáneas
2. **Usar cache**: Almacenar resultados localmente cuando sea posible
3. **Límites razonables**: No solicitar más de 20 resultados por búsqueda
4. **Monitorear stats**: Revisar `/stats` para evitar bloqueos

## 🔍 Filtros Avanzados

### Operadores de Búsqueda Google
```bash
# Búsqueda exacta
"machine learning algorithms"

# Excluir términos
python -java

# Rango numérico
laptop $500..$1000

# Comodín
python * tutorial

# OR lógico
python OR java programming
```

### Filtros de Fecha
- `day`: Últimas 24 horas
- `week`: Última semana
- `month`: Último mes
- `year`: Último año

### Tipos de Archivo Soportados
- `pdf`, `doc`, `docx`, `ppt`, `pptx`
- `xls`, `xlsx`, `txt`, `rtf`
- `py`, `js`, `html`, `css`, `json`

## 🐳 Configuración Docker

### docker-compose.yml
```yaml
services:
  google-scraper-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=info
    restart: unless-stopped
```

### Variables de Entorno
```env
PYTHONUNBUFFERED=1
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

## 🚨 Limitaciones y Consideraciones

### Limitaciones Técnicas
- Máximo 50 resultados por búsqueda
- Rate limiting: ~10-20 requests por minuto
- Dependiente de la estructura HTML de Google

### Consideraciones Legales
- Uso personal y educativo únicamente
- Respetar términos de servicio de Google
- Implementar delays apropiados
- No uso comercial sin autorización

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica `/stats` para estado del scraper
3. Usa `/reset` si hay bloqueos persistentes
4. Consulta la documentación en `/docs`