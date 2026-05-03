import requests
import time
from typing import Optional
from utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

class OpenRouterBackend:
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    AVAILABLE_MODELS = {
        "mistral-7b": "mistralai/mistral-7b-instruct",
        "mistral-medium": "mistralai/mistral-medium",
        "llama-2-70b": "meta-llama/llama-2-70b-chat",
        "gpt-3.5": "openai/gpt-3.5-turbo",
        "gpt-4": "openai/gpt-4",
        "claude-2": "anthropic/claude-2",
    }
    
    def __init__(self):
        self.api_key = settings.OR_API_KEY
        self.model = settings.OR_MODEL
        self.timeout = 30
        
        if not self.api_key:
            logger.warning("⚠️ OR_API_KEY not configured")
    
    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        if not self.api_key:
            logger.error("❌ OR_API_KEY not configured")
            return None
        
        try:
            logger.debug(f"🤖 OpenRouter: {self.model}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/nothingnullnuke-blip/ai-file-generator"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.95
            }
            
            start_time = time.time()
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"]
                    usage = result.get("usage", {})
                    
                    logger.info(
                        f"📨 OpenRouter response in {elapsed:.2f}s "
                        f"({len(text)} chars, "
                        f"{usage.get('prompt_tokens', 0)}→{usage.get('completion_tokens', 0)} tokens)"
                    )
                    return text
            
            elif response.status_code == 429:
                logger.error("⏱️ OpenRouter rate limit")
                return None
            elif response.status_code == 401:
                logger.error("❌ OpenRouter auth failed")
                return None
            elif response.status_code == 402:
                logger.error("💳 OpenRouter: insufficient credits")
                return None
            else:
                logger.error(f"❌ OpenRouter {response.status_code}: {response.text[:200]}")
                return None
            
        except requests.Timeout:
            logger.error(f"⏱️ OpenRouter timeout ({self.timeout}s)")
            return None
        except Exception as e:
            logger.error(f"❌ OpenRouter error: {str(e)}")
            return None