import hashlib
import time
import re
import threading
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from utils.logger import setup_logger
from config.settings import settings
from models.schemas import StructuredOutput
from ai_engine.json_validator import JSONValidator
from ai_engine.openrouter_backend import OpenRouterBackend
from ai_engine.huggingface_backend import HuggingFaceBackend

logger = setup_logger(__name__)

class CacheEntry:
    def __init__(self, data: StructuredOutput, ttl_hours: int = 24):
        self.data = data
        self.created_at = datetime.now()
        self.ttl = timedelta(hours=ttl_hours)
    
    def is_expired(self) -> bool:
        return datetime.now() > (self.created_at + self.ttl)
    
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()

class PromptProcessor:
    _cache: Dict[str, CacheEntry] = {}
    _cache_max_size = 100
    _cache_ttl_hours = 24
    
    def __init__(self):
        self.openrouter = OpenRouterBackend()
        self.huggingface = HuggingFaceBackend()
        self.timeout_seconds = settings.AI_TIMEOUT
        logger.info("✅ PromptProcessor initialized (cloud-based backends)")
    
    def process(self, prompt: str, file_type: str = "pdf") -> StructuredOutput:
        logger.info(f"🔄 Processing: {prompt[:80]}...")
        
        cache_hit = self._check_cache(prompt, file_type)
        if cache_hit:
            output, age = cache_hit
            logger.info(f"⚡ Cache hit (age: {age:.1f}s)")
            return output
        
        backend = self.select_best_backend(prompt)
        logger.info(f"🔀 Backend: {backend}")
        
        if backend == "template":
            logger.info("📋 Using template (skipping API)")
            output = self._get_fallback_output(prompt)
            self._cache_result(prompt, file_type, output)
            return output
        
        system_prompt = self._build_system_prompt(file_type)
        
        logger.info("📍 Attempt 1: Calling AI backend...")
        raw_output = self._call_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            backend=backend,
            temperature=settings.AI_TEMPERATURE,
            attempt=1
        )
        
        if raw_output:
            output = self._validate_and_convert(raw_output, attempt=1)
            if output:
                logger.info("✅ SUCCESS: First attempt")
                self._cache_result(prompt, file_type, output)
                return output
        
        logger.warning("⚠️ First attempt failed, retrying...")
        logger.info("📍 Attempt 2: Retry with enhanced params...")
        
        retry_prompt = self._prepare_retry_prompt(prompt)
        raw_output = self._call_ai(
            prompt=retry_prompt,
            system_prompt=system_prompt,
            backend=backend,
            temperature=0.2,
            attempt=2
        )
        
        if raw_output:
            output = self._validate_and_convert(raw_output, attempt=2)
            if output:
                logger.info("✅ SUCCESS: Retry")
                self._cache_result(prompt, file_type, output)
                return output
        
        logger.error("❌ AI failed on both attempts")
        logger.info("📍 Using template fallback...")
        output = self._get_fallback_output(prompt)
        self._cache_result(prompt, file_type, output)
        return output
    
    def select_best_backend(self, prompt: str) -> str:
        logger.debug("🔍 Analyzing prompt...")
        
        prompt_length = len(prompt)
        word_count = len(prompt.split())
        
        if prompt_length < 20 or word_count < 5:
            logger.debug("   → Too short, use template")
            return "template"
        
        vague = any(re.search(p, prompt.lower()) 
                   for p in [r'help', r'create something', r'\?{2,}'])
        if vague:
            logger.debug("   → Vague prompt, use template")
            return "template"
        
        if settings.OR_API_KEY:
            logger.debug("   → Using OpenRouter")
            return "openrouter"
        elif settings.HF_API_KEY:
            logger.debug("   → Using HuggingFace")
            return "huggingface"
        else:
            logger.warning("   → No API keys configured, using template")
            return "template"
    
    def _call_ai(
        self,
        prompt: str,
        system_prompt: str,
        backend: str,
        temperature: float,
        attempt: int = 1
    ) -> Optional[str]:
        logger.info(f"📞 Calling {backend} (attempt {attempt}, temp={temperature})")
        
        start_time = time.time()
        
        try:
            if backend == "openrouter":
                raw_output = self._call_with_timeout(
                    lambda: self.openrouter.generate(
                        prompt, system_prompt, temperature,
                        settings.AI_MAX_TOKENS
                    )
                )
            elif backend == "huggingface":
                raw_output = self._call_with_timeout(
                    lambda: self.huggingface.generate(
                        prompt, system_prompt, temperature,
                        settings.AI_MAX_TOKENS
                    )
                )
            else:
                logger.error(f"Unknown backend: {backend}")
                return None
            
            elapsed = time.time() - start_time
            
            if raw_output:
                logger.info(f"📨 Response in {elapsed:.2f}s ({len(raw_output)} chars)")
                return raw_output
            else:
                logger.warning(f"Empty response from {backend}")
                return None
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {backend} failed after {elapsed:.2f}s: {str(e)}")
            return None
    
    def _call_with_timeout(self, func, timeout: int = None) -> Optional[str]:
        if timeout is None:
            timeout = self.timeout_seconds
        
        result = [None]
        
        def wrapper():
            result[0] = func()
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            logger.error(f"⏱️ Timeout ({timeout}s exceeded)")
            return None
        
        return result[0]
    
    def _prepare_retry_prompt(self, prompt: str) -> str:
        logger.debug("📝 Preparing retry prompt...")
        
        core = prompt[:100].strip()
        enhanced = (
            f"{core}\n\n"
            f"CRITICAL: Respond with ONLY valid JSON. No markdown.\n"
            f"Start with {{ end with }}. INVALID OUTPUT FAILS."
        )
        
        logger.debug(f"   Original: {len(prompt)} chars → Retry: {len(enhanced)} chars")
        return enhanced
    
    def _validate_and_convert(self, raw_output: str, attempt: int = 1) -> Optional[StructuredOutput]:
        try:
            logger.info(f"🔍 JSON validation (Attempt {attempt})...")
            
            json_dict = JSONValidator.validate_and_repair(raw_output, max_retries=2)
            logger.info("✅ JSON repair passed")
            
            output = JSONValidator.validate_pydantic(json_dict)
            logger.info("✨ Validation complete")
            
            return output
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            return None
    
    @classmethod
    def _get_cache_key(cls, prompt: str, file_type: str) -> str:
        combined = f"{prompt}_{file_type}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _check_cache(self, prompt: str, file_type: str) -> Optional[Tuple[StructuredOutput, float]]:
        cache_key = self._get_cache_key(prompt, file_type)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            
            if not entry.is_expired():
                age = entry.age_seconds()
                logger.info(f"✅ Cache hit (age: {age:.1f}s)")
                return (entry.data, age)
            else:
                del self._cache[cache_key]
        
        return None
    
    def _cache_result(self, prompt: str, file_type: str, output: StructuredOutput):
        cache_key = self._get_cache_key(prompt, file_type)
        
        if len(self._cache) >= self._cache_max_size:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at
            )
            del self._cache[oldest_key]
        
        self._cache[cache_key] = CacheEntry(output, self._cache_ttl_hours)
        logger.debug(f"💾 Cached (size: {len(self._cache)}/{self._cache_max_size})")
    
    @classmethod
    def clear_cache(cls):
        size = len(cls._cache)
        cls._cache.clear()
        logger.info(f"🗑️ Cache cleared ({size} entries)")
    
    @classmethod
    def get_cache_stats(cls) -> Dict:
        return {
            "total": len(cls._cache),
            "max": cls._cache_max_size,
            "usage_percent": (len(cls._cache) / cls._cache_max_size) * 100
        }
    
    def _get_fallback_output(self, prompt: str) -> StructuredOutput:
        logger.warning("🔧 FALLBACK: Using template...")
        
        title = prompt.split('.')[0][:80].strip()
        if not title or len(title) < 3:
            title = "Generated Document"
        
        fallback_dict = {
            "title": title,
            "description": "Generated with template system.",
            "color_scheme": "professional",
            "sections": [
                {
                    "type": "heading",
                    "content": {"text": "Content"},
                    "order": 0
                },
                {
                    "type": "text",
                    "content": {"text": prompt[:1000]},
                    "order": 1
                },
                {
                    "type": "text",
                    "content": {
                        "text": "Note: Template used. For better results, use API keys or more specific prompts."
                    },
                    "order": 2
                }
            ],
            "metadata": {
                "generated": True,
                "fallback": True,
                "reason": "No API or AI failed"
            }
        }
        
        output = JSONValidator.validate_pydantic(fallback_dict)
        logger.info("✅ Fallback generated")
        return output
    
    def _build_system_prompt(self, file_type: str) -> str:
        return f"""You are a professional document generator AI.

CRITICAL: Output MUST be ONLY valid JSON. No markdown, no code blocks.
Start with {{ and end with }}. NOTHING ELSE.

Task: Convert user's prompt into JSON document structure for {file_type} files.

REQUIRED STRUCTURE:
{{
    "title": "Document Title",
    "description": "Optional description",
    "color_scheme": "professional",
    "sections": [
        {{
            "type": "heading",
            "content": {{"text": "Content"}},
            "order": 0
        }}
    ],
    "metadata": {{"generated": true}}
}}

VALID VALUES:
- color_scheme: "professional", "modern", "vibrant", "classic"
- section.type: "heading", "text", "table", "chart"
- section.order: 0, 1, 2, 3... (sequential)

CONTENT TYPES:

HEADING/TEXT:
{{"type": "heading", "content": {{"text": "Title"}}, "order": 0}}

TABLE:
{{
    "type": "table",
    "content": {{
        "title": "Table Name",
        "headers": ["Col1", "Col2"],
        "rows": [["Data1", "Data2"]]
    }},
    "order": 1
}}

CHART:
{{
    "type": "chart",
    "content": {{
        "type": "bar",
        "title": "Chart Title",
        "labels": ["A", "B"],
        "datasets": [{{"name": "Series1", "values": [10, 20]}}]
    }},
    "order": 2
}}

RULES:
✓ Valid JSON (no trailing commas)
✓ At least 2 sections
✓ All strings quoted
✓ section.order sequential

RESPOND WITH ONLY JSON."""