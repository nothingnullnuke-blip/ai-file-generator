from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from datetime import datetime

from config.settings import settings
from models.schemas import (
    FileGenerationRequest, FileGenerationResponse, ErrorResponse,
    FileType
)
from ai_engine.prompt_processor import PromptProcessor
from generators.pdf_generator import PDFGenerator
from generators.excel_generator import ExcelGenerator
from generators.docx_generator import DocxGenerator
from generators.csv_json_generator import CSVJSONGenerator
from utils.logger import setup_logger
from utils.validators import PromptValidator

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered file generator using cloud-based AI backends"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

# Status
@app.get("/status")
async def status():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "cache": PromptProcessor.get_cache_stats(),
        "backends": {
            "openrouter": "configured" if settings.OR_API_KEY else "not configured",
            "huggingface": "configured" if settings.HF_API_KEY else "not configured"
        },
        "timestamp": datetime.now().isoformat()
    }

# Generate file
@app.post("/generate", response_model=FileGenerationResponse)
async def generate(request: FileGenerationRequest):
    """
    Generate a file from a prompt.
    
    - **prompt**: Natural language description (10-5000 chars)
    - **file_type**: pdf, excel, docx, csv, or json
    - **color_scheme**: professional, modern, vibrant, or classic
    """
    try:
        logger.info(f"API request: {request.file_type} file")
        
        # Validate
        PromptValidator.validate_prompt(request.prompt)
        PromptValidator.validate_file_type(request.file_type)
        
        # Process
        processor = PromptProcessor()
        structured_output = processor.process(request.prompt, request.file_type)
        
        # Generate
        generator = _get_generator(request.file_type, structured_output)
        filepath = generator.generate()
        
        file_size = filepath.stat().st_size
        
        return FileGenerationResponse(
            success=True,
            file_path=str(filepath.name),
            file_type=FileType(request.file_type),
            file_size_bytes=file_size,
            generated_at=datetime.now().isoformat()
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="File generation failed")

# Generate and download
@app.post("/generate-and-download")
async def generate_and_download(request: FileGenerationRequest):
    """Generate file and return it for download"""
    try:
        processor = PromptProcessor()
        structured_output = processor.process(request.prompt, request.file_type)
        
        generator = _get_generator(request.file_type, structured_output)
        filepath = generator.generate()
        
        return FileResponse(
            path=filepath,
            filename=filepath.name,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate file")

# List files
@app.get("/files")
async def list_files():
    """List all generated files"""
    try:
        files = list(settings.OUTPUT_DIR.glob("*"))
        return {
            "count": len(files),
            "files": [
                {
                    "name": f.name,
                    "size_bytes": f.stat().st_size,
                    "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
                    "url": f"/files/{f.name}"
                }
                for f in sorted(files, key=lambda x: x.stat().st_ctime, reverse=True)
            ]
        }
    except Exception as e:
        logger.error(f"List files error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list files")

# Download file
@app.get("/files/{filename}")
async def download_file(filename: str):
    """Download a generated file"""
    try:
        filepath = settings.OUTPUT_DIR / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(path=filepath, filename=filename)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download file")

# Delete file
@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a generated file"""
    try:
        filepath = settings.OUTPUT_DIR / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        filepath.unlink()
        logger.info(f"Deleted file: {filename}")
        
        return {"success": True, "message": f"Deleted {filename}"}
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

# Cache stats
@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    try:
        stats = PromptProcessor.get_cache_stats()
        return {
            "status": "ok",
            "cache": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Clear cache
@app.delete("/cache")
async def clear_cache():
    """Clear entire cache"""
    try:
        PromptProcessor.clear_cache()
        logger.info("Cache cleared via API")
        return {
            "status": "cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyze routing
@app.get("/routing/analyze")
async def analyze_routing(prompt: str):
    """Analyze which backend would be selected"""
    try:
        processor = PromptProcessor()
        backend = processor.select_best_backend(prompt)
        
        return {
            "prompt": prompt,
            "length": len(prompt),
            "words": len(prompt.split()),
            "backend_selected": backend,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List backends
@app.get("/backends")
async def list_backends():
    """List available backends and their status"""
    try:
        return {
            "backends": {
                "openrouter": {
                    "name": "OpenRouter (Cloud)",
                    "status": "available" if settings.OR_API_KEY else "not configured",
                    "model": settings.OR_MODEL,
                    "best_for": "Fast, structured data, 100+ models"
                },
                "huggingface": {
                    "name": "HuggingFace Inference",
                    "status": "available" if settings.HF_API_KEY else "not configured",
                    "model": settings.HF_MODEL,
                    "best_for": "Free tier, fallback option"
                },
                "template": {
                    "name": "Template System",
                    "status": "always available",
                    "best_for": "Fallback, vague prompts"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Backends info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_generator(file_type: str, structured_output):
    """Get appropriate generator"""
    if file_type == 'pdf':
        return PDFGenerator(structured_output)
    elif file_type == 'excel':
        return ExcelGenerator(structured_output)
    elif file_type == 'docx':
        return DocxGenerator(structured_output)
    elif file_type == 'csv':
        return CSVJSONGenerator(structured_output, file_format='csv')
    elif file_type == 'json':
        return CSVJSONGenerator(structured_output, file_format='json')
    else:
        raise ValueError(f"Unknown file type: {file_type}")

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} API")
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        log_level="info"
    )