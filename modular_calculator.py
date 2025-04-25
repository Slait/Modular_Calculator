import tkinter as tk
from tkinter import ttk, messagebox
import math
import sympy
import re
import os
import sys
import time
import json

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем языковые файлы
import importlib
from lang.ru import *

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

class ModularCalculator:
    def __init__(self, root):
        self.root = root
        
        # Загружаем настройки
        self.config = self.load_config()
        
        # Устанавливаем язык из конфигурации
        if self.config.get('language') == 'English':
            importlib.reload(sys.modules['lang.ru'])
            lang_module = importlib.import_module('lang.en')
            for var_name in dir(lang_module):
                if var_name.isupper():
                    globals()[var_name] = getattr(lang_module, var_name)
        
        self.root.title(TITLE)
        self.root.geometry("540x450")
        self.root.resizable(True, True)
        
        # Создаем основной фрейм
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Выпадающий список для выбора языка
        ttk.Label(main_frame, text=LANGUAGE_LABEL).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=self.config.get('language', 'Русский'))
        language_combo = ttk.Combobox(main_frame, textvariable=self.language_var, state="readonly", width=15)
        language_combo['values'] = ("Русский", "English")
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        language_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Создаем элементы интерфейса
        ttk.Label(main_frame, text=EXPRESSION_LABEL).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.expression_var = tk.StringVar()
        self.expression_entry = tk.Entry(main_frame, textvariable=self.expression_var, width=50, bg="#e0ffe0")
        self.expression_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.expression_entry.bind("<Return>", lambda event: self.calculate())
        ttk.Button(main_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.expression_var.get())).grid(row=1, column=3, padx=2)
        
        ttk.Label(main_frame, text=MODULE_LABEL).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.module_var = tk.StringVar(value=DEFAULT_MODULE)
        module_entry = ttk.Entry(main_frame, textvariable=self.module_var, width=50)
        module_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        ttk.Button(main_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.module_var.get())).grid(row=2, column=3, padx=2)
        
        # Кнопки для модулей
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Button(button_frame, text=TEST_BUTTON, command=self.set_test_module).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=BTC_BUTTON, command=self.set_btc_module).pack(side=tk.LEFT, padx=5)
        
        # Кнопка вычислить (отдельно и крупнее)
        calculate_button = tk.Button(main_frame, text=CALCULATE_BUTTON, command=self.calculate, 
                                    bg="#e0ffe0", font=("Arial", 12, "bold"), padx=20, pady=10)
        calculate_button.grid(row=3, column=2, columnspan=2, pady=10, sticky=tk.E)
        
        # Результаты
        result_frame = ttk.LabelFrame(main_frame, text="")
        result_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(result_frame, text=RESULT_LABEL).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.result_var = tk.StringVar()
        result_entry = ttk.Entry(result_frame, textvariable=self.result_var, state="readonly", width=50)
        result_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        ttk.Button(result_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.result_var.get())).grid(row=0, column=2, padx=2)
        
        ttk.Label(result_frame, text=SYMMETRIC_LABEL).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.symmetric_var = tk.StringVar()
        symmetric_entry = ttk.Entry(result_frame, textvariable=self.symmetric_var, state="readonly", width=50)
        symmetric_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        ttk.Button(result_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.symmetric_var.get())).grid(row=1, column=2, padx=2)
        
        # Подсказка по операциям
        hint_frame = ttk.LabelFrame(main_frame, text=OPERATIONS_HINT_TITLE)
        hint_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(hint_frame, text=OPERATIONS_HINT).grid(row=0, column=0, sticky=tk.W, pady=5)
    
    def change_language(self, event):
        """Изменяет язык интерфейса"""
        selected_language = self.language_var.get()
        
        # Импортируем соответствующий языковой модуль
        if selected_language == "English":
            lang_module = importlib.import_module("lang.en")
        else:  # По умолчанию русский
            lang_module = importlib.import_module("lang.ru")
        
        # Обновляем глобальные переменные языка
        for var_name in dir(lang_module):
            if var_name.isupper():  # Только константы
                globals()[var_name] = getattr(lang_module, var_name)
        
        # Обновляем элементы интерфейса
        self.root.title(TITLE)
        
        # Обновляем текст всех элементов
        for widget in self.root.winfo_children():
            self._update_widget_text(widget)
        
        # Сохраняем выбранный язык в конфигурацию
        self.config['language'] = selected_language
        self.save_config()
        
        messagebox.showinfo(TITLE, f"{LANGUAGE_SELECTED}: {selected_language}")
    
    def _update_widget_text(self, widget):
        """Рекурсивно обновляет текст всех виджетов"""
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                self._update_widget_text(child)
        
        # Обновляем текст меток
        if isinstance(widget, ttk.Label) or isinstance(widget, tk.Label):
            # Обновляем основные метки интерфейса
            if widget.grid_info() and 'row' in widget.grid_info():
                row = widget.grid_info()['row']
                column = widget.grid_info()['column']
                
                # Метки в основном фрейме
                if row == 0 and column == 0:  # Метка языка
                    widget.config(text=LANGUAGE_LABEL)
                elif row == 1 and column == 0:  # Метка выражения
                    widget.config(text=EXPRESSION_LABEL)
                elif row == 2 and column == 0:  # Метка модуля
                    widget.config(text=MODULE_LABEL)
            
            # Метки в результирующем фрейме
            if widget.master and isinstance(widget.master, ttk.LabelFrame) and widget.master.grid_info() and widget.master.grid_info().get('row') == 4:
                if widget.grid_info() and 'row' in widget.grid_info():
                    if widget.grid_info()['row'] == 0 and widget.grid_info()['column'] == 0:
                        widget.config(text=RESULT_LABEL)
                    elif widget.grid_info()['row'] == 1 and widget.grid_info()['column'] == 0:
                        widget.config(text=SYMMETRIC_LABEL)
            
            # Метка с подсказкой операций
            if widget.master and isinstance(widget.master, ttk.LabelFrame) and widget.master.grid_info() and widget.master.grid_info().get('row') == 5:
                widget.config(text=OPERATIONS_HINT)
        
        # Обновляем текст кнопок
        if isinstance(widget, ttk.Button) or isinstance(widget, tk.Button):
            if widget.cget('text') == "Тестовый 79" or widget.cget('text') == "Testing 79":
                widget.config(text=TEST_BUTTON)
            elif widget.cget('text') == "BTC":
                widget.config(text=BTC_BUTTON)
            elif widget.cget('text') == "Вычислить" or widget.cget('text') == "Calculate":
                widget.config(text=CALCULATE_BUTTON)
        
        # Обновляем текст фреймов
        if isinstance(widget, ttk.LabelFrame):
            if widget.grid_info() and widget.grid_info().get('row') == 5:
                widget.config(text=OPERATIONS_HINT_TITLE)
    
    def set_test_module(self):
        """Устанавливает тестовый модуль 79"""
        self.module_var.set("79")
    
    def set_btc_module(self):
        """Устанавливает модуль BTC"""
        self.module_var.set("115792089237316195423570985008687907852837564279074904382605163141518161494337")
    
    def is_prime(self, n):
        """Проверяет, является ли число простым"""
        try:
            return sympy.isprime(n)
        except:
            return False
    
    def mod_inverse(self, a, m):
        """Вычисляет обратное по модулю"""
        try:
            return pow(a, -1, m)
        except:
            raise ValueError(ERROR_DIVISION_NON_PRIME)
    
    def fast_power_mod(self, base, exponent, modulus):
        """Быстрое возведение в степень по модулю"""
        if modulus == 1:
            return 0
        
        result = 1
        base = base % modulus
        
        while exponent > 0:
            # Если текущий бит экспоненты равен 1, умножаем результат на базу
            if exponent % 2 == 1:
                result = (result * base) % modulus
            
            # Сдвигаем на один бит вправо
            exponent = exponent >> 1
            base = (base * base) % modulus
            
        return result
    
    def evaluate_expression(self, expr, mod):
        """Вычисляет выражение по модулю"""
        # Заменяем оператор возведения в степень на специальный обработчик
        # Ищем все вхождения вида a^b
        power_pattern = r'(\d+)\^(\d+)'
        
        # Заменяем все степени на вызов нашей оптимизированной функции
        while re.search(power_pattern, expr):
            match = re.search(power_pattern, expr)
            if match:
                base = int(match.group(1))
                exp = int(match.group(2))
                # Вычисляем результат быстрого возведения в степень
                power_result = self.fast_power_mod(base, exp, mod)
                # Заменяем выражение на результат
                expr = expr.replace(f"{base}^{exp}", str(power_result))
            else:
                break
        
        # Заменяем оставшиеся операторы возведения в степень на стандартный Python оператор
        expr = expr.replace("^", "**")
        
        # Проверяем наличие операции деления
        if "/" in expr and not self.is_prime(mod):
            raise ValueError(ERROR_DIVISION_NON_PRIME)
        
        # Заменяем деление на умножение на обратное по модулю
        while "/" in expr:
            match = re.search(r'(\d+)/(\d+)', expr)
            if match:
                num, denom = int(match.group(1)), int(match.group(2))
                inv = self.mod_inverse(denom, mod)
                expr = expr.replace(f"{num}/{denom}", f"{num}*{inv}")
            else:
                break
        
        # Вычисляем выражение
        # Используем безопасный eval с ограниченными функциями
        allowed_names = {"__builtins__": {}}
        code = compile(expr, "<string>", "eval")
        
        # Проверяем, что в выражении используются только разрешенные операции
        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(ERROR_INVALID_EXPRESSION)
        
        result = eval(expr, {"__builtins__": {}}, {})
        
        # Возвращаем результат по модулю
        return result % mod
    
    def calculate(self):
        """Вычисляет результат выражения по модулю"""
        try:
            # Показываем индикатор выполнения для сложных вычислений
            self.result_var.set(CALCULATING)
            self.root.update_idletasks()
            
            expr = self.expression_var.get().strip()
            mod_str = self.module_var.get().strip()
            
            if not expr:
                raise ValueError(ERROR_INVALID_EXPRESSION)
            
            try:
                mod = int(mod_str)
                if mod <= 0:
                    raise ValueError
            except:
                raise ValueError(ERROR_INVALID_MODULE)
            
            # Засекаем время выполнения для отладки
            start_time = time.time()
            
            result = self.evaluate_expression(expr, mod)
            
            # Выводим время выполнения для отладки
            end_time = time.time()
            print(f"Время выполнения: {end_time - start_time:.6f} секунд")
            
            self.result_var.set(str(result))
            
            # Вычисляем симметричное представление
            symmetric = (mod - result) % mod
            self.symmetric_var.set(str(symmetric))
            
        except Exception as e:
            messagebox.showerror(TITLE, str(e))

    def load_config(self):
        """Загружает конфигурацию из файла"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'language': 'Русский'}
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return {'language': 'Русский'}
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")

    def copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModularCalculator(root)
    root.mainloop()