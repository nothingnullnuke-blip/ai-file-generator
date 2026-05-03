import requests
import time
from typing import Optional
from utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class HuggingFaceBackend:
    API_URL = "https://api-inference.huggingface.co/models/{model}"
    
    AVAILABLE_MODELS = {
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.2",
        "zephyr-7b": "HuggingFaceH4/zephyr-7b-beta",
        "neural-8b": "NousResearch/Neural-Chat-7B-v3-1",
    }
    
    def __init__(self):
        self.api_key = settings.HF_API_KEY
        self.model = settings.HF_MODEL
        self.timeout = 30
        
        if not self.api_key:
            logger.warning("⚠️ HF_API_KEY not configured")
    
    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        if not self.api_key:
            logger.error("❌ HF_API_KEY not configured")
            return None
        
        try:
            logger.debug(f"🤖 HuggingFace: {self.model}")
            
            url = self.API_URL.format(model=self.model)
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": f"{system_prompt}\n\nUser Request: {prompt}",
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "do_sample": True,
                }
            }
            
            start_time = time.time()
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    logger.info(f"📨 HuggingFace response in {elapsed:.2f}s ({len(text)} chars)")
                    return text
            
            elif response.status_code == 429:
                logger.error("⏱️ HuggingFace rate limit")
                return None
            elif response.status_code == 401:
                logger.error("❌ HuggingFace auth failed")
                return None
            else:
                logger.error(f"❌ HuggingFace {response.status_code}")
                return None
            
        except requests.Timeout:
            logger.error(f"⏱️ HuggingFace timeout ({self.timeout}s)")
            return None
        except Exception as e:
            logger.error(f"❌ HuggingFace error: {str(e)}")
            return None