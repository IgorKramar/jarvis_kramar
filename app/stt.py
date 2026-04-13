"""
STT модуль на основе Vosk для распознавания речи.
Преобразует речь в текст с использованием модели Vosk.
"""

import sounddevice as sd
import vosk
import sys
import queue
import json
from typing import Callable, Optional
import os


class VoskSTT:
    """Класс для распознавания речи с использованием Vosk."""
    
    def __init__(self, modelpath: str = "model", samplerate: int = 16000):
        """
        Инициализирует STT модель Vosk.
        
        Args:
            modelpath: Путь к папке с моделью распознавания речи
            samplerate: Частота дискретизации аудио
        """
        self.__REC__ = None
        self.__Q__ = queue.Queue()
        self.__SAMPLERATE__ = samplerate
        self.__MODEL_PATH__ = modelpath
        
        # Подгружаем модель
        self._load_model()
    
    def _load_model(self):
        """Загружает модель Vosk."""
        try:
            # Проверяем существование пути к модели
            if not os.path.exists(self.__MODEL_PATH__):
                print(f"STT: Model path '{self.__MODEL_PATH__}' does not exist.")
                print("STT: Please download a model from https://alphacephei.com/vosk/models")
                print("STT: And extract it to the specified path.")
                raise FileNotFoundError(f"Model path not found: {self.__MODEL_PATH__}")
            
            self.__REC__ = vosk.KaldiRecognizer(
                vosk.Model(self.__MODEL_PATH__), 
                self.__SAMPLERATE__
            )
            print(f"STT: Model loaded from {self.__MODEL_PATH__}")
        except Exception as e:
            print(f"STT: Error loading model: {e}")
            raise
    
    def q_callback(self, indata, _, __, status):
        """Callback для обработки входящих аудиоданных."""
        if status:
            print(status, file=sys.stderr)
        self.__Q__.put(bytes(indata))
    
    def listen(self, executor: Callable[[str], None]):
        """
        Запускает непрерывное прослушивание и обработку речи.
        
        Args:
            executor: Функция, которая будет вызвана с распознанным текстом
        """
        if not self.__REC__:
            print("STT: Model not loaded")
            return
        
        try:
            with sd.RawInputStream(
                samplerate=self.__SAMPLERATE__,
                blocksize=8000,
                device=None,  # Используем устройство по умолчанию
                dtype='int16',
                channels=1,
                callback=self.q_callback
            ):
                print("STT: Listening...")
                while True:
                    data = self.__Q__.get()
                    if self.__REC__.AcceptWaveform(data):
                        result = json.loads(self.__REC__.Result())
                        text = result.get("text", "")
                        if text:
                            executor(text)
                    else:
                        # Частичный результат (можно использовать для отображения в реальном времени)
                        partial = json.loads(self.__REC__.PartialResult())
                        if partial.get("partial"):
                            pass  # Можно обработать частичный результат если нужно
        except KeyboardInterrupt:
            print("STT: Stopped by user")
        except Exception as e:
            print(f"STT: Error during listening: {e}")
    
    def listen_once(self, executor: Optional[Callable[[str], None]] = None, timeout_seconds: float = 10.0) -> Optional[str]:
        """
        Слушает одну фразу и возвращает распознанный текст.
        
        Args:
            executor: Опциональная функция, которая будет вызвана с распознанным текстом
            timeout_seconds: Таймаут ожидания речи в секундах
            
        Returns:
            Распознанный текст или None
        """
        if not self.__REC__:
            print("STT: Model not loaded")
            return None
        
        import time
        result_text = None
        start_time = time.time()
        
        try:
            with sd.RawInputStream(
                samplerate=self.__SAMPLERATE__,
                blocksize=8000,
                device=None,
                dtype='int16',
                channels=1,
                callback=self.q_callback
            ):
                print("STT: Listening for one phrase...")
                while time.time() - start_time < timeout_seconds:
                    if not self.__Q__.empty():
                        data = self.__Q__.get()
                        if self.__REC__.AcceptWaveform(data):
                            result = json.loads(self.__REC__.Result())
                            result_text = result.get("text", "")
                            if result_text:
                                print(f"STT: Recognized: {result_text}")
                                if executor:
                                    executor(result_text)
                                break
        except KeyboardInterrupt:
            print("STT: Stopped by user")
        except Exception as e:
            print(f"STT: Error during listening: {e}")
        
        return result_text
