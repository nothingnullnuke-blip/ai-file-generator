from config.settings import settings
from models.schemas import FileType
import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

class PromptValidator:
    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        if not prompt or len(prompt) < settings.MIN_PROMPT_LENGTH:
            raise ValueError(f"Prompt must be at least {settings.MIN_PROMPT_LENGTH} characters")
        
        if len(prompt) > settings.MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt cannot exceed {settings.MAX_PROMPT_LENGTH} characters")
        
        return True
    
    @staticmethod
    def validate_file_type(file_type: str) -> bool:
        valid_types = [ft.value for ft in FileType]
        if file_type not in valid_types:
            raise ValueError(f"Invalid file type. Must be one of {valid_types}")
        return True