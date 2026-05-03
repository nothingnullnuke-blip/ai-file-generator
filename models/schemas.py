from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"

class DataType(str, Enum):
    TABLE = "table"
    CHART = "chart"
    TEXT = "text"
    HEADING = "heading"

class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"

class ColorScheme(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    VIBRANT = "vibrant"
    PROFESSIONAL = "professional"

class FileGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=5000)
    file_type: FileType = Field(default=FileType.PDF)
    color_scheme: ColorScheme = Field(default=ColorScheme.PROFESSIONAL)
    include_charts: bool = Field(default=True)
    
    @validator('prompt')
    def prompt_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class TableData(BaseModel):
    headers: List[str]
    rows: List[List[Any]]
    title: Optional[str] = None
    description: Optional[str] = None

class ChartData(BaseModel):
    type: ChartType
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    description: Optional[str] = None

class Section(BaseModel):
    type: DataType
    content: Dict[str, Any]
    order: int = 0

class StructuredOutput(BaseModel):
    title: str
    description: Optional[str] = None
    color_scheme: ColorScheme = ColorScheme.PROFESSIONAL
    sections: List[Section]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FileGenerationResponse(BaseModel):
    success: bool
    file_path: str
    file_type: FileType
    file_size_bytes: int
    generated_at: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    status_code: int