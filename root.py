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

class ModularRootCalculator:
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
        
        self.root.title(ROOT_TITLE)
        self.root.geometry("540x300")
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
        ttk.Label(main_frame, text=ROOT_POWER_LABEL).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.root_power_var = tk.StringVar()
        self.root_power_entry = tk.Entry(main_frame, textvariable=self.root_power_var, width=50, bg="#e0ffe0")
        self.root_power_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.root_power_entry.bind("<Return>", lambda event: self.calculate())
        ttk.Button(main_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.root_power_var.get())).grid(row=1, column=3, padx=2)
        
        ttk.Label(main_frame, text=NUMBER_LABEL).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar()
        self.number_entry = tk.Entry(main_frame, textvariable=self.number_var, width=50, bg="#e0ffe0")
        self.number_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.number_entry.bind("<Return>", lambda event: self.calculate())
        ttk.Button(main_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.number_var.get())).grid(row=2, column=3, padx=2)
        
        ttk.Label(main_frame, text=MODULE_LABEL).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.module_var = tk.StringVar(value=DEFAULT_MODULE)
        self.module_entry = tk.Entry(main_frame, textvariable=self.module_var, width=50, bg="#e0ffe0")
        self.module_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.module_entry.bind("<Return>", lambda event: self.calculate())
        ttk.Button(main_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.module_var.get())).grid(row=3, column=3, padx=2)

        # Кнопки для модулей
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Button(button_frame, text=TEST_BUTTON, command=self.set_test_module).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=BTC_BUTTON, command=self.set_btc_module).pack(side=tk.LEFT, padx=5)
        
        # Кнопка вычислить (отдельно и крупнее)
        calculate_button = tk.Button(main_frame, text=CALCULATE_BUTTON, command=self.calculate, 
                                    bg="#e0ffe0", font=("Arial", 12, "bold"), padx=20, pady=10)
        calculate_button.grid(row=4, column=2, columnspan=2, pady=10, sticky=tk.E)
        
        # Результаты
        result_frame = ttk.LabelFrame(main_frame, text=RESULTS_TITLE)
        result_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(result_frame, text=ROOT_RESULT_LABEL).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(result_frame, textvariable=self.result_var, state="readonly", width=50)
        self.result_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        ttk.Button(result_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.result_var.get())).grid(row=0, column=2, padx=2)
        
        ttk.Label(result_frame, text=SYMMETRIC_LABEL).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.symmetric_var = tk.StringVar()
        ttk.Entry(result_frame, textvariable=self.symmetric_var, state="readonly", width=50).grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        ttk.Button(result_frame, text="📋", width=3, command=lambda: self.copy_to_clipboard(self.symmetric_var.get())).grid(row=1, column=2, padx=2)
    
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
        self.root.title(ROOT_TITLE)
        
        # Обновляем текст всех элементов
        for widget in self.root.winfo_children():
            self._update_widget_text(widget)
        
        # Сохраняем выбранный язык в конфигурацию
        self.config['language'] = selected_language
        self.save_config()
        
        messagebox.showinfo(ROOT_TITLE, f"{LANGUAGE_SELECTED}: {selected_language}")
    
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
                elif row == 1 and column == 0:  # Метка корня
                    widget.config(text=ROOT_POWER_LABEL)
                elif row == 2 and column == 0:  # Метка числа
                    widget.config(text=NUMBER_LABEL)
                elif row == 3 and column == 0:  # Метка модуля
                    widget.config(text=MODULE_LABEL)
            
            # Метки в результирующем фрейме
            if widget.master and isinstance(widget.master, ttk.LabelFrame) and widget.master.grid_info() and widget.master.grid_info().get('row') == 5:
                if widget.grid_info() and 'row' in widget.grid_info():
                    if widget.grid_info()['row'] == 0 and widget.grid_info()['column'] == 0:
                        widget.config(text=ROOT_RESULT_LABEL)
                    elif widget.grid_info()['row'] == 1 and widget.grid_info()['column'] == 0:
                        widget.config(text=SYMMETRIC_LABEL)
        
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
                widget.config(text=RESULTS_TITLE)
    
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
    
    def tonelli_shanks(self, n, p):
        """Алгоритм Тонелли-Шенкса для нахождения квадратного корня по модулю простого числа"""
        # Проверяем, что p - простое число
        if not self.is_prime(p):
            return []
        
        # Проверяем, что n - квадратичный вычет по модулю p
        if pow(n, (p - 1) // 2, p) != 1:
            return []
        
        # Особый случай: p = 2
        if p == 2:
            return [n % 2]
        
        # Находим Q и S такие, что p - 1 = Q * 2^S
        Q, S = p - 1, 0
        while Q % 2 == 0:
            Q //= 2
            S += 1
        
        # Находим квадратичный невычет z
        z = 2
        while pow(z, (p - 1) // 2, p) == 1:
            z += 1
        
        # Инициализируем переменные
        M = S
        c = pow(z, Q, p)
        t = pow(n, Q, p)
        R = pow(n, (Q + 1) // 2, p)
        
        # Основной цикл алгоритма
        while True:
            if t == 0:
                return [0]
            if t == 1:
                return [R, p - R]
            
            # Находим наименьшее i такое, что t^(2^i) = 1 (mod p)
            i = 0
            temp = t
            while temp != 1 and i < M:
                temp = (temp * temp) % p
                i += 1
            
            if i == M:
                return []
            
            # Вычисляем b = c^(2^(M-i-1)) mod p
            b = pow(c, 2 ** (M - i - 1), p)
            
            # Обновляем переменные
            M = i
            c = (b * b) % p
            t = (t * c) % p
            R = (R * b) % p
    
    def find_nth_roots(self, n, a, m):
        """Находит все n-е корни числа a по модулю m"""
        # Проверяем, что n и m взаимно просты
        if math.gcd(n, m) != 1:
            # Для случая, когда n и m не взаимно просты, используем более сложный алгоритм
            # Это упрощенная реализация для демонстрации
            return self.find_roots_general(n, a, m)
        
        # Находим обратное к n по модулю phi(m)
        if self.is_prime(m):
            phi_m = m - 1
        else:
            # Для составных чисел вычисляем функцию Эйлера
            phi_m = sympy.totient(m)
        
        # Проверяем, что n и phi(m) взаимно просты
        if math.gcd(n, phi_m) != 1:
            return self.find_roots_general(n, a, m)
        
        # Находим обратное к n по модулю phi(m)
        n_inv = pow(n, -1, phi_m)
        
        # Вычисляем x = a^(n_inv) mod m
        x = pow(a, n_inv, m)
        
        # Проверяем, что x^n = a (mod m)
        if pow(x, n, m) == a % m:
            return [x]
        else:
            return []
    
    def find_roots_general(self, n, a, m):
        """Общий метод для нахождения n-х корней по модулю m"""
        # Для простоты реализации ограничимся перебором для небольших модулей
        # Для больших модулей нужно использовать более эффективные алгоритмы
        if m > 10**6:  # Ограничение для больших модулей
            # Используем метод на основе китайской теоремы об остатках для больших модулей
            return self.find_roots_crt(n, a, m)
        
        roots = []
        a = a % m
        
        # Перебираем все возможные значения от 0 до m-1
        for x in range(m):
            if pow(x, n, m) == a:
                roots.append(x)
        
        return roots
    
    def find_roots_crt(self, n, a, m):
        """Метод нахождения корней с использованием китайской теоремы об остатках"""
        # Разложение модуля на простые множители
        factors = sympy.factorint(m)
        
        # Находим корни по каждому простому модулю
        all_roots = []
        for prime, power in factors.items():
            prime_power = prime ** power
            prime_roots = self.find_roots_prime_power(n, a % prime_power, prime, power)
            all_roots.append((prime_power, prime_roots))
        
        # Если по какому-то модулю нет корней, то и по всему модулю нет корней
        if any(not roots for _, roots in all_roots):
            return []
        
        # Применяем китайскую теорему об остатках
        result = []
        for combination in self.cartesian_product([roots for _, roots in all_roots]):
            # Решаем систему сравнений с помощью китайской теоремы об остатках
            moduli = [mod for mod, _ in all_roots]
            remainders = combination
            root = self.chinese_remainder_theorem(moduli, remainders)
            if root is not None:
                result.append(root)
        
        return result
    
    def find_roots_prime_power(self, n, a, p, k):
        """Находит n-е корни по модулю p^k, где p - простое число"""
        # Находим корни по модулю p
        roots_mod_p = []
        
        # Для квадратного корня используем алгоритм Тонелли-Шенкса
        if n == 2:
            roots_mod_p = self.tonelli_shanks(a % p, p)
        else:
            # Для других корней используем более общий подход
            g = math.gcd(n, p - 1)
            if pow(a, (p - 1) // g, p) != 1:
                return []
            
            # Находим все корни по модулю p
            for i in range(g):
                # Находим один корень
                n_inv = pow(n // g, -1, (p - 1) // g)
                x = pow(a, n_inv, p)
                
                # Находим примитивный корень по модулю p
                primitive_root = 2
                while pow(primitive_root, (p - 1) // g, p) == 1:
                    primitive_root += 1
                
                # Генерируем все корни
                omega = pow(primitive_root, (p - 1) // g, p)
                root = (x * pow(omega, i, p)) % p
                roots_mod_p.append(root)
        
        # Если k = 1, возвращаем корни по модулю p
        if k == 1:
            return roots_mod_p
        
        # Поднимаем корни до модуля p^k с помощью метода Хензеля
        roots_mod_pk = []
        for r in roots_mod_p:
            # Применяем лемму Хензеля для поднятия корня
            root = r
            for i in range(1, k):
                p_i = p ** i
                f_prime = (n * pow(root, n - 1, p_i)) % p_i
                if f_prime == 0:  # Если производная равна 0, корень не может быть поднят
                    continue
                
                f_prime_inv = pow(f_prime, -1, p_i)
                correction = ((a - pow(root, n, p_i * p)) * f_prime_inv) % (p_i * p)
                root = (root + correction * p_i) % (p_i * p)
            
            roots_mod_pk.append(root)
        
        return roots_mod_pk
    
    def cartesian_product(self, lists):
        """Возвращает декартово произведение списков"""
        if not lists:
            return [()]
        result = []
        for item in lists[0]:
            for rest in self.cartesian_product(lists[1:]):
                result.append((item,) + rest)
        return result
    
    def chinese_remainder_theorem(self, moduli, remainders):
        """Решает систему сравнений с помощью китайской теоремы об остатках"""
        if len(moduli) != len(remainders):
            return None
        
        # Вычисляем произведение всех модулей
        M = 1
        for modulus in moduli:
            M *= modulus
        
        result = 0
        for modulus, remainder in zip(moduli, remainders):
            m_i = M // modulus
            # Находим обратное к m_i по модулю modulus
            try:
                m_i_inv = pow(m_i, -1, modulus)
            except:
                return None
            
            result = (result + remainder * m_i * m_i_inv) % M
        
        return result
    
    def copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
    
    def calculate(self):
        """Вычисляет корни по модулю"""
        try:
            # Показываем индикатор выполнения для сложных вычислений
            self.result_var.set(CALCULATING)
            self.root.update_idletasks()
            
            root_power = self.root_power_var.get().strip()
            number = self.number_var.get().strip()
            mod_str = self.module_var.get().strip()
            
            if not root_power or not number:
                raise ValueError(ERROR_INVALID_EXPRESSION)
            
            try:
                n = int(root_power)
                a = int(number)
                mod = int(mod_str)
                if n <= 0 or mod <= 0:
                    raise ValueError
            except:
                raise ValueError(ERROR_INVALID_MODULE)
            
            # Засекаем время выполнения для отладки
            start_time = time.time()
            
            # Находим все корни
            roots = self.find_nth_roots(n, a, mod)
            
            # Выводим время выполнения для отладки
            end_time = time.time()
            print(f"Время выполнения: {end_time - start_time:.6f} секунд")
            
            # Выводим результат
            if not roots:
                self.result_var.set(NO_ROOTS)
                self.symmetric_var.set("")
            else:
                # Сортируем корни для удобства
                roots.sort()
                self.result_var.set(", ".join(str(root) for root in roots))
                
                # Вычисляем симметричные представления
                symmetric_roots = [(mod - root) % mod for root in roots]
                symmetric_roots.sort()
                self.symmetric_var.set(", ".join(str(root) for root in symmetric_roots))
            
        except Exception as e:
            messagebox.showerror(ROOT_TITLE, str(e))

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

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ModularRootCalculator(root)
    root.mainloop()