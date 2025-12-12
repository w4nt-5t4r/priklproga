import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import pygame
    from pygame import mixer
except ImportError:
    pygame = None
    mixer = None

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg"}

class AudioPlayerTk:
    def __init__(self, root):
        self.root = root
        self.root.title("Аудиоплеер")
        self.root.geometry("800x500")
        self.root.minsize(600, 380)

        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.repeat = tk.BooleanVar(value=False)
        self.volume = tk.DoubleVar(value=0.8)

        if pygame is None or mixer is None:
            messagebox.showerror("Ошибка", "Установите pygame: pip install pygame")
            sys.exit()

        mixer.init()
        mixer.music.set_volume(self.volume.get())

        self.create_menu()
        self.create_layout()

        self.root.bind("<space>", lambda e: self.toggle_play_pause())
        self.root.bind("<s>", lambda e: self.stop())
        self.root.bind("<Right>", lambda e: self.next_track())
        self.root.bind("<Left>", lambda e: self.prev_track())
        self.root.bind("<Escape>", lambda e: self.on_exit())

        self.update_ui()
        self.root.after(500, self.update_loop)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Открыть файлы...", command=self.open_files)
        file_menu.add_command(label="Выход", command=self.on_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        play_menu = tk.Menu(menubar, tearoff=False)
        play_menu.add_command(label="Играть/Пауза", command=self.toggle_play_pause)
        play_menu.add_command(label="Стоп", command=self.stop)
        play_menu.add_command(label="Предыдущий трек", command=self.prev_track)
        play_menu.add_command(label="Следующий трек", command=self.next_track)
        menubar.add_cascade(label="Воспроизведение", menu=play_menu)

        self.root.config(menu=menubar)

    def create_layout(self):
        style = ttk.Style()
        style.theme_use("clam")

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=8)

        self.track_label = ttk.Label(top_frame, text="Выберите аудиофайл")
        self.track_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.time_label = ttk.Label(top_frame, text="00:00")
        self.time_label.pack(side=tk.RIGHT)

        center_frame = ttk.Frame(self.root)
        center_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.listbox = tk.Listbox(center_frame, selectmode=tk.SINGLE, font=("Segoe UI", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(center_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=8)

        self.btn_open = ttk.Button(bottom_frame, text="📂 Открыть", command=self.open_files)
        self.btn_prev = ttk.Button(bottom_frame, text="⏮ Предыдущий", command=self.prev_track)
        self.btn_play_pause = ttk.Button(bottom_frame, text="▶ Играть", command=self.toggle_play_pause)
        self.btn_stop = ttk.Button(bottom_frame, text="⏹ Стоп", command=self.stop)
        self.btn_next = ttk.Button(bottom_frame, text="⏭ Следующий", command=self.next_track)
        self.btn_exit = ttk.Button(bottom_frame, text="❌ Выход", command=self.on_exit)

        for btn in (self.btn_open, self.btn_prev, self.btn_play_pause, self.btn_stop, self.btn_next, self.btn_exit):
            btn.pack(side=tk.LEFT, padx=6)

        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(controls_frame, text="Громкость").pack(side=tk.LEFT, padx=(0, 8))
        self.volume_scale = ttk.Scale(controls_frame, from_=0.0, to=1.0, variable=self.volume, command=self.on_volume_change)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.repeat_check = ttk.Checkbutton(controls_frame, text="Повтор", variable=self.repeat)
        self.repeat_check.pack(side=tk.LEFT, padx=10)

        self.status = tk.StringVar(value="Готово")
        statusbar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def open_files(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Аудио файлы", "*.mp3 *.wav *.ogg"), ("Все файлы", "*.*")]
        )
        for path in paths:
            if os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS:
                self.playlist.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))

        if self.playlist and self.current_index == -1:
            self.current_index = 0
            self.listbox.select_set(0)
            self.load_track()

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if sel:
            self.current_index = sel[0]
            self.load_track()

    def load_track(self):
        if not (0 <= self.current_index < len(self.playlist)):
            return
        path = self.playlist[self.current_index]
        mixer.music.load(path)
        mixer.music.set_volume(self.volume.get())
        self.is_playing = False
        self.is_paused = False
        self.track_label.config(text=f"Текущий трек: {os.path.basename(path)}")
        self.time_label.config(text="00:00")
        self.status.set(f"Загружен: {os.path.basename(path)}")

    def toggle_play_pause(self):
        if self.is_playing and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True
            self.btn_play_pause.config(text="▶ Продолжить")
            self.status.set("На паузе")
        elif self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True
            self.btn_play_pause.config(text="⏸ Пауза")
            self.status.set("Воспроизведение")
        else:
            if self.current_index >= 0:
                mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.btn_play_pause.config(text="⏸ Пауза")
                self.status.set("Воспроизведение")

    def stop(self):
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.btn_play_pause.config(text="▶ Играть")
        self.status.set("Остановлено")

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_index)
        self.load_track()
        mixer.music.play()
        self.is_playing = True
        self.btn_play_pause.config(text="⏸ Пауза")

    def prev_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_index)
        self.load_track()
        mixer.music.play()
        self.is_playing = True
        self.btn_play_pause.config(text="⏸ Пауза")

    def on_volume_change(self, event=None):
        mixer.music.set_volume(self.volume.get())

    def update_ui(self):
        try:
            if mixer.get_init():
                pos = mixer.music.get_pos()
                if pos >= 0:
                    s = pos // 1000
                    self.time_label.config(text=f"{s//60:02}:{s%60:02}")
                if self.is_playing and not self.is_paused and not mixer.music.get_busy():
                    if self.repeat.get():
                        mixer.music.play()
                        self.status.set("Повтор трека")
                    else:
                        self.is_playing = False
                        self.btn_play_pause.config(text="▶ Играть")
                        self.status.set("Трек завершён")
        except Exception as e:
            pass

    def update_loop(self):
        self.update_ui()
        self.root.after(500, self.update_loop)

    def on_exit(self):
        try:
            mixer.music.stop()
            mixer.quit()
        except:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AudioPlayerTk(root)
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()


if __name__ == "__main__":
    main()