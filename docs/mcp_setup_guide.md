# Google Scraper MCP Setup Guide

## Configuración rápida

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar servidor MCP
```bash
python mcp/google_scraper_mcp.py
```

### 3. Configurar Claude Desktop
Edita tu archivo de configuración de Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-scraper": {
      "command": "python",
      "args": ["path/to/mcp/google_scraper_mcp.py"],
      "env": {}
    }
  }
}
```

## Uso básico

Una vez configurado, puedes usar estos comandos en Claude:

- `search_google` - Buscar en Google
- `get_search_suggestions` - Obtener sugerencias de búsqueda

## Funciones disponibles

### search_google
Realiza búsquedas en Google con parámetros avanzados.

### get_search_suggestions  
Obtiene sugerencias de búsqueda de Google.

## Solución de problemas

### Error de conexión
- Verificar que Python esté en el PATH
- Confirmar que las dependencias estén instaladas
- Revisar los logs en Claude Desktop

### Resultados vacíos
- Google puede estar bloqueando las solicitudes
- Intenta cambiar el user agent o usar un proxy

## Características anti-detección

- Rotación automática de user agents
- Delays aleatorios entre solicitudes  
- Headers HTTP realistas
- Manejo de rate limiting