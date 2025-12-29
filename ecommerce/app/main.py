import os
import httpx
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from datetime import datetime

# Import WAF Engine
# We need to make sure the current directory is in sys.path for pickle to find classes if needed
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.waf_detector import WAFEngine

# Configuration
HAAS_BACKEND_URL = os.getenv("HAAS_BACKEND_URL", "http://backend:8000/api/v1")
MODEL_DIR = os.getenv("MODEL_DIR", "/app/models")

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecommerce")

# Initialize WAF
waf = WAFEngine(model_dir=MODEL_DIR)

app = FastAPI(title="Vulnerable E-Commerce App")

# Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Middleware for WAF
@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    # Skip static files or internal routes if any
    if request.url.path.startswith("/static"):
        return await call_next(request)

    # Extract payload from Query Params
    query_params = str(request.query_params)
    
    # Extract payload from Body (if form data)
    body_payload = ""
    if request.method == "POST":
        try:
            form = await request.form()
            body_payload = str(dict(form))
        except:
            pass # Not a form

    # Combine for analysis
    full_payload = f"{query_params} {body_payload}".strip()
    
    if full_payload:
        logger.info(f"Inspecting payload: {full_payload}")
        result = waf.analyze(full_payload)
        
        if result.get('is_attack'):
            logger.warning(f"WAF BLOCKED ATTACK! Confidence: {result.get('confidence')}")
            
            # Trigger HaaS Backend
            try:
                async with httpx.AsyncClient() as client:
                    # 1. Report the attack to the Dashboard
                    await client.post(f"{HAAS_BACKEND_URL}/observability/alerts/", json={
                        "source_ip": request.client.host,
                        "payload": full_payload,
                        "confidence": result.get('confidence'),
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    # 2. Deploy Honeypot
                    await client.post(f"{HAAS_BACKEND_URL}/honeypots/", json={
                        "name": f"honeypot-triggered-{os.urandom(4).hex()}",
                        "image": "shellm-honeypot:latest"
                    })
            except Exception as e:
                logger.error(f"Failed to notify HaaS backend: {e}")

            # Return a generic 403 or a fake error page
            return JSONResponse(status_code=403, content={"detail": "Access Denied: Malicious Activity Detected"})

    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    products = [
        {"id": 1, "name": "Super Secure Firewall", "price": 999.99},
        {"id": 2, "name": "Unbreakable Lock", "price": 49.99},
        {"id": 3, "name": "Invisible Cloak", "price": 10000.00},
    ]
    return templates.TemplateResponse("index.html", {"request": request, "products": products})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    # This is where the vulnerability would be if WAF didn't catch it
    # We just display results.
    return templates.TemplateResponse("search.html", {"request": request, "q": q})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    # Fake login logic
    if username == "admin" and password == "admin":
        return templates.TemplateResponse("index.html", {"request": request, "message": "Welcome Admin!"})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
