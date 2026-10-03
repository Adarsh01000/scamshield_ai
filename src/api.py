import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.agents.orchestrator import OrchestratorAgent
from src.agents.evaluation import EvaluationAgent
from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Agentic Multi-Modal Scam Detection & Explainable Risk Assessment API"
)

# Enable CORS for cross-origin web/browser integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()
eval_agent = EvaluationAgent()

class TextAnalysisRequest(BaseModel):
    text: str

class URLAnalysisRequest(BaseModel):
    url: str

class QuickScanRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "modalities": ["text", "url", "screenshot", "multimodal", "quick_scan"]
    }

@app.post("/analyze/quick-scan")
def analyze_quick_scan(request: QuickScanRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    result = orchestrator.analyze(content=request.query.strip(), modality="auto")
    return result

@app.post("/analyze/text")
def analyze_text(request: TextAnalysisRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = orchestrator.analyze(content=request.text, modality="text")
    return result

@app.post("/analyze/url")
def analyze_url(request: URLAnalysisRequest):
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    result = orchestrator.analyze(content=request.url, modality="url")
    return result

@app.post("/analyze/screenshot")
async def analyze_screenshot(file: UploadFile = File(...)):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    result = orchestrator.analyze(
        content=file.filename or "uploaded_screenshot.png",
        image_bytes=image_bytes,
        image_name=file.filename,
        modality="screenshot"
    )
    return result

@app.post("/analyze/multimodal")
async def analyze_multimodal(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    image_bytes = None
    filename = None
    if file:
        image_bytes = await file.read()
        filename = file.filename

    if not text and not image_bytes:
        raise HTTPException(status_code=400, detail="Provide at least text or a screenshot.")

    result = orchestrator.analyze(
        content=text or (filename or ""),
        image_bytes=image_bytes,
        image_name=filename,
        modality="multimodal"
    )
    return result

@app.get("/evaluation/report")
def get_evaluation_report():
    return eval_agent.generate_full_report()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
