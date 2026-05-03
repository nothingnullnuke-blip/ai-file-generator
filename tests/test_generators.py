import pytest
from ai_engine.prompt_processor import PromptProcessor
from models.schemas import StructuredOutput
from generators.pdf_generator import PDFGenerator
from generators.excel_generator import ExcelGenerator
from pathlib import Path

@pytest.fixture
def processor():
    return PromptProcessor()

@pytest.fixture
def sample_output():
    return StructuredOutput(
        title="Test Document",
        description="Test",
        color_scheme="professional",
        sections=[
            {
                "type": "heading",
                "content": {"text": "Test"},
                "order": 0
            },
            {
                "type": "text",
                "content": {"text": "Test content"},
                "order": 1
            }
        ]
    )

def test_processor_initialization(processor):
    assert processor is not None
    assert processor.timeout_seconds == 30

def test_cache_operations(processor):
    PromptProcessor.clear_cache()
    assert len(PromptProcessor._cache) == 0
    
    stats = PromptProcessor.get_cache_stats()
    assert stats["total"] == 0

def test_backend_selection(processor):
    backend = processor.select_best_backend("short")
    assert backend == "template"
    
    backend = processor.select_best_backend("This is a longer prompt with meaningful content")
    assert backend in ["openrouter", "huggingface", "template"]

def test_pdf_generation(sample_output):
    generator = PDFGenerator(sample_output)
    assert generator.get_file_extension() == "pdf"

def test_excel_generation(sample_output):
    generator = ExcelGenerator(sample_output)
    assert generator.get_file_extension() == "xlsx"