"""
Голосовой модуль для Джарвиса Крамара.
Обеспечивает распознавание речи (STT) и синтез речи (TTS).
Использует Silero для TTS и Vosk для STT.
"""

import threading
from typing import Optional, Callable

from .tts import SileroTTS, SPEAKER_BAYA, DEVICE_CPU
from .stt import VoskSTT


class VoiceManager:
    """Управляет голосовым вводом и выводом."""

    def __init__(self, tts_speaker: str = SPEAKER_BAYA, 
                 tts_device: str = DEVICE_CPU,
                 stt_model_path: str = "model"):
        self.tts: Optional[SileroTTS] = None
        self.stt: Optional[VoskSTT] = None
        self.is_listening = False
        self._stop_listening = False
        
        # Инициализация TTS
        try:
            self.tts = SileroTTS(speaker=tts_speaker, device=tts_device)
            print("Voice: TTS initialized with Silero")
        except Exception as e:
            print(f"Voice: Error initializing TTS: {e}")
        
        # Инициализация STT
        try:
            self.stt = VoskSTT(modelpath=stt_model_path)
            print("Voice: STT initialized with Vosk")
        except Exception as e:
            print(f"Voice: Error initializing STT: {e}")
        
    def set_language(self, language: str):
        """Переключает язык синтеза речи."""
        # Silero поддерживает в основном русский язык
        # Для других языков можно использовать другие модели
        if language == 'ru':
            print("Voice: Russian language selected")
            return True
        else:
            print(f"Voice: Language {language} may not be fully supported by Silero TTS")
            return False
        
    def speak(self, text: str, callback: Optional[Callable] = None):
        """
        Озвучивает текст.
        
        Args:
            text: Текст для озвучивания (можно использовать + для указания ударения)
            callback: Функция обратного вызова после завершения
        """
        def _speak_thread():
            try:
                if self.tts:
                    # В headless среде или при отсутствии аудиоустройства play=False
                    # можно установить через переменную окружения или конфигурацию
                    self.tts.text2speech(text, play=True)
                if callback:
                    callback()
            except Exception as e:
                print(f"Voice: Error speaking: {e}")
                if callback:
                    callback()
        
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()
        
    def listen_once(self, language: str = 'ru-RU', callback: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        Слушает одну фразу и возвращает распознанный текст.
        
        Args:
            language: Язык распознавания (для Vosk используется модель языка)
            callback: Функция обратного вызова с результатом
            
        Returns:
            Распознанный текст или None
        """
        if not self.stt:
            print("Voice: STT not initialized")
            return None
        
        def _listen_callback(text):
            if callback:
                callback(text)
                
        return self.stt.listen_once(executor=_listen_callback)
            
    def start_continuous_listening(self, language: str = 'ru-RU', 
                                   on_speech: Optional[Callable[[str], None]] = None):
        """
        Запускает непрерывное прослушивание в фоновом потоке.
        
        Args:
            language: Язык распознавания (для Vosk используется модель языка)
            on_speech: Callback при распознавании речи
        """
        if not self.stt:
            print("Voice: STT not initialized")
            return
                
        self.is_listening = True
        self._stop_listening = False
        
        def _listen_loop():
            while self.is_listening and not self._stop_listening:
                try:
                    # Используем listen с executor
                    self.stt.listen(on_speech)
                except Exception as e:
                    if self.is_listening:
                        print(f"Voice: Continuous listening error: {e}")
                    continue
                    
        thread = threading.Thread(target=_listen_loop, daemon=True)
        thread.start()
        
    def stop_listening(self):
        """Останавливает непрерывное прослушивание."""
        self.is_listening = False
        self._stop_listening = True
        
    def is_available(self) -> bool:
        """Проверяет доступность голосовых функций."""
        tts_available = self.tts is not None
        stt_available = self.stt is not None
        return tts_available or stt_available


# Глобальный экземпляр
_voice_manager: Optional[VoiceManager] = None


def get_voice_manager(tts_speaker: str = SPEAKER_BAYA, 
                      tts_device: str = DEVICE_CPU,
                      stt_model_path: str = "model") -> VoiceManager:
    """Получает глобальный экземпляр VoiceManager."""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoiceManager(
            tts_speaker=tts_speaker,
            tts_device=tts_device,
            stt_model_path=stt_model_path
        )
    return _voice_manager
