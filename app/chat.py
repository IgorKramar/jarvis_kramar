"""Chat management with history support"""
import json
from typing import Optional
from pathlib import Path
from .config import HISTORY_FILE, MAX_HISTORY_LENGTH, SYSTEM_PROMPT


class ChatHistory:
    """Manages chat conversation history"""
    
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        self.messages: list[dict[str, str]] = []
        self.history_file = Path(HISTORY_FILE)
        
        # Initialize with system prompt
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
    
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
