import os
import shutil
import subprocess
import yt_dlp
import re
import logging
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
import threading
import pyperclip
import time
import json
import os.path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="download.log", filemode="a")

# Константы для настроек UI
WINDOW_SIZE = "600x650"
MIN_WINDOW_SIZE = (500, 600)
PADDING = 15
BUTTON_PADDING = (15, 8)
MAIN_FONT = ('Helvetica', 10)
HEADER_FONT = ('Helvetica', 16, 'bold')
LABEL_FONT = ('Helvetica', 11, 'bold')
STATUS_FONT = ('Helvetica', 9, 'italic')

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "download_mode": "video",
    "last_resolution": "720p",
    "cookies_from_browser": "chrome"
}

# В начале файла добавляем глобальную переменную для настроек
settings = None

class YouTubeDownloader:
    def __init__(self):
        global settings
        settings = load_settings()
        self.settings = settings
        self.setup_ui()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)
        
        # Добавляем иконку
        try:
            if os.path.exists('ytdl.ico'):
                self.root.iconbitmap('ytdl.ico')
            else:
                logging.warning("Файл иконки ytdl.ico не найден")
        except Exception as e:
            logging.error(f"Ошибка при установке иконки: {e}")
        
        self.setup_styles()
        self.main_frame = self.create_main_frame()
        self.create_header()
        self.create_url_section()
        self.create_settings_section()
        self.create_progress_section()
        self.create_download_button()
        self.create_status_label()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TFrame", padding=PADDING)
        style.configure("TButton", padding=BUTTON_PADDING, font=MAIN_FONT)
        style.configure("TLabel", font=MAIN_FONT)
        style.configure("Header.TLabel", font=HEADER_FONT)
        style.configure("Status.TLabel", font=STATUS_FONT)
        style.configure("TLabelframe", padding=PADDING)
        style.configure("TLabelframe.Label", font=LABEL_FONT)
        style.configure("TRadiobutton", padding=5)
        style.configure("TProgressbar", thickness=15)

    def create_main_frame(self):
        main_frame = ttk.Frame(self.root, padding=25)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        return main_frame

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        ttk.Label(
            header_frame,
            text="YouTube Downloader",
            style="Header.TLabel"
        ).grid(row=0, column=0, columnspan=3)
        
        ttk.Label(
            header_frame,
            text="Скачивайте видео и аудио с YouTube",
            foreground="gray"
        ).grid(row=1, column=0, columnspan=3, pady=(5, 0))

    def create_url_section(self):
        self.url_frame = ttk.LabelFrame(self.main_frame, text="URL видео", padding=PADDING)
        self.url_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        self.url_entry = ttk.Entry(self.url_frame, width=52, font=MAIN_FONT)
        self.url_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(
            self.url_frame,
            text="Вставить URL",
            command=lambda: self.paste_url(),
            width=15
        ).grid(row=0, column=1, padx=5)

    def create_settings_section(self):
        self.settings_frame = ttk.LabelFrame(
            self.main_frame,
            text="Настройки загрузки",
            padding=PADDING
        )
        self.settings_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        self.create_mode_selection()
        self.create_resolution_selection()

    def create_mode_selection(self):
        mode_frame = ttk.Frame(self.settings_frame)
        mode_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        self.download_mode = StringVar(value=self.settings.get('download_mode', 'video'))
        
        ttk.Radiobutton(
            mode_frame,
            text="Видео",
            variable=self.download_mode,
            value="video",
            style="TRadiobutton"
        ).grid(row=0, column=0, padx=20)
        
        ttk.Radiobutton(
            mode_frame,
            text="Только аудио",
            variable=self.download_mode,
            value="audio",
            style="TRadiobutton"
        ).grid(row=0, column=1, padx=20)
        
        self.download_mode.trace('w', self.toggle_resolution_widgets)

    def create_resolution_selection(self):
        self.resolution_label = ttk.Label(self.settings_frame, text="Разрешение:")
        self.resolution_combobox = ttk.Combobox(
            self.settings_frame,
            width=15,
            font=MAIN_FONT,
            state="readonly"
        )
        self.refresh_button = ttk.Button(
            self.settings_frame,
            text="Обновить список",
            command=self.update_resolutions
        )
        
        self.toggle_resolution_widgets()
        self.resolution_combobox.bind("<Button-1>", lambda e: self.update_resolutions())

    def create_progress_section(self):
        self.progress_frame = ttk.LabelFrame(
            self.main_frame,
            text="Прогресс загрузки",
            padding=PADDING
        )
        self.progress_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        self.setup_progress_bars()

    def setup_progress_bars(self):
        # Видео прогресс
        self.video_progress_label = ttk.Label(
            self.progress_frame,
            text="Ожидание...",
            style="Status.TLabel"
        )
        self.video_progress_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        self.video_progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.video_progress_bar.grid(row=1, column=0, columnspan=3, pady=(0, 10), padx=10)
        
        # Аудио прогресс
        self.audio_progress_label = ttk.Label(
            self.progress_frame,
            text="",
            style="Status.TLabel"
        )
        self.audio_progress_label.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        self.audio_progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.audio_progress_bar.grid(row=3, column=0, columnspan=3, padx=10)

    def create_download_button(self):
        self.download_button = ttk.Button(
            self.main_frame,
            text="Скачать",
            command=self.start_download,
            width=25
        )
        self.download_button.grid(row=4, column=0, columnspan=3, pady=20)

    def create_status_label(self):
        self.status_label = ttk.Label(
            self.main_frame,
            text="Готов к загрузке",
            style="Status.TLabel",
            foreground="gray"
        )
        self.status_label.grid(row=5, column=0, columnspan=3)

    # Методы для работы с UI
    def paste_url(self):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, pyperclip.paste())

    def toggle_resolution_widgets(self, *args):
        if self.download_mode.get() == "video":
            self.resolution_label.grid(row=1, column=0, padx=5, pady=5)
            self.resolution_combobox.grid(row=1, column=1, padx=5, pady=5)
            self.refresh_button.grid(row=1, column=2, padx=5)
        else:
            self.resolution_label.grid_remove()
            self.resolution_combobox.grid_remove()
            self.refresh_button.grid_remove()
        
        self.settings['download_mode'] = self.download_mode.get()
        save_settings(self.settings)

    def update_resolutions(self):
        url = self.url_entry.get()
        if url:
            resolutions = get_available_resolutions(url, self.settings)
            self.resolution_combobox["values"] = resolutions
            if resolutions:
                self.resolution_combobox.set(resolutions[0])

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL видео!")
            return

        self.download_button.config(state=tk.DISABLED)
        self.reset_progress_bars()

        thread = threading.Thread(
            target=self.download_content,
            args=(url,)
        )
        thread.start()

    def reset_progress_bars(self):
        self.video_progress_label.config(text="Начало загрузки...")
        self.audio_progress_label.config(text="")
        self.video_progress_bar["value"] = 0
        self.audio_progress_bar["value"] = 0

    def download_content(self, url):
        try:
            if self.download_mode.get() == "audio":
                download_audio(url, self.video_progress_label, self.video_progress_bar, self.settings)
            else:
                resolution = self.resolution_combobox.get()
                download_video(
                    url, resolution,
                    self.video_progress_label, self.video_progress_bar,
                    self.audio_progress_label, self.audio_progress_bar,
                    self.settings
                )
        finally:
            self.download_button.config(state=tk.NORMAL)

    def run(self):
        check_ffmpeg()
        self.root.mainloop()

# Вспомогательные функции
def load_settings():
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
    except Exception as e:
        logging.error(f"Ошибка загрузки настроек: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        logging.error(f"Ошибка сохранения настроек: {e}")

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        logging.error("ffmpeg.exe не установлен.")
        messagebox.showerror("Ошибка", "ffmpeg не установлен. Установите ffmpeg и повторите попытку.")
        exit(1)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

# Функции для работы с YouTube
def get_available_resolutions(url, settings):
    try:
        browser = settings.get('cookies_from_browser', 'chrome')
        logging.info(f"Используется браузер: {browser}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'cookies_from_browser': browser,
            'socket_timeout': 30,
            'retries': 10,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                resolutions = set()
                
                for f in formats:
                    if f.get('height') and f.get('vcodec') != 'none':
                        resolutions.add(f'{f["height"]}p')
                
                if not resolutions:
                    logging.warning("Не найдены доступные разрешения")
                    return ['720p']
                
                sorted_resolutions = sorted(list(resolutions), key=lambda x: int(x.replace('p', '')), reverse=True)
                logging.info(f"Найдены разрешения: {sorted_resolutions}")
                return sorted_resolutions
        except yt_dlp.utils.DownloadError as e:
            if "Sign in to confirm you're not a bot" in str(e):
                logging.error(f"Ошибка авторизации в браузере {browser}. Убедитесь, что вы вошли в YouTube.")
                messagebox.showerror("Ошибка авторизации", 
                    f"Не удалось получить доступ к YouTube через браузер {browser}.\n\n"
                    "Убедитесь, что:\n"
                    "1. Вы вошли в свой аккаунт YouTube в этом браузере\n"
                    "2. Браузер не в режиме инкогнито\n"
                    "3. Браузер установлен в стандартном расположении\n"
                    "4. У вас есть права на чтение профиля браузера")
            raise
    except Exception as e:
        logging.error(f"Ошибка при получении разрешений: {e}")
        logging.exception(e)
        return ['720p']

def download_video(url, resolution, video_progress_label, video_progress_bar, 
                  audio_progress_label, audio_progress_bar, settings):
    try:
        logging.info(f"Начало загрузки по URL: {url}")
        resolution_number = resolution.replace('p', '')
        current_download = {'type': 'video'}
        
        # Сначала получаем информацию о видео
        with yt_dlp.YoutubeDL({
            'quiet': True, 
            'cookies_from_browser': settings.get('cookies_from_browser', 'chrome')
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            output_filename = f"{sanitize_filename(video_title)}_{resolution}.mp4"
            
            if os.path.exists(output_filename):
                if not messagebox.askyesno("Файл существует", 
                    f"Файл {output_filename} уже существует.\nХотите перезаписать его?"):
                    logging.info("Загрузка отменена пользователем - файл уже существует")
                    video_progress_label.config(text="Загрузка отменена")
                    return
                try:
                    os.remove(output_filename)
                    logging.info(f"Удален существующий файл: {output_filename}")
                except Exception as e:
                    logging.error(f"Ошибка при удалении существующего файла: {e}")
                    raise

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    percent = (downloaded_bytes / total_bytes) * 100
                    if current_download['type'] == 'video':
                        video_progress_label.config(text=f"Загрузка видео: {percent:.1f}%")
                        video_progress_bar["value"] = percent
                        video_progress_bar.update()
                    else:
                        audio_progress_label.config(text=f"Загрузка аудио: {percent:.1f}%")
                        audio_progress_bar["value"] = percent
                        audio_progress_bar.update()
            elif d['status'] == 'finished':
                if current_download['type'] == 'video':
                    video_progress_label.config(text="Видео загружено")
                    video_progress_bar["value"] = 100
                    current_download['type'] = 'audio'
                else:
                    audio_progress_label.config(text="Аудио загружено")
                    audio_progress_bar["value"] = 100

        ydl_opts = {
            'format': f'bestvideo[height<={resolution_number}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [progress_hook],
            'outtmpl': output_filename,
            'merge_output_format': 'mp4',
            'postprocessor_hooks': [progress_hook],
            'updatetime': False,
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'retry_sleep': 3,
        }
        
        # Сбрасываем прогресс-бары
        video_progress_label.config(text="Подготовка к загрузке...")
        audio_progress_label.config(text="")
        video_progress_bar["value"] = 0
        audio_progress_bar["value"] = 0

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            # Устанавливаем текущее время для файла
            if os.path.exists(output_filename):
                current_time = time.time()
                os.utime(output_filename, (current_time, current_time))
            
            # Финальное обновление статуса
            video_progress_label.config(text="Загрузка завершена")
            audio_progress_label.config(text="")
            video_progress_bar["value"] = 100
            audio_progress_bar["value"] = 100
            
            logging.info(f"Скачивание завершено. Файл сохранен как {output_filename}")
            messagebox.showinfo("Успех", f"Скачивание завершено. Файл сохранен как {output_filename}")
            
    except Exception as e:
        logging.error(f"Ошибка при загрузке: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        video_progress_label.config(text="Произошла ошибка")
        audio_progress_label.config(text="")

def download_audio(url, video_progress_label, video_progress_bar, settings):
    try:
        with yt_dlp.YoutubeDL({
            'quiet': True, 
            'cookies_from_browser': settings.get('cookies_from_browser', 'chrome')
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'audio')
            output_filename = f"{sanitize_filename(video_title)}_audio.mp3"
            
            if os.path.exists(output_filename):
                if not messagebox.askyesno("Файл существует", 
                    f"Файл {output_filename} уже существует.\nХотите перезаписать его?"):
                    video_progress_label.config(text="Загрузка отменена")
                    return

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    percent = (downloaded_bytes / total_bytes) * 100
                    video_progress_label.config(text=f"Загрузка аудио: {percent:.1f}%")
                    video_progress_bar["value"] = percent
                    video_progress_bar.update()
            elif d['status'] == 'finished':
                video_progress_label.config(text="Конвертация в MP3...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'progress_hooks': [progress_hook],
            'outtmpl': output_filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'updatetime': False,
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'retry_sleep': 3,
        }

        video_progress_label.config(text="Подготовка к загрузке...")
        video_progress_bar["value"] = 0

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            if os.path.exists(output_filename):
                current_time = time.time()
                os.utime(output_filename, (current_time, current_time))
            
            video_progress_label.config(text="Загрузка завершена")
            video_progress_bar["value"] = 100
            logging.info(f"Скачивание аудио завершено. Файл сохранен как {output_filename}")
            messagebox.showinfo("Успех", f"Скачивание завершено. Файл сохранен как {output_filename}")
            
    except Exception as e:
        logging.error(f"Ошибка при загрузке аудио: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        video_progress_label.config(text="Произошла ошибка")

def main():
    app = YouTubeDownloader()
    app.run()

if __name__ == "__main__":
    main() 