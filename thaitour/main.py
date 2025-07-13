from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from thaitour.routers.v1 import authentication_router, registration_router, province_router, tax_router
from thaitour.core.config import settings

app = FastAPI(
    title="ThaiTour - คนละครึ่ง API",
    description="API สำหรับระบบท่องเที่ยวไทยคนละครึ่ง",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในการใช้งานจริงควรกำหนด origins ที่เฉพาะเจาะจง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(authentication_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(registration_router.router, prefix="/api/v1/registration", tags=["Registration"])
app.include_router(province_router.router, prefix="/api/v1/provinces", tags=["Provinces"])
app.include_router(tax_router.router, prefix="/api/v1/tax", tags=["Tax Benefits"])

@app.get("/")
async def root():
    return {
        "message": "ยินดีต้อนรับสู่ ThaiTour API - ระบบท่องเที่ยวไทยคนละครึ่ง",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ThaiTour API"}
