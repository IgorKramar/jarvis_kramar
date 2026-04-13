"""
Голосовой модуль для Джарвиса Крамара.
Обеспечивает распознавание речи (STT) и синтез речи (TTS).
"""

import speech_recognition as sr
import pyttsx3
import threading
from typing import Optional, Callable


class VoiceManager:
    """Управляет голосовым вводом и выводом."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        self.engine = pyttsx3.init()
        self.is_listening = False
        self._stop_listening = False
        
        # Настройка голоса TTS
        self._setup_voice()
        
    def _setup_voice(self):
        """Настраивает параметры голоса для британского дворецкого."""
        voices = self.engine.getProperty('voices')
        
        # Пытаемся найти английский голос (предпочтительно британский)
        english_voice = None
        russian_voice = None
        
        for voice in voices:
            if hasattr(voice, 'languages') and voice.languages:
                lang_str = str(voice.languages).lower()
                if 'en-gb' in lang_str or 'en_uk' in lang_str:
                    english_voice = voice.id
                    break
                elif 'en' in lang_str and not english_voice:
                    english_voice = voice.id
                elif 'ru' in lang_str:
                    russian_voice = voice.id
        
        # Устанавливаем голос (по умолчанию английский для Джарвиса)
        if english_voice:
            self.engine.setProperty('voice', english_voice)
        elif russian_voice:
            self.engine.setProperty('voice', russian_voice)
        
        # Настройка скорости и тона
        self.engine.setProperty('rate', 175)  # Немного медленнее для важности
        self.engine.setProperty('volume', 0.9)  # Громкость
        
    def set_language(self, language: str):
        """Переключает язык синтеза речи."""
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            if hasattr(voice, 'languages') and voice.languages:
                lang_str = str(voice.languages).lower()
                if language == 'ru' and 'ru' in lang_str:
                    self.engine.setProperty('voice', voice.id)
                    self.engine.setProperty('rate', 160)  # Для русского чуть медленнее
                    return True
                elif language in ['en', 'auto'] and ('en-gb' in lang_str or 'en_uk' in lang_str or 'en' in lang_str):
                    self.engine.setProperty('voice', voice.id)
                    self.engine.setProperty('rate', 175)
                    return True
        
        return False
        
    def initialize_microphone(self) -> bool:
        """Инициализирует микрофон для записи."""
        try:
            self.microphone = sr.Microphone()
            # Калибровка шума
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            return True
        except Exception as e:
            print(f"Voice: Error initializing microphone: {e}")
            return False
            
    def speak(self, text: str, callback: Optional[Callable] = None):
        """
        Озвучивает текст.
        
        Args:
            text: Текст для озвучивания
            callback: Функция обратного вызова после завершения
        """
        def _speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                if callback:
                    callback()
            except Exception as e:
                print(f"Voice: Error speaking: {e}")
                if callback:
                    callback()
        
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()
        
    def listen_once(self, language: str = 'en-US', callback: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        Слушает одну фразу и возвращает распознанный текст.
        
        Args:
            language: Язык распознавания (en-US, ru-RU, etc.)
            callback: Функция обратного вызова с результатом
            
        Returns:
            Распознанный текст или None
        """
        if not self.microphone:
            if not self.initialize_microphone():
                return None
                
        try:
            with self.microphone as source:
                print("Voice: Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                
            print("Voice: Recognizing...")
            # Используем Google Speech Recognition (бесплатно, требует интернет)
            # Можно заменить на Whisper локально
            text = self.recognizer.recognize_google(audio, language=language)
            print(f"Voice: Recognized: {text}")
            
            if callback:
                callback(text)
                
            return text
            
        except sr.WaitTimeoutError:
            print("Voice: No speech detected")
            return None
        except sr.UnknownValueError:
            print("Voice: Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Voice: Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"Voice: Error during recognition: {e}")
            return None
            
    def start_continuous_listening(self, language: str = 'en-US', 
                                   on_speech: Optional[Callable[[str], None]] = None):
        """
        Запускает непрерывное прослушивание в фоновом потоке.
        
        Args:
            language: Язык распознавания
            on_speech: Callback при распознавании речи
        """
        if not self.microphone:
            if not self.initialize_microphone():
                return
                
        self.is_listening = True
        self._stop_listening = False
        
        def _listen_loop():
            while self.is_listening and not self._stop_listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=15)
                    
                    text = self.recognizer.recognize_google(audio, language=language)
                    if text and on_speech:
                        on_speech(text)
                        
                except sr.WaitTimeoutError:
                    continue
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
        try:
            # Проверка микрофона
            mic_available = True
            try:
                test_mic = sr.Microphone()
                test_mic.__enter__()
                test_mic.__exit__(None, None, None)
            except:
                mic_available = False
            
            # Проверка движка TTS
            tts_available = True
            try:
                test_engine = pyttsx3.init()
                test_engine.say("test")
            except:
                tts_available = False
                
            return mic_available or tts_available
        except:
            return False


# Глобальный экземпляр
_voice_manager: Optional[VoiceManager] = None


def get_voice_manager() -> VoiceManager:
    """Получает глобальный экземпляр VoiceManager."""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoiceManager()
    return _voice_manager
