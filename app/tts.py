"""
TTS модуль на основе Silero для синтеза речи.
Преобразует текст в речь с использованием нейронной модели Silero.
"""

import sounddevice as sd
import torch
import time
from typing import Optional


# Константы голосов, поддерживаемых в Silero
SPEAKER_AIDAR = "aidar"
SPEAKER_BAYA = "baya"
SPEAKER_KSENIYA = "kseniya"
SPEAKER_XENIA = "xenia"
SPEAKER_EUS = "eus"
SPEAKER_RANDOM = "random"

# Константы девайсов для работы torch
DEVICE_CPU = "cpu"
DEVICE_CUDA = "cuda"
DEVICE_VULKAN = "vulkan"
DEVICE_OPENGL = "opengl"
DEVICE_OPENCL = "opencl"


class SileroTTS:
    """Класс для синтеза речи с использованием Silero TTS."""
    
    def __init__(
        self, 
        speaker: str = SPEAKER_BAYA, 
        device: str = DEVICE_CPU, 
        samplerate: int = 48000
    ):
        """
        Инициализирует TTS модель Silero.
        
        Args:
            speaker: Имя голоса (aidar, baya, kseniya, xenia, eus, random)
            device: Устройство для вычислений (cpu, cuda, vulkan, opengl, opencl)
            samplerate: Частота дискретизации аудио
        """
        self.__MODEL__ = None
        self.__SPEAKER__ = speaker
        self.__SAMPLERATE__ = samplerate
        self.__DEVICE__ = device
        
        # Подгружаем модель
        self._load_model()
    
    def _load_model(self):
        """Загружает модель Silero TTS."""
        try:
            self.__MODEL__, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_tts",
                language="ru",
                speaker="ru_v3"
            )
            self.__MODEL__.to(torch.device(self.__DEVICE__))
            print(f"TTS: Model loaded on device {self.__DEVICE__}")
        except Exception as e:
            print(f"TTS: Error loading model: {e}")
            raise
    
    def text2speech(self, text: str, play: bool = True) -> Optional[bytes]:
        """
        Преобразует текст в речь и воспроизводит его.
        
        Args:
            text: Текст для озвучивания (можно использовать + для указания ударения)
            play: Воспроизводить ли аудио (по умолчанию True)
            
        Returns:
            Аудиоданные или None при ошибке
        """
        if not self.__MODEL__:
            print("TTS: Model not loaded")
            return None
        
        try:
            # Генерируем аудио из текста
            audio = self.__MODEL__.apply_tts(
                text=text,
                speaker=self.__SPEAKER__,
                sample_rate=self.__SAMPLERATE__,
                put_accent=True,
                put_yo=True
            )
            
            # Проигрываем то что получилось если requested
            if play:
                sd.play(audio, samplerate=self.__SAMPLERATE__)
                time.sleep(len(audio) / self.__SAMPLERATE__)
                sd.stop()
            
            return audio
        except Exception as e:
            print(f"TTS: Error generating speech: {e}")
            return None
    
    def set_speaker(self, speaker: str):
        """Устанавливает новый голос."""
        if speaker in [SPEAKER_AIDAR, SPEAKER_BAYA, SPEAKER_KSENIYA, 
                       SPEAKER_XENIA, SPEAKER_EUS, SPEAKER_RANDOM]:
            self.__SPEAKER__ = speaker
            print(f"TTS: Speaker changed to {speaker}")
        else:
            print(f"TTS: Unknown speaker {speaker}")
    
    def set_device(self, device: str):
        """Устанавливает новое устройство для вычислений."""
        if device in [DEVICE_CPU, DEVICE_CUDA, DEVICE_VULKAN, 
                      DEVICE_OPENGL, DEVICE_OPENCL]:
            self.__DEVICE__ = device
            print(f"TTS: Device changed to {device}")
            # Перезагружаем модель на новом устройстве
            if self.__MODEL__:
                self.__MODEL__.to(torch.device(device))
        else:
            print(f"TTS: Unknown device {device}")
