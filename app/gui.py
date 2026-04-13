"""
Графический интерфейс в стиле Тони Старка + Викторианская Англия + Стимпанк
"""

import customtkinter as ctk
from tkinter import font as tkfont
import threading
import queue
from datetime import datetime
from .client import LMStudioClient
from .chat import ChatHistory
from .config import Config, DEFAULT_CONFIG


class SteampunkTheme:
    """Цветовая палитра в стиле стимпанк + викторианская роскошь"""
    
    # Основные цвета
    BRONZE = "#CD7F32"
    COPPER = "#B87333"
    GOLD = "#D4AF37"
    DARK_BRONZE = "#8B4513"
    VICTORIAN_RED = "#8B0000"
    DEEP_BLUE = "#191970"
    CREAM = "#F5F5DC"
    DARK_BG = "#1A1A2E"
    PANEL_BG = "#16213E"
    TEXT_COLOR = "#E8E8E8"
    ACCENT_GREEN = "#00FF7F"
    
    # Градиенты (эмуляция через цвета)
    METAL_LIGHT = "#FFD700"
    METAL_DARK = "#8B4513"


class JarvisGUI(ctk.CTk):
    """Основное окно приложения в стиле Джарвиса"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("🎩 JARVIS KRAMAR - AI Butler Interface")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Цветовая схема
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Очереди для потокобезопасной работы
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Инициализация компонентов
        self.client = None
        self.chat_history = None
        self.is_streaming = False
        self.current_response = ""
        
        # Создание интерфейса
        self._setup_styles()
        self._create_layout()
        self._bind_events()
        
        # Запуск обработки очереди
        self._process_queue()
        
        # Приветственное сообщение
        self._show_welcome()
    
    def _setup_styles(self):
        """Настройка шрифтов и стилей"""
        
        # Кастомные шрифты
        self.title_font = ctk.CTkFont(
            family="Georgia",
            size=24,
            weight="bold"
        )
        
        self.header_font = ctk.CTkFont(
            family="Times New Roman",
            size=16,
            weight="bold"
        )
        
        self.text_font = ctk.CTkFont(
            family="Consolas",
            size=13
        )
        
        self.button_font = ctk.CTkFont(
            family="Arial",
            size=12,
            weight="bold"
        )
        
        # Словарь стилей
        self.styles = {
            "main_frame": {
                "fg_color": SteampunkTheme.DARK_BG
            },
            "sidebar": {
                "fg_color": SteampunkTheme.PANEL_BG,
                "corner_radius": 0
            },
            "chat_display": {
                "fg_color": "#0D1B2A",
                "border_color": SteampunkTheme.BRONZE,
                "border_width": 2
            },
            "input_frame": {
                "fg_color": SteampunkTheme.PANEL_BG
            },
            "button_primary": {
                "fg_color": SteampunkTheme.BRONZE,
                "hover_color": SteampunkTheme.COPPER,
                "text_color": SteampunkTheme.CREAM,
                "font": self.button_font
            },
            "button_secondary": {
                "fg_color": SteampunkTheme.DARK_BRONZE,
                "hover_color": SteampunkTheme.BRONZE,
                "text_color": SteampunkTheme.CREAM,
                "font": self.button_font
            },
            "button_accent": {
                "fg_color": SteampunkTheme.GOLD,
                "hover_color": SteampunkTheme.METAL_LIGHT,
                "text_color": SteampunkTheme.DARK_BG,
                "font": self.button_font
            },
            "entry": {
                "fg_color": "#0D1B2A",
                "border_color": SteampunkTheme.BRONZE,
                "border_width": 1,
                "text_color": SteampunkTheme.TEXT_COLOR,
                "font": self.text_font
            },
            "label_title": {
                "text_color": SteampunkTheme.GOLD,
                "font": self.title_font
            },
            "label_header": {
                "text_color": SteampunkTheme.BRONZE,
                "font": self.header_font
            },
            "label_normal": {
                "text_color": SteampunkTheme.TEXT_COLOR,
                "font": self.text_font
            }
        }
    
    def _create_layout(self):
        """Создание основной компоновки"""
        
        # Главный контейнер
        self.main_frame = ctk.CTkFrame(self, **self.styles["main_frame"])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель
        self._create_header()
        
        # Основная область с боковой панелью
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=10)
        
        # Боковая панель
        self._create_sidebar()
        
        # Область чата
        self._create_chat_area()
        
        # Область ввода
        self._create_input_area()
        
        # Статус бар
        self._create_status_bar()
    
    def _create_header(self):
        """Создание заголовка"""
        
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Логотип/заголовок
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ JARVIS KRAMAR ⚙️",
            **self.styles["label_title"]
        )
        title_label.pack(side="left", padx=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Victorian Steampunk AI Butler System",
            text_color=SteampunkTheme.BRONZE,
            font=ctk.CTkFont(family="Times New Roman", size=12)
        )
        subtitle_label.pack(side="left", padx=10, pady=25)
        
        # Индикатор статуса справа
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="● ONLINE",
            text_color=SteampunkTheme.ACCENT_GREEN,
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold")
        )
        self.status_indicator.pack(side="right", padx=20, pady=20)
    
    def _create_sidebar(self):
        """Создание боковой панели управления"""
        
        sidebar = ctk.CTkFrame(self.content_frame, width=250, **self.styles["sidebar"])
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Заголовок панели
        settings_label = ctk.CTkLabel(
            sidebar,
            text="━ CONTROL PANEL ━",
            **self.styles["label_header"]
        )
        settings_label.pack(pady=15)
        
        # Выбор языка
        lang_label = ctk.CTkLabel(
            sidebar,
            text="Language / Язык:",
            **self.styles["label_normal"]
        )
        lang_label.pack(pady=(15, 5), padx=10, anchor="w")
        
        self.lang_var = ctk.StringVar(value="auto")
        self.lang_menu = ctk.CTkOptionMenu(
            sidebar,
            variable=self.lang_var,
            values=["auto", "en", "ru", "fr", "de", "es"],
            command=self._on_language_change,
            fg_color=SteampunkTheme.DARK_BRONZE,
            button_color=SteampunkTheme.BRONZE,
            button_hover_color=SteampunkTheme.COPPER,
            dropdown_fg_color=SteampunkTheme.PANEL_BG,
            dropdown_hover_color=SteampunkTheme.BRONZE,
            font=self.button_font
        )
        self.lang_menu.pack(pady=5, padx=10, fill="x")
        
        # Размер ответа
        tokens_label = ctk.CTkLabel(
            sidebar,
            text="Max Tokens:",
            **self.styles["label_normal"]
        )
        tokens_label.pack(pady=(15, 5), padx=10, anchor="w")
        
        self.tokens_var = ctk.StringVar(value="2048")
        self.tokens_menu = ctk.CTkOptionMenu(
            sidebar,
            variable=self.tokens_var,
            values=["512", "1024", "2048", "4096", "8192"],
            fg_color=SteampunkTheme.DARK_BRONZE,
            button_color=SteampunkTheme.BRONZE,
            button_hover_color=SteampunkTheme.COPPER,
            dropdown_fg_color=SteampunkTheme.PANEL_BG,
            dropdown_hover_color=SteampunkTheme.BRONZE,
            font=self.button_font
        )
        self.tokens_menu.pack(pady=5, padx=10, fill="x")
        
        # Температура
        temp_label = ctk.CTkLabel(
            sidebar,
            text="Creativity (Temperature):",
            **self.styles["label_normal"]
        )
        temp_label.pack(pady=(15, 5), padx=10, anchor="w")
        
        self.temp_slider = ctk.CTkSlider(
            sidebar,
            from_=0.0,
            to=1.5,
            number_of_steps=15,
            command=self._on_temp_change,
            button_color=SteampunkTheme.GOLD,
            progress_color=SteampunkTheme.BRONZE
        )
        self.temp_slider.set(0.7)
        self.temp_slider.pack(pady=5, padx=10, fill="x")
        
        self.temp_value_label = ctk.CTkLabel(
            sidebar,
            text="0.70",
            text_color=SteampunkTheme.GOLD,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.temp_value_label.pack(pady=(0, 15))
        
        # Разделитель
        separator = ctk.CTkLabel(
            sidebar,
            text="━━━━━━━━━━━━━━",
            text_color=SteampunkTheme.DARK_BRONZE
        )
        separator.pack(pady=10)
        
        # Кнопки управления
        self.clear_btn = ctk.CTkButton(
            sidebar,
            text="🗑 Clear Chat",
            command=self._clear_chat,
            **self.styles["button_secondary"]
        )
        self.clear_btn.pack(pady=5, padx=10, fill="x")
        
        self.export_btn = ctk.CTkButton(
            sidebar,
            text="💾 Export Chat",
            command=self._export_chat,
            **self.styles["button_secondary"]
        )
        self.export_btn.pack(pady=5, padx=10, fill="x")
        
        self.settings_btn = ctk.CTkButton(
            sidebar,
            text="⚙ Settings",
            command=self._open_settings,
            **self.styles["button_primary"]
        )
        self.settings_btn.pack(pady=5, padx=10, fill="x")
        
        # Информация о подключении
        conn_label = ctk.CTkLabel(
            sidebar,
            text="Connection:",
            **self.styles["label_normal"]
        )
        conn_label.pack(pady=(20, 5), padx=10, anchor="w")
        
        self.conn_status = ctk.CTkLabel(
            sidebar,
            text="● Disconnected",
            text_color="#FF4444",
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.conn_status.pack(padx=10, anchor="w")
    
    def _create_chat_area(self):
        """Создание области чата"""
        
        chat_frame = ctk.CTkFrame(self.content_frame, **self.styles["chat_display"])
        chat_frame.pack(side="left", fill="both", expand=True)
        
        # Заголовок области чата
        chat_header = ctk.CTkLabel(
            chat_frame,
            text="✦ Conversation Log ✦",
            **self.styles["label_header"]
        )
        chat_header.pack(pady=10)
        
        # Текстовое поле для чата
        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            wrap="word",
            font=self.text_font,
            text_color=SteampunkTheme.TEXT_COLOR,
            cursor_color=SteampunkTheme.GOLD,
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Настройка тегов для форматирования
        self.chat_display.tag_config("user", foreground=SteampunkTheme.BRONZE, justify="right")
        self.chat_display.tag_config("assistant", foreground=SteampunkTheme.ACCENT_GREEN, justify="left")
        self.chat_display.tag_config("system", foreground=SteampunkTheme.GOLD, justify="center")
        self.chat_display.tag_config("timestamp", foreground="#666666", justify="right")
    
    def _create_input_area(self):
        """Создание области ввода"""
        
        input_frame = ctk.CTkFrame(self.main_frame, **self.styles["input_frame"])
        input_frame.pack(fill="x", pady=(10, 0))
        
        # Поле ввода
        self.input_entry = ctk.CTkTextbox(
            input_frame,
            height=80,
            wrap="word",
            **self.styles["entry"]
        )
        self.input_entry.pack(fill="x", padx=10, pady=10)
        
        # Кнопки
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.send_btn = ctk.CTkButton(
            button_frame,
            text="⚡ SEND MESSAGE",
            command=self._send_message,
            **self.styles["button_accent"]
        )
        self.send_btn.pack(side="right", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹ STOP",
            command=self._stop_generation,
            state="disabled",
            fg_color="#FF4444",
            hover_color="#CC0000",
            text_color="white",
            font=self.button_font
        )
        self.stop_btn.pack(side="right", padx=5)
        
        # Подсказка
        hint_label = ctk.CTkLabel(
            button_frame,
            text="Press Ctrl+Enter to send | Shift+Enter for new line",
            text_color="#666666",
            font=ctk.CTkFont(size=10)
        )
        hint_label.pack(side="left", padx=5, pady=5)
    
    def _create_status_bar(self):
        """Создание строки состояния"""
        
        status_frame = ctk.CTkFrame(self.main_frame, height=30, fg_color=SteampunkTheme.PANEL_BG)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready | Language: Auto | Model: Connected",
            text_color=SteampunkTheme.TEXT_COLOR,
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.token_count_label = ctk.CTkLabel(
            status_frame,
            text="Tokens: 0",
            text_color=SteampunkTheme.BRONZE,
            font=ctk.CTkFont(size=11)
        )
        self.token_count_label.pack(side="right", padx=10, pady=5)
    
    def _bind_events(self):
        """Привязка событий"""
        
        # Ctrl+Enter для отправки
        self.input_entry.bind("<Control-Return>", lambda e: self._send_message())
        self.input_entry.bind("<Control-KP_Enter>", lambda e: self._send_message())
        
        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _show_welcome(self):
        """Показ приветственного сообщения"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        welcome_messages = [
            f"[{timestamp}] System initialized\n",
            f"[{timestamp}] JARVIS KRAMAR at your service\n",
            f"[{timestamp}] Victorian protocols engaged\n",
            f"[{timestamp}] Steampunk aesthetics: ACTIVE\n",
            f"[{timestamp}] Awaiting your command, Sir/Madam\n",
            "\n" + "─" * 50 + "\n\n"
        ]
        
        self.chat_display.configure(state="normal")
        for msg in welcome_messages:
            self.chat_display.insert("end", msg)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def _connect_to_lmstudio(self):
        """Подключение к LM Studio"""
        
        try:
            self.client = LMStudioClient(
                base_url=DEFAULT_CONFIG["base_url"],
                model=DEFAULT_CONFIG["model"],
                language=self.lang_var.get(),
                max_tokens=int(self.tokens_var.get()),
                temperature=self.temp_slider.get()
            )
            
            self.chat_history = ChatHistory(language=self.lang_var.get())
            
            self.conn_status.configure(text="● Connected", text_color=SteampunkTheme.ACCENT_GREEN)
            self.status_label.configure(text=f"Connected to {DEFAULT_CONFIG['base_url']}")
            
            return True
            
        except Exception as e:
            self.conn_status.configure(text="● Connection Failed", text_color="#FF4444")
            self.status_label.configure(text=f"Error: {str(e)}")
            return False
    
    def _send_message(self):
        """Отправка сообщения"""
        
        if self.is_streaming:
            return
        
        # Получение текста
        user_message = self.input_entry.get("1.0", "end-1c").strip()
        
        if not user_message:
            return
        
        # Проверка подключения
        if not self.client:
            if not self._connect_to_lmstudio():
                self._add_system_message("Error: Cannot connect to LM Studio. Please ensure it's running.")
                return
        
        # Очистка поля ввода
        self.input_entry.delete("1.0", "end")
        
        # Добавление сообщения пользователя
        self._add_user_message(user_message)
        
        # Блокировка интерфейса
        self.is_streaming = True
        self.send_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Generating response...")
        
        # Запуск генерации в отдельном потоке
        thread = threading.Thread(target=self._generate_response, args=(user_message,), daemon=True)
        thread.start()
    
    def _generate_response(self, user_message):
        """Генерация ответа в отдельном потоке"""
        
        try:
            self.current_response = ""
            
            # Отправка в клиент
            for chunk in self.client.chat_stream(user_message, self.chat_history):
                if not self.is_streaming:  # Проверка на остановку
                    break
                
                self.current_response += chunk
                self.response_queue.put(chunk)
            
            # Добавление в историю
            if self.current_response:
                self.chat_history.add_message("assistant", self.current_response)
            
            self.response_queue.put(None)  # Сигнал окончания
            
        except Exception as e:
            self.response_queue.put(f"\n[Error: {str(e)}]")
            self.response_queue.put(None)
    
    def _process_queue(self):
        """Обработка очереди ответов"""
        
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message == "STOP_STREAMING":
                    self._stop_streaming_ui()
                elif message == "ENABLE_SEND":
                    self.send_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                break
        except queue.Empty:
            pass
        
        try:
            while True:
                chunk = self.response_queue.get_nowait()
                
                if chunk is None:
                    self._stop_streaming_ui()
                    break
                else:
                    self._append_to_chat(chunk, "assistant")
                    
        except queue.Empty:
            pass
        
        # Планирование следующей проверки
        self.after(50, self._process_queue)
    
    def _append_to_chat(self, text, sender):
        """Добавление текста в чат"""
        
        self.chat_display.configure(state="normal")
        
        if sender == "assistant":
            self.chat_display.insert("end", text, "assistant")
        elif sender == "user":
            self.chat_display.insert("end", text, "user")
        elif sender == "system":
            self.chat_display.insert("end", text, "system")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def _add_user_message(self, message):
        """Добавление сообщения пользователя"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n[{timestamp}] You: ", "timestamp")
        self.chat_display.insert("end", f"{message}\n", "user")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
        # Добавление в историю
        if self.chat_history:
            self.chat_history.add_message("user", message)
    
    def _add_system_message(self, message):
        """Добавление системного сообщения"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n[{timestamp}] System: {message}\n", "system")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def _stop_generation(self):
        """Остановка генерации"""
        
        self.is_streaming = False
        self.message_queue.put("STOP_STREAMING")
    
    def _stop_streaming_ui(self):
        """Обновление UI после остановки"""
        
        self.is_streaming = False
        self.send_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Ready")
        
        if self.current_response and self.chat_history:
            # Убедиться, что последнее сообщение добавлено в историю
            last_msg = self.chat_history.messages[-1]
            if last_msg["role"] == "assistant" and not last_msg["content"]:
                last_msg["content"] = self.current_response
    
    def _clear_chat(self):
        """Очистка чата"""
        
        if self.chat_history:
            self.chat_history.clear()
        
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        
        self._show_welcome()
        self.status_label.configure(text="Chat cleared")
    
    def _export_chat(self):
        """Экспорт чата"""
        
        if not self.chat_history or not self.chat_history.messages:
            self._add_system_message("No messages to export.")
            return
        
        # Простая реализация - вывод в консоль
        # В полной версии можно сохранить в файл
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")],
            title="Export Chat History"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.chat_history.messages, f, ensure_ascii=False, indent=2)
                self._add_system_message(f"Chat exported to {file_path}")
            except Exception as e:
                self._add_system_message(f"Export failed: {str(e)}")
    
    def _open_settings(self):
        """Открытие настроек"""
        
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # Заголовок
        title = ctk.CTkLabel(
            settings_window,
            text="⚙ Configuration",
            font=self.title_font,
            text_color=SteampunkTheme.GOLD
        )
        title.pack(pady=20)
        
        # URL LM Studio
        url_label = ctk.CTkLabel(
            settings_window,
            text="LM Studio URL:",
            font=self.header_font
        )
        url_label.pack(pady=(10, 5))
        
        url_entry = ctk.CTkEntry(
            settings_window,
            width=400,
            placeholder_text="http://localhost:1234/v1"
        )
        url_entry.insert(0, DEFAULT_CONFIG["base_url"])
        url_entry.pack(pady=5)
        
        # Модель
        model_label = ctk.CTkLabel(
            settings_window,
            text="Model Name:",
            font=self.header_font
        )
        model_label.pack(pady=(10, 5))
        
        model_entry = ctk.CTkEntry(
            settings_window,
            width=400,
            placeholder_text="local-model"
        )
        model_entry.insert(0, DEFAULT_CONFIG["model"])
        model_entry.pack(pady=5)
        
        # Кнопки
        btn_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save & Reconnect",
            command=lambda: self._save_settings(url_entry.get(), model_entry.get(), settings_window),
            **self.styles["button_accent"]
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=settings_window.destroy,
            **self.styles["button_secondary"]
        )
        cancel_btn.pack(side="left", padx=10)
    
    def _save_settings(self, url, model, window):
        """Сохранение настроек"""
        
        # Обновление конфига
        global DEFAULT_CONFIG
        DEFAULT_CONFIG["base_url"] = url
        DEFAULT_CONFIG["model"] = model
        
        # Переподключение
        self.client = None
        self.chat_history = None
        self._connect_to_lmstudio()
        
        window.destroy()
        self._add_system_message("Settings updated. Reconnected to LM Studio.")
    
    def _on_language_change(self, new_lang):
        """Обработка смены языка"""
        
        if self.chat_history:
            self.chat_history.set_language(new_lang)
        
        if self.client:
            self.client.set_language(new_lang)
        
        self.status_label.configure(text=f"Language changed to: {new_lang.upper()}")
    
    def _on_temp_change(self, value):
        """Обработка изменения температуры"""
        
        self.temp_value_label.configure(text=f"{value:.2f}")
        
        if self.client:
            self.client.temperature = value
    
    def _on_closing(self):
        """Обработка закрытия окна"""
        
        self.is_streaming = False
        self.destroy()


def run_gui():
    """Запуск GUI приложения"""
    
    app = JarvisGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
