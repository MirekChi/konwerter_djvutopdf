#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop GUI dla konwertera DjVu -> PDF
Aplikacja desktopowa oparta na tkinter
"""

import os
import sys
import subprocess
import glob
import threading
from pathlib import Path
import shutil
from tkinter import *
from tkinter import ttk, filedialog, messagebox

class DjVuToPDFGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Konwerter DjVu → PDF")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Zmienne
        self.selected_files = []
        self.ddjvu_path = None
        self.output_directory = StringVar()
        self.quality = StringVar(value='normal')
        self.timeout = IntVar(value=300)
        self.same_directory = BooleanVar(value=True)
        self.is_converting = False
        
        self.setup_ui()
        self.center_window()
        self.check_ddjvu()
        
    def center_window(self):
        """Wyśrodkuj okno na ekranie"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        """Stwórz interfejs użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))
        
        # Konfiguracja siatki
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="Konwerter DjVu → PDF", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status ddjvu
        self.ddjvu_status_frame = ttk.Frame(main_frame)
        self.ddjvu_status_frame.grid(row=1, column=0, columnspan=3, sticky=(W, E), pady=(0, 10))
        self.ddjvu_status_frame.columnconfigure(1, weight=1)
        
        self.ddjvu_status_label = ttk.Label(self.ddjvu_status_frame, text="Sprawdzanie ddjvu...")
        self.ddjvu_status_label.grid(row=0, column=0, sticky=W)
        
        # Sekcja wyboru plików
        files_frame = ttk.LabelFrame(main_frame, text="Pliki do konwersji", padding="10")
        files_frame.grid(row=2, column=0, columnspan=3, sticky=(W, E, N, S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(2, weight=1)
        
        # Przyciski wyboru plików
        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Wybierz pliki DjVu", 
                  command=self.select_files).pack(side=LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Wybierz katalog", 
                  command=self.select_directory).pack(side=LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Wyczyść listę", 
                  command=self.clear_files).pack(side=LEFT)
        
        # Informacja o plikach
        self.files_info_label = ttk.Label(files_frame, text="Nie wybrano plików")
        self.files_info_label.grid(row=1, column=0, columnspan=2, sticky=W, pady=(0, 5))
        
        # Lista plików
        list_frame = ttk.Frame(files_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(W, E, N, S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.files_listbox = Listbox(list_frame, height=6)
        self.files_listbox.grid(row=0, column=0, sticky=(W, E, N, S), padx=(0, 10))
        
        # Scrollbar dla listy
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.files_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Sekcja ustawień
        settings_frame = ttk.LabelFrame(main_frame, text="Ustawienia konwersji", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(W, E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Jakość konwersji
        ttk.Label(settings_frame, text="Jakość:").grid(row=0, column=0, sticky=W, padx=(0, 10))
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.grid(row=0, column=1, sticky=W, pady=(0, 5))
        
        ttk.Radiobutton(quality_frame, text="Niska (szybka, mały rozmiar)", 
                       variable=self.quality, value='low').pack(anchor=W)
        ttk.Radiobutton(quality_frame, text="Normalna (zalecana)", 
                       variable=self.quality, value='normal').pack(anchor=W)
        ttk.Radiobutton(quality_frame, text="Wysoka (wolna, duży rozmiar)", 
                       variable=self.quality, value='high').pack(anchor=W)
        
        # Timeout
        ttk.Label(settings_frame, text="Timeout (sekundy):").grid(row=1, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        timeout_frame = ttk.Frame(settings_frame)
        timeout_frame.grid(row=1, column=1, sticky=W, pady=(10, 0))
        
        self.timeout_spinbox = ttk.Spinbox(timeout_frame, from_=30, to=3600, 
                                          width=10, textvariable=self.timeout)
        self.timeout_spinbox.pack(side=LEFT, padx=(0, 10))
        ttk.Label(timeout_frame, text="(30-3600 sekund)").pack(side=LEFT)
        
        # Katalog wyjściowy
        ttk.Checkbutton(settings_frame, text="Zapisz w tym samym katalogu co pliki źródłowe",
                       variable=self.same_directory, 
                       command=self.toggle_output_directory).grid(row=2, column=0, columnspan=2, 
                                                                 sticky=W, pady=(10, 5))
        
        self.output_frame = ttk.Frame(settings_frame)
        self.output_frame.grid(row=3, column=0, columnspan=2, sticky=(W, E), pady=(5, 0))
        self.output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.output_frame, text="Katalog wyjściowy:").grid(row=0, column=0, sticky=W, padx=(0, 10))
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_directory, state=DISABLED)
        self.output_entry.grid(row=0, column=1, sticky=(W, E), padx=(0, 10))
        self.output_button = ttk.Button(self.output_frame, text="Przeglądaj...", 
                                       command=self.select_output_directory, state=DISABLED)
        self.output_button.grid(row=0, column=2)
        
        # Sekcja konwersji
        convert_frame = ttk.Frame(main_frame)
        convert_frame.grid(row=4, column=0, columnspan=3, sticky=(W, E), pady=(10, 0))
        convert_frame.columnconfigure(0, weight=1)
        
        # Pasek postępu
        self.progress = ttk.Progressbar(convert_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(W, E), pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(convert_frame, text="Gotowy do konwersji")
        self.status_label.grid(row=1, column=0, sticky=W, pady=(0, 10))
        
        # Log konwersji
        log_frame = ttk.LabelFrame(convert_frame, text="Log konwersji", padding="5")
        log_frame.grid(row=2, column=0, sticky=(W, E, N, S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = Text(log_frame, height=8, wrap=WORD)
        self.log_text.grid(row=0, column=0, sticky=(W, E, N, S))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Przycisk konwersji
        self.convert_button = ttk.Button(convert_frame, text="Rozpocznij konwersję", 
                                        command=self.start_conversion, style="Accent.TButton")
        self.convert_button.grid(row=3, column=0, pady=(0, 10))
        
        # Konfiguracja wag dla responsywności
        main_frame.rowconfigure(2, weight=1)
        convert_frame.rowconfigure(2, weight=1)
        
    def find_ddjvu(self):
        """Znajdź ścieżkę do ddjvu"""
        env_path = os.environ.get('DJVU_PATH')
        if env_path:
            if os.path.isfile(env_path) and os.access(env_path, os.X_OK):
                return env_path
            if os.path.isdir(env_path):
                candidate = os.path.join(env_path, 'ddjvu.exe' if os.name == 'nt' else 'ddjvu')
                if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                    return candidate

        for name in ('ddjvu', 'ddjvu.exe'):
            path = shutil.which(name)
            if path:
                return path

        return None
        
    def check_ddjvu(self):
        """Sprawdź dostępność ddjvu"""
        self.ddjvu_path = self.find_ddjvu()
        if self.ddjvu_path:
            self.ddjvu_status_label.config(text=f"✅ ddjvu znaleziony: {os.path.basename(self.ddjvu_path)}")
            self.ddjvu_status_label.config(foreground='green')
        else:
            self.ddjvu_status_label.config(text="❌ ddjvu nie znaleziony - sprawdź PATH lub DJVU_PATH")
            self.ddjvu_status_label.config(foreground='red')
            
    def find_djvu_files(self, directory):
        """Znajdź pliki DjVu w katalogu"""
        patterns = ['*.djvu', '*.djv', '*.DJVU', '*.DJV']
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
        return sorted(files)
        
    def toggle_output_directory(self):
        """Przełącz dostępność wyboru katalogu wyjściowego"""
        if self.same_directory.get():
            self.output_entry.config(state=DISABLED)
            self.output_button.config(state=DISABLED)
        else:
            self.output_entry.config(state=NORMAL)
            self.output_button.config(state=NORMAL)
            
    def select_files(self):
        """Wybierz pliki DjVu"""
        files = filedialog.askopenfilenames(
            title="Wybierz pliki DjVu",
            filetypes=[("Pliki DjVu", "*.djvu *.djv *.DJVU *.DJV"), ("Wszystkie pliki", "*.*")]
        )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.update_files_list()
                
    def select_directory(self):
        """Wybierz katalog z plikami DjVu"""
        directory = filedialog.askdirectory(title="Wybierz katalog z plikami DjVu")
        
        if directory:
            djvu_files = self.find_djvu_files(directory)
            
            if not djvu_files:
                messagebox.showwarning("Ostrzeżenie", 
                                     f"Nie znaleziono plików DjVu w katalogu:\n{directory}")
                return
            
            for file in djvu_files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    
            self.update_files_list()
                    
    def clear_files(self):
        """Wyczyść listę plików"""
        self.selected_files.clear()
        self.update_files_list()
        
    def update_files_list(self):
        """Aktualizuj listę plików"""
        self.files_listbox.delete(0, END)
        if self.selected_files:
            total_size = 0
            for file in self.selected_files:
                filename = os.path.basename(file)
                self.files_listbox.insert(END, filename)
                try:
                    total_size += os.path.getsize(file)
                except:
                    pass
            size_mb = total_size / (1024 * 1024)
            self.files_info_label.config(text=f"Wybrano {len(self.selected_files)} plików ({size_mb:.1f} MB)")
        else:
            self.files_info_label.config(text="Nie wybrano plików")
            
    def select_output_directory(self):
        """Wybierz katalog wyjściowy"""
        directory = filedialog.askdirectory(title="Wybierz katalog wyjściowy")
        if directory:
            self.output_directory.set(directory)
            
    def log_message(self, message):
        """Dodaj wiadomość do loga"""
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.root.update_idletasks()
        
    def convert_file(self, djvu_file, output_dir, quality='normal', timeout_s=300):
        """Konwertuj pojedynczy plik DjVu na PDF"""
        filename = os.path.basename(djvu_file)
        name_without_ext = os.path.splitext(filename)[0]
        pdf_file = os.path.join(output_dir, f"{name_without_ext}.pdf")
        
        quality_params = {
            'low': ['-quality=25', '-smooth'],
            'normal': ['-quality=75'],
            'high': ['-quality=100', '-smooth']
        }
        
        params = quality_params.get(quality, ['-quality=75'])
        cmd = [self.ddjvu_path, '-format=pdf'] + params + [djvu_file, pdf_file]
        
        self.log_message(f"🔄 Konwertowanie: {filename}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
            if result.returncode == 0:
                try:
                    size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
                    self.log_message(f"✅ Utworzono: {name_without_ext}.pdf ({size_mb:.1f} MB)")
                except:
                    self.log_message(f"✅ Utworzono: {name_without_ext}.pdf")
                return True
            else:
                self.log_message(f"❌ Błąd konwersji {filename} (kod {result.returncode})")
                if result.stdout:
                    self.log_message(f"STDOUT: {result.stdout}")
                if result.stderr:
                    self.log_message(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message(f"❌ Przekroczono limit czasu ({timeout_s}s) dla: {filename}")
            return False
        except Exception as e:
            self.log_message(f"❌ Błąd: {filename} - {e}")
            return False
            
    def start_conversion(self):
        """Rozpocznij konwersję"""
        if not self.ddjvu_path:
            messagebox.showerror("Błąd", "ddjvu nie jest dostępny!\n\nDodaj ddjvu.exe do PATH lub ustaw zmienną środowiskową DJVU_PATH.")
            return
            
        if not self.selected_files:
            messagebox.showwarning("Ostrzeżenie", "Nie wybrano żadnych plików do konwersji!")
            return
            
        if not self.same_directory.get() and not self.output_directory.get():
            messagebox.showwarning("Ostrzeżenie", "Wybierz katalog wyjściowy!")
            return
            
        if self.is_converting:
            return
            
        # Uruchom konwersję w osobnym wątku
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
        
    def convert_files(self):
        """Konwertuj pliki (uruchamiane w osobnym wątku)"""
        self.is_converting = True
        total_files = len(self.selected_files)
        successful = 0
        
        # Przygotuj katalog wyjściowy
        if not self.same_directory.get():
            output_dir = Path(self.output_directory.get())
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Aktualizuj interfejs
        self.root.after(0, lambda: self.convert_button.config(state=DISABLED, text="Konwertowanie..."))
        self.root.after(0, lambda: self.progress.config(maximum=total_files, value=0))
        self.root.after(0, lambda: self.log_text.delete(1.0, END))
        
        self.root.after(0, lambda: self.log_message(f"📋 Rozpoczynam konwersję {total_files} plików"))
        self.root.after(0, lambda: self.log_message(f"📁 Katalog wyjściowy: {self.output_directory.get() if not self.same_directory.get() else 'Ten sam co źródłowe'}"))
        self.root.after(0, lambda: self.log_message(f"🎨 Jakość: {self.quality.get()}"))
        self.root.after(0, lambda: self.log_message(f"⏱️ Timeout: {self.timeout.get()}s"))
        self.root.after(0, lambda: self.log_message("=" * 50))
        
        for i, file_path in enumerate(self.selected_files):
            if not self.is_converting:  # Sprawdź czy nie przerwano
                break
                
            filename = os.path.basename(file_path)
            self.root.after(0, lambda f=filename: self.status_label.config(text=f"Konwertowanie: {f}"))
            
            # Ustal katalog wyjściowy
            if self.same_directory.get():
                output_dir = os.path.dirname(file_path)
            else:
                output_dir = self.output_directory.get()
            
            # Konwertuj plik
            if self.convert_file(file_path, output_dir, self.quality.get(), self.timeout.get()):
                successful += 1
            
            # Aktualizuj pasek postępu
            self.root.after(0, lambda v=i+1: self.progress.config(value=v))
        
        # Zakończ konwersję
        self.root.after(0, self.conversion_finished, successful, total_files)
        
    def conversion_finished(self, successful, total):
        """Zakończ proces konwersji"""
        self.is_converting = False
        self.convert_button.config(state=NORMAL, text="Rozpocznij konwersję")
        
        self.log_message("=" * 50)
        self.log_message(f"📊 PODSUMOWANIE")
        self.log_message(f"✅ Pomyślnie skonwertowano: {successful}")
        self.log_message(f"❌ Błędy: {total - successful}")
        
        self.status_label.config(text=f"Zakończono: {successful}/{total} plików skonwertowanych")
        
        if successful == total:
            messagebox.showinfo("Sukces", f"Pomyślnie skonwertowano wszystkie {total} plików!")
        elif successful > 0:
            messagebox.showwarning("Częściowy sukces", 
                                 f"Skonwertowano {successful} z {total} plików.\n"
                                 f"Sprawdź log dla szczegółów błędów.")
        else:
            messagebox.showerror("Błąd", "Nie udało się skonwertować żadnego pliku!")

def main():
    """Główna funkcja aplikacji"""
    root = Tk()
    
    # Ustaw styl
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    
    app = DjVuToPDFGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()

if __name__ == "__main__":
    main()