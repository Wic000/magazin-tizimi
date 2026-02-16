"""FastAPI asosiy ilova - Magazin tizimi"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, get_db
from models import User
from auth import get_password_hash
from routers import auth, products, sales, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ishga tushganda baza va default admin yaratish"""
    init_db()
    db = next(get_db())
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            full_name="Administrator",
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("Default admin yaratildi: admin / admin123")
    db.close()
    yield
    # shutdown


app = FastAPI(
    title="Magazin tizimi",
    description="Kichik do'kon uchun multi-user magazin",
    lifespan=lifespan
)

# CORS - brauzer va boshqa domenlar uchun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Productionda aniq domen yozing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


# Static fayllar
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    """Asosiy sahifa"""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Magazin API ishlayapti. Frontend: /static/index.html"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
