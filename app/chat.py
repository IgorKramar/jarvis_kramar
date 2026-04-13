"""Chat management with history support"""
import json
from typing import Optional
from pathlib import Path
from .config import HISTORY_FILE, MAX_HISTORY_LENGTH, SYSTEM_PROMPT, SYSTEM_PROMPTS


class ChatHistory:
    """Manages chat conversation history"""
    
    def __init__(self, system_prompt: str = SYSTEM_PROMPT, language: str = "auto"):
        self.language = language
        self.system_prompt = system_prompt
        self.messages: list[dict[str, str]] = []
        self.history_file = Path(HISTORY_FILE)
        
        # Initialize with system prompt
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
    
    def update_system_prompt(self, language: str = None):
        """Update system prompt based on language setting"""
        if language:
            self.language = language
        
        new_prompt = SYSTEM_PROMPTS.get(self.language, SYSTEM_PROMPTS["en"])
        self.system_prompt = new_prompt
        
        # Update or add system prompt in messages
        if self.messages and self.messages[0].get('role') == 'system':
            self.messages[0]['content'] = new_prompt
        else:
            self.messages.insert(0, {
                "role": "system",
                "content": new_prompt
            })
    
    def set_language(self, language: str):
        """Set language and update system prompt"""
        if language not in SYSTEM_PROMPTS:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
        self.update_system_prompt(language)
    
    def get_language(self) -> str:
        """Get current language setting"""
        return self.language
    
    def add_user_message(self, content: str):
        """Add user message to history"""
        self.messages.append({
            "role": "user",
            "content": content
        })
    
    def add_assistant_message(self, content: str):
        """Add assistant response to history"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
    
    def get_messages(self) -> list[dict[str, str]]:
        """Get all messages in the conversation"""
        return self.messages.copy()
    
    def clear(self):
        """Clear conversation history (keep system prompt)"""
        if self.system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        else:
            self.messages = []
    
    def save_to_file(self):
        """Save chat history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_from_file(self):
        """Load chat history from file"""
        if not self.history_file.exists():
            return False
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                loaded_messages = json.load(f)
            
            # Keep system prompt and append loaded messages
            if self.system_prompt and loaded_messages:
                self.messages = [loaded_messages[0]] if loaded_messages[0].get('role') == 'system' else []
                self.messages.extend(loaded_messages[1:] if loaded_messages[0].get('role') == 'system' else loaded_messages)
            else:
                self.messages = loaded_messages
            
            # Trim history if too long
            if len(self.messages) > MAX_HISTORY_LENGTH:
                # Keep system prompt + last messages
                if self.messages[0].get('role') == 'system':
                    self.messages = [self.messages[0]] + self.messages[-(MAX_HISTORY_LENGTH-1):]
                else:
                    self.messages = self.messages[-MAX_HISTORY_LENGTH:]
            
            return True
        except Exception as e:
            print(f"Error loading history: {e}")
            return False
    
    def get_message_count(self) -> int:
        """Get number of messages (excluding system prompt)"""
        count = len(self.messages)
        if self.messages and self.messages[0].get('role') == 'system':
            count -= 1
        return count
