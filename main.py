from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.manager.routes_manager import RoutesManager

app = FastAPI(
    title="API - Creaciones Morochita",
    description="API para la Gestión de Inventariado y Ventas",
    version="1.0.0"
)

# Configuración de CORS
# Dominios permitidos
origins = [
    "http://localhost:3000", # front react local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # de momento permitimos todos los origenes
    allow_credentials=True,
    allow_methods=["*"],  # métodos permitidos
    allow_headers=["*"],  # cabeceras permitidas
)

# redirecciona a la documentacion
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# rutas de endpoints
routes_manager = RoutesManager(app)
routes_manager.include_routes()