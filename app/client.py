"""LM Studio API Client"""
import requests
from typing import Optional, Generator, Dict, Any
from .config import LM_STUDIO_BASE_URL, LM_STUDIO_MODEL


class LMStudioClient:
    """Client for interacting with LM Studio API"""
    
    def __init__(self, base_url: str = LM_STUDIO_BASE_URL, model: str = None):
        self.base_url = base_url.rstrip('/')
        self.model = model or LM_STUDIO_MODEL
        self.session = requests.Session()
    
    def get_available_models(self) -> list[str]:
        """Get list of available models from LM Studio"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return [model['id'] for model in data.get('data', [])]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            return []
    
    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = True
    ) -> Generator[str, None, None] | str:
        """Send chat completion request to LM Studio"""
        
        # Auto-detect model if not specified
        model = self.model
        if not model:
            models = self.get_available_models()
            if models:
                model = models[0]
            else:
                raise ValueError("No models available in LM Studio")
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_completion(payload)
            else:
                return self._non_stream_completion(payload)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to LM Studio: {e}")
    
    def _stream_completion(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream chat completion response"""
        payload["stream"] = True
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        import json
                        chunk = json.loads(data)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue
    
    def _non_stream_completion(self, payload: Dict[str, Any]) -> str:
        """Non-streaming chat completion response"""
        payload["stream"] = False
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
