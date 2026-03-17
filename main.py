from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.core.database import init_db
from backend.api.routes import devices, networks, auth, scan, security, intelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NetScan API",
    description="Advanced Network Scanner and Security Analysis Platform - Beat Fing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(networks.router, prefix="/api/networks", tags=["networks"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting NetScan API v2.0 - Beat Fing Edition")
    await init_db()

@app.get("/")
async def root():
    return {
        "message": "NetScan API - Advanced Network Intelligence Platform",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Device Intelligence Engine",
            "Presence Detection System",
            "Smart Alerts Engine",
            "Internet Monitoring",
            "Real DPI (Coming Soon)",
            "AI Insights Layer (Coming Soon)",
            "Router Integration",
            "Security Scanning"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# WebSocket for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({
                "type": "update",
                "data": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
