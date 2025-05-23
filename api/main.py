#!/usr/bin/env python3
"""
Punto de entrada principal para la API de Google Search Scraper
"""

import os
import sys
import uvicorn
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

# Importar la app desde google_scraper_api
from google_scraper_api import app

def main():
    """Función principal para ejecutar el servidor"""
    # Configuración desde variables de entorno
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"🚀 Iniciando Google Search Scraper API")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔍 Redoc: http://{host}:{port}/redoc")
    
    # Ejecutar servidor
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        access_log=True
    )

if __name__ == "__main__":
    main()