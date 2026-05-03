from abc import ABC, abstractmethod
from pathlib import Path
from config.settings import settings
from models.schemas import StructuredOutput, ColorScheme
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ColorPalette:
    PALETTES = {
        ColorScheme.PROFESSIONAL: {
            "primary": "#2C3E50",
            "secondary": "#3498DB",
            "accent": "#E74C3C",
            "light": "#ECF0F1",
            "dark": "#34495E"
        },
        ColorScheme.MODERN: {
            "primary": "#1A1A2E",
            "secondary": "#0F3460",
            "accent": "#E94560",
            "light": "#F5F5F5",
            "dark": "#16213E"
        },
        ColorScheme.VIBRANT: {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#FFE66D",
            "light": "#F1F1F2",
            "dark": "#95E1D3"
        },
        ColorScheme.CLASSIC: {
            "primary": "#1F4788",
            "secondary": "#D4A574",
            "accent": "#8B4513",
            "light": "#F5F5DC",
            "dark": "#2C2C2C"
        }
    }
    
    @classmethod
    def get_palette(cls, scheme: ColorScheme) -> dict:
        return cls.PALETTES.get(scheme, cls.PALETTES[ColorScheme.PROFESSIONAL])

class BaseGenerator(ABC):
    def __init__(self, structured_output: StructuredOutput, output_filename: str = None):
        self.output = structured_output
        self.filename = output_filename or self._generate_filename()
        self.filepath = settings.OUTPUT_DIR / self.filename
        self.colors = ColorPalette.get_palette(structured_output.color_scheme)
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def generate(self) -> Path:
        pass
    
    def _generate_filename(self) -> str:
        from datetime import datetime
        import re
        
        title = self.output.title.lower()
        title = re.sub(r'[^a-z0-9]+', '_', title)
        title = title.strip('_')[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = self.get_file_extension()
        return f"{title}_{timestamp}.{ext}"
    
    @abstractmethod
    def get_file_extension(self) -> str:
        pass
    
    def get_section_by_type(self, data_type: str):
        return [s for s in self.output.sections if s.type == data_type]