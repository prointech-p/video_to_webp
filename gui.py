import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

from mp4_to_webp import super_optimized_chromakey_simple


class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to WebP Converter")
        self.root.geometry("1000x850")
        # self.root.configure(bg='#f0f0f0')
        
        # Загрузка настроек
        self.settings_file = "converter_settings.json"
        self.settings = self.load_settings()
        
        # Стили
        self.setup_styles()
        
        # Переменные
        self.setup_variables()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Центрирование окна
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('alt')
        
        # Настройка цветов - светлая приятная тема
        bg_color = "#f5d498"
        fg_color = '#333333'
        accent_color = '#4a6fa5'
        section_bg = '#f0f0f0'
        entry_bg = '#f0f0f0'
        
        # self.root.configure(bg=accent_color)
        
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        self.style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground=accent_color)
        self.style.configure('Section.TLabel', font=('Segoe UI', 13, 'bold'), foreground=accent_color)
        self.style.configure('Section.TFrame')
        
        self.style.configure('TCheckbutton')
        self.style.configure('TLabelframe', relief='flat', borderwidth=0)
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground=accent_color)
        
        # Стиль для полей ввода
        # self.style.configure('TEntry', fieldbackground=entry_bg)
        # self.style.configure('TSpinbox', fieldbackground=entry_bg)

        # self.root.configure(bg=bg_color)
        
        # self.style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        # self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        # self.style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground=accent_color)
        # self.style.configure('Section.TLabel', font=('Segoe UI', 13, 'bold'), foreground=accent_color)
        # self.style.configure('Section.TFrame', background=section_bg)
        
        # self.style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
        # self.style.configure('TLabelframe', background=bg_color, relief='flat', borderwidth=0)
        # self.style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color, font=('Segoe UI', 11, 'bold'))
        
        # # Стиль для полей ввода
        # self.style.configure('TEntry', fieldbackground=entry_bg)
        # self.style.configure('TSpinbox', fieldbackground=entry_bg)
        
    def setup_variables(self):
        # Основные параметры
        self.input_path = tk.StringVar(value=self.settings.get('input_path', ''))
        self.output_path = tk.StringVar(value=self.settings.get('output_path', ''))
        self.scale = tk.IntVar(value=self.settings.get('scale', 70))
        self.target_fps = tk.IntVar(value=self.settings.get('target_fps', 10))
        self.quality = tk.IntVar(value=self.settings.get('quality', 85))
        
        # Параметры резкости
        self.sharpen = tk.BooleanVar(value=self.settings.get('sharpen', True))
        self.sharpen_amount = tk.DoubleVar(value=self.settings.get('sharpen_amount', 0.5))
        
        # Параметры обрезки
        self.crop_top = tk.IntVar(value=self.settings.get('crop_top', 0))
        self.crop_bottom = tk.IntVar(value=self.settings.get('crop_bottom', 0))
        self.crop_left = tk.IntVar(value=self.settings.get('crop_left', 0))
        self.crop_right = tk.IntVar(value=self.settings.get('crop_right', 0))
        
        # Переменные для отображения значений
        self.scale_label = tk.StringVar(value=f"{self.scale.get()}%")
        self.fps_label = tk.StringVar(value=f"{self.target_fps.get()}")
        self.quality_label = tk.StringVar(value=f"{self.quality.get()}%")
        self.sharpen_label = tk.StringVar(value=f"{self.sharpen_amount.get():.1f}")
        
    def create_widgets(self):
        # Главный контейнер с прокруткой
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🎬 Video to WebP Converter", style='Title.TLabel')
        title_label.pack()
        
        # Создаем Notebook для лучшей организации
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True, pady=10)
        
        # Вкладка "Основные настройки"
        basic_tab = ttk.Frame(notebook)
        notebook.add(basic_tab, text='Основные настройки')
        self.create_basic_tab(basic_tab)
        
        # Вкладка "Дополнительные настройки"
        advanced_tab = ttk.Frame(notebook)
        notebook.add(advanced_tab, text='Дополнительные настройки')
        self.create_advanced_tab(advanced_tab)
        
        # Панель управления внизу
        self.create_control_panel(main_container)
        
    def create_basic_tab(self, parent):
        # Секция файлов
        file_section = ttk.LabelFrame(parent, text="📁 Файлы", padding=15)
        file_section.pack(fill='x', pady=(0, 20), padx=5)
        
        # Входной файл
        input_frame = ttk.Frame(file_section)
        input_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(input_frame, text="Входной файл (MP4):", width=20).pack(side='left', padx=(0, 10))
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=60)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(input_frame, text="Обзор...", command=self.browse_input, 
                  width=12).pack(side='left')
        
        # Выходной файл
        output_frame = ttk.Frame(file_section)
        output_frame.pack(fill='x')
        
        ttk.Label(output_frame, text="Выходной файл (WebP):", width=20).pack(side='left', padx=(0, 10))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=60)
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="Обзор...", command=self.browse_output, 
                  width=12).pack(side='left')
        
        # Секция основных параметров
        params_section = ttk.LabelFrame(parent, text="⚙️ Основные параметры", padding=15)
        params_section.pack(fill='x', pady=(0, 20), padx=5)
        
        # Масштаб
        scale_frame = ttk.Frame(params_section)
        scale_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(scale_frame, text="Масштаб:", width=15).pack(side='left')
        scale_slider = ttk.Scale(scale_frame, from_=10, to=100, variable=self.scale, 
                                command=self.on_scale_change)
        scale_slider.pack(side='left', fill='x', expand=True, padx=10)
        self.scale_display = ttk.Label(scale_frame, textvariable=self.scale_label, 
                                      width=8, font=('Segoe UI', 10, 'bold'), 
                                      foreground='#4a6fa5')
        self.scale_display.pack(side='left')
        
        # FPS
        fps_frame = ttk.Frame(params_section)
        fps_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(fps_frame, text="Целевой FPS:", width=15).pack(side='left')
        fps_slider = ttk.Scale(fps_frame, from_=1, to=60, variable=self.target_fps, 
                              command=self.on_fps_change)
        fps_slider.pack(side='left', fill='x', expand=True, padx=10)
        self.fps_display = ttk.Label(fps_frame, textvariable=self.fps_label, 
                                    width=8, font=('Segoe UI', 10, 'bold'), 
                                    foreground='#4a6fa5')
        self.fps_display.pack(side='left')
        
        # Качество
        quality_frame = ttk.Frame(params_section)
        quality_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(quality_frame, text="Качество:", width=15).pack(side='left')
        quality_slider = ttk.Scale(quality_frame, from_=1, to=100, variable=self.quality, 
                                  command=self.on_quality_change)
        quality_slider.pack(side='left', fill='x', expand=True, padx=10)
        self.quality_display = ttk.Label(quality_frame, textvariable=self.quality_label, 
                                        width=8, font=('Segoe UI', 10, 'bold'), 
                                        foreground='#4a6fa5')
        self.quality_display.pack(side='left')

        # Секция увеличения резкости
        sharpen_section = ttk.LabelFrame(parent, text="🔍 Увеличение резкости", padding=15)
        sharpen_section.pack(fill='x', pady=(0, 20), padx=5)
        
        # Чекбокс увеличения резкости
        check_frame = ttk.Frame(sharpen_section)
        check_frame.pack(fill='x', pady=(0, 15))
        
        self.sharpen_check = ttk.Checkbutton(check_frame, text="Применить увеличение резкости", 
                                           variable=self.sharpen, command=self.on_sharpen_change)
        self.sharpen_check.pack(side='left')
        
        # Сила увеличения резкости
        sharpen_amount_frame = ttk.Frame(sharpen_section)
        sharpen_amount_frame.pack(fill='x')
        
        ttk.Label(sharpen_amount_frame, text="Сила резкости:", width=15).pack(side='left')
        sharpen_slider = ttk.Scale(sharpen_amount_frame, from_=0.1, to=2.0, 
                                  variable=self.sharpen_amount, command=self.on_sharpen_amount_change)
        sharpen_slider.pack(side='left', fill='x', expand=True, padx=10)
        self.sharpen_display = ttk.Label(sharpen_amount_frame, textvariable=self.sharpen_label, 
                                        width=8, font=('Segoe UI', 10, 'bold'), 
                                        foreground='#4a6fa5')
        self.sharpen_display.pack(side='left')
        
    def create_advanced_tab(self, parent):
        
        # Секция обрезки
        crop_section = ttk.LabelFrame(parent, text="✂️ Обрезка видео", padding=15)
        crop_section.pack(fill='x', padx=5)
        
        # Сетка для полей обрезки
        crop_grid = ttk.Frame(crop_section)
        crop_grid.pack(fill='x')
        
        crop_labels = ['Сверху:', 'Снизу:', 'Слева:', 'Справа:']
        crop_vars = [self.crop_top, self.crop_bottom, self.crop_left, self.crop_right]
        
        for i, (label, var) in enumerate(zip(crop_labels, crop_vars)):
            frame = ttk.Frame(crop_grid)
            frame.grid(row=i, column=0, sticky='ew', pady=5, padx=5)
            
            ttk.Label(frame, text=label, width=10).pack(side='left')
            spinbox = ttk.Spinbox(frame, from_=0, to=1000, textvariable=var, 
                                 width=12, command=self.on_crop_change)
            spinbox.pack(side='left', padx=(5, 2))
            ttk.Label(frame, text="px").pack(side='left')
        
    def create_control_panel(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=(20, 0))
        
        # Кнопки управления
        button_style = {'style': 'TButton', 'padding': (15, 10)}
        
        # Первый ряд кнопок
        row1 = ttk.Frame(control_frame)
        row1.pack(fill='x', pady=(0, 10))
        
        self.convert_btn = ttk.Button(row1, text="🎬 Начать конвертацию", 
                                     command=self.convert_video, **button_style)
        self.convert_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        self.save_btn = ttk.Button(row1, text="💾 Сохранить настройки", 
                                  command=self.save_settings, **button_style)
        self.save_btn.pack(side='left', expand=True, fill='x', padx=5)
        
        # Второй ряд кнопок
        row2 = ttk.Frame(control_frame)
        row2.pack(fill='x')
        
        self.load_btn = ttk.Button(row2, text="📂 Загрузить настройки", 
                                  command=self.load_settings_from_file, **button_style)
        self.load_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        self.reset_btn = ttk.Button(row2, text="🔄 Сбросить настройки", 
                                   command=self.reset_settings, **button_style)
        self.reset_btn.pack(side='left', expand=True, fill='x', padx=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_frame = ttk.Frame(parent, relief='sunken', borderwidth=1)
        status_frame.pack(fill='x', pady=(15, 0))
        
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                                   anchor='w', padding=10, 
                                   background='#e8e8e8', foreground='#333333',
                                   font=('Segoe UI', 9))
        self.status_bar.pack(fill='x')
    
    def on_scale_change(self, value):
        self.scale.set(int(float(value)))
        self.scale_label.set(f"{self.scale.get()}%")
    
    def on_fps_change(self, value):
        self.target_fps.set(int(float(value)))
        self.fps_label.set(f"{self.target_fps.get()}")
    
    def on_quality_change(self, value):
        self.quality.set(int(float(value)))
        self.quality_label.set(f"{self.quality.get()}%")
    
    def on_sharpen_change(self):
        # Обновляем состояние слайдера резкости
        state = 'normal' if self.sharpen.get() else 'disabled'
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    if isinstance(tab, ttk.Frame):
                        for child in tab.winfo_children():
                            if isinstance(child, ttk.LabelFrame) and "Увеличение резкости" in child.cget('text'):
                                for subchild in child.winfo_children():
                                    if isinstance(subchild, ttk.Frame) and subchild.winfo_children():
                                        for slider in subchild.winfo_children():
                                            if isinstance(slider, ttk.Scale):
                                                slider.config(state=state)
    
    def on_sharpen_amount_change(self, value):
        self.sharpen_amount.set(float(value))
        self.sharpen_label.set(f"{self.sharpen_amount.get():.1f}")
    
    def on_crop_change(self):
        # Здесь можно добавить логику валидации обрезки
        pass
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Выберите видео файл",
            filetypes=[
                ("MP4 files", "*.mp4"), 
                ("Video files", "*.avi *.mov *.MOV *.mkv"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            if not self.output_path.get():
                # Автоматически генерируем имя выходного файла
                output = Path(filename).with_suffix('.webp')
                self.output_path.set(str(output))
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить WebP файл",
            defaultextension=".webp",
            filetypes=[("WebP files", "*.webp"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def save_settings(self):
        settings = {
            'input_path': self.input_path.get(),
            'output_path': self.output_path.get(),
            'scale': self.scale.get(),
            'target_fps': self.target_fps.get(),
            'quality': self.quality.get(),
            'sharpen': self.sharpen.get(),
            'sharpen_amount': self.sharpen_amount.get(),
            'crop_top': self.crop_top.get(),
            'crop_bottom': self.crop_bottom.get(),
            'crop_left': self.crop_left.get(),
            'crop_right': self.crop_right.get()
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.status_var.set("Настройки сохранены успешно!")
            messagebox.showinfo("Сохранено", "Настройки сохранены в файл converter_settings.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
    
    def load_settings(self):
        default_settings = {
            'input_path': '',
            'output_path': '',
            'scale': 70,
            'target_fps': 10,
            'quality': 85,
            'sharpen': True,
            'sharpen_amount': 0.5,
            'crop_top': 0,
            'crop_bottom': 0,
            'crop_left': 0,
            'crop_right': 0
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
                return default_settings
            except:
                return default_settings
        return default_settings
    
    def load_settings_from_file(self):
        filename = filedialog.askopenfilename(
            title="Загрузить настройки",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                # Обновляем переменные
                for key, value in settings.items():
                    if hasattr(self, key):
                        var = getattr(self, key)
                        if isinstance(var, tk.Variable):
                            var.set(value)
                
                # Обновляем отображаемые значения
                self.scale_label.set(f"{self.scale.get()}%")
                self.fps_label.set(f"{self.target_fps.get()}")
                self.quality_label.set(f"{self.quality.get()}%")
                self.sharpen_label.set(f"{self.sharpen_amount.get():.1f}")
                
                # Обновляем состояние слайдера резкости
                self.on_sharpen_change()
                
                self.status_var.set(f"Настройки загружены из {filename}")
                messagebox.showinfo("Загружено", "Настройки успешно загружены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {str(e)}")
    
    def reset_settings(self):
        default_settings = self.load_settings()
        for key, value in default_settings.items():
            if hasattr(self, key):
                var = getattr(self, key)
                if isinstance(var, tk.Variable):
                    var.set(value)
        
        # Обновляем отображаемые значения
        self.scale_label.set(f"{self.scale.get()}%")
        self.fps_label.set(f"{self.target_fps.get()}")
        self.quality_label.set(f"{self.quality.get()}%")
        self.sharpen_label.set(f"{self.sharpen_amount.get():.1f}")
        
        self.status_var.set("Настройки сброшены к значениям по умолчанию")
        messagebox.showinfo("Сброс", "Настройки сброшены к значениям по умолчанию")
    
    def convert_video(self):
        # Проверка входного файла
        if not self.input_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите входной файл")
            return
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Ошибка", "Входной файл не существует")
            return
        
        # Проверка выходного файла
        if not self.output_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, укажите выходной файл")
            return
        
        # Создание папки для выходного файла если нужно
        output_dir = os.path.dirname(self.output_path.get())
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Обновление статуса
        self.status_var.set("Конвертация началась...")
        self.convert_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.load_btn.config(state='disabled')
        self.reset_btn.config(state='disabled')
        self.root.update()
        
        try:
            # Вызов функции конвертации
           
            success, frames = super_optimized_chromakey_simple(
                input_path=self.input_path.get(),
                output_path=self.output_path.get(),
                scale=self.scale.get(),
                target_fps=self.target_fps.get(),
                quality=self.quality.get(),
                sharpen=self.sharpen.get(),
                sharpen_amount=self.sharpen_amount.get(),
                crop_top=self.crop_top.get(),
                crop_bottom=self.crop_bottom.get(),
                crop_left=self.crop_left.get(),
                crop_right=self.crop_right.get()
            )
            
            if success:
                self.status_var.set(f"Готово! Сохранено {frames} кадров")
                messagebox.showinfo("Успех", f"Конвертация завершена успешно!\nСохранено {frames} кадров")
            else:
                self.status_var.set("Ошибка: не удалось сохранить кадры")
                messagebox.showerror("Ошибка", "Не удалось сохранить кадры")
                
        except Exception as e:
            self.status_var.set(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации:\n{str(e)}")
        finally:
            self.convert_btn.config(state='normal')
            self.save_btn.config(state='normal')
            self.load_btn.config(state='normal')
            self.reset_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()