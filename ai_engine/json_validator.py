import json
import re
from typing import Dict, Any, Optional
from models.schemas import StructuredOutput
from utils.logger import setup_logger

logger = setup_logger(__name__)

class JSONValidator:
    @staticmethod
    def validate_and_repair(raw_output: str, max_retries: int = 2) -> Dict[str, Any]:
        logger.debug(f"Validating JSON from AI output (length: {len(raw_output)})")
        
        # Attempt 1: Direct JSON parse
        json_dict = JSONValidator._extract_json(raw_output)
        if json_dict:
            validated = JSONValidator._validate_schema(json_dict)
            if validated:
                logger.info("✅ JSON validation passed on first attempt")
                return json_dict
        
        # Attempt 2: Repair common issues
        logger.warning("⚠️ First extraction failed, attempting repair...")
        for attempt in range(max_retries):
            repaired = JSONValidator._repair_json(raw_output)
            if repaired:
                json_dict = JSONValidator._extract_json(repaired)
                if json_dict:
                    validated = JSONValidator._validate_schema(json_dict)
                    if validated:
                        logger.info(f"✅ JSON validation passed after repair (attempt {attempt + 1})")
                        return json_dict
        
        # Fallback: Return default template
        logger.error("❌ JSON repair failed, using default template")
        return JSONValidator._get_default_template(raw_output)
    
    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        # Strategy 1: Find JSON between braces
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            try:
                json_str = text[first_brace:last_brace + 1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Direct parse attempt
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        logger.debug("No valid JSON found in AI output")
        return None
    
    @staticmethod
    def _repair_json(text: str) -> str:
        # Remove markdown code fences
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Fix trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Fix unquoted keys
        text = re.sub(r'(\{|,)\s*([a-zA-Z_]\w*)\s*:', r'\1 "\2":', text)
        
        logger.debug("Attempted JSON repair")
        return text
    
    @staticmethod
    def _validate_schema(data: Dict[str, Any]) -> bool:
        try:
            if 'title' not in data:
                return False
            
            if 'sections' not in data or not isinstance(data['sections'], list):
                return False
            
            if len(data['sections']) == 0:
                return False
            
            for idx, section in enumerate(data['sections']):
                if not isinstance(section, dict):
                    return False
                
                if 'type' not in section:
                    return False
                
                if 'content' not in section:
                    return False
            
            logger.info("Schema validation passed")
            return True
            
        except Exception as e:
            logger.warning(f"Schema validation error: {str(e)}")
            return False
    
    @staticmethod
    def _get_default_template(raw_output: str) -> Dict[str, Any]:
        logger.info("Using default fallback template")
        
        lines = raw_output.split('\n')
        title = "Generated Document"
        for line in lines[:5]:
            clean_line = line.strip()
            if clean_line and len(clean_line) > 5 and len(clean_line) < 100:
                title = clean_line.replace('#', '').strip()
                break
        
        return {
            "title": title,
            "description": "Generated from your prompt",
            "color_scheme": "professional",
            "sections": [
                {
                    "type": "heading",
                    "content": {"text": "Content"},
                    "order": 0
                },
                {
                    "type": "text",
                    "content": {"text": raw_output[:1000]},
                    "order": 1
                }
            ],
            "metadata": {
                "generated": True,
                "fallback": True
            }
        }
    
    @staticmethod
    def validate_pydantic(json_dict: Dict[str, Any]) -> StructuredOutput:
        try:
            logger.debug("🔐 Validating with Pydantic...")
            structured_output = StructuredOutput(**json_dict)
            logger.info("✅ Pydantic validation passed")
            return structured_output
            
        except Exception as e:
            logger.error(f"❌ Pydantic validation failed: {str(e)}")
            logger.warning("   Using minimal fallback StructuredOutput")
            
            fallback = {
                "title": json_dict.get("title", "Document"),
                "description": json_dict.get("description"),
                "color_scheme": "professional",
                "sections": [
                    {
                        "type": "text",
                        "content": {"text": str(json_dict.get("sections", []))},
                        "order": 0
                    }
                ],
                "metadata": {"fallback": True}
            }
            
            return StructuredOutput(**fallback)