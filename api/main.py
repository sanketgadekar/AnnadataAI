from fastapi import FastAPI
from api.routers import crop, fertilizer, yield_, irrigation, soil_health, disease

app = FastAPI(title="AnnadataAI API")

app.include_router(crop.router)
app.include_router(fertilizer.router)
app.include_router(yield_.router)
app.include_router(irrigation.router)
app.include_router(soil_health.router)
app.include_router(disease.router)

@app.get("/")
def home():
    return {"message": "API Running"}

@app.get("/health")
def health():
    return {"status": "ok"}
