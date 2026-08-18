import io
import json
import threading
import time
import tkinter as tk
from tkinter import ttk
import urllib.request
from urllib.error import HTTPError, URLError
from PIL import Image, ImageTk

# Offline Fallback Data when Jikan API returns 504 or times out
MOCK_ANIME_DATA = [
    {
        "title": "Frieren: Beyond Journey's End",
        "score": 9.32,
        "episodes": 28,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/1015/138006.jpg"
            }
        },
    },
    {
        "title": "Fullmetal Alchemist: Brotherhood",
        "score": 9.09,
        "episodes": 64,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/1208/94745.jpg"
            }
        },
    },
    {
        "title": "Steins;Gate",
        "score": 9.07,
        "episodes": 24,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/1935/127974.jpg"
            }
        },
    },
    {
        "title": "Bleach: Thousand-Year Blood War",
        "score": 8.90,
        "episodes": 13,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/1908/135431.jpg"
            }
        },
    },
    {
        "title": "Hunter x Hunter (2011)",
        "score": 9.04,
        "episodes": 148,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/1337/99013.jpg"
            }
        },
    },
    {
        "title": "Gintama°",
        "score": 9.06,
        "episodes": 51,
        "images": {
            "jpg": {
                "image_url": "https://cdn.myanimelist.net/images/anime/3/72078.jpg"
            }
        },
    },
]


class AnimeCard(tk.Frame):
    """Interactive visual card with image, badges, progress bar, and hover effects."""

    def __init__(self, parent, anime_data, rank, *args, **kwargs):
        super().__init__(
            parent,
            bg="#252526",
            highlightthickness=1,
            highlightbackground="#3A3A3C",
            padx=10,
            pady=10,
            *args,
            **kwargs,
        )
        self.anime = anime_data
        self.rank = rank

        # Hover Bindings
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

        # 1. Badge Header
        self.badge_frame = tk.Frame(self, bg="#252526")
        self.badge_frame.pack(fill="x", pady=(0, 8))

        badge_text = f"🔥 TOP #{self.rank}" if self.rank <= 3 else f"★ #{self.rank}"
        badge_bg = "#E81123" if self.rank <= 3 else "#007ACC"

        self.badge = tk.Label(
            self.badge_frame,
            text=badge_text,
            bg=badge_bg,
            fg="white",
            font=("Segoe UI", 7, "bold"),
            padx=6,
            pady=2,
        )
        self.badge.pack(side="left")

        score_val = self.anime.get("score", "N/A")
        self.score_label = tk.Label(
            self.badge_frame,
            text=f"Score: {score_val}",
            bg="#252526",
            fg="#FFD700",
            font=("Segoe UI", 8, "bold"),
        )
        self.score_label.pack(side="right")

        # 2. Media Poster Placeholder
        self.poster_label = tk.Label(
            self,
            text="[ Loading Image... ]",
            bg="#1E1E1E",
            fg="#777777",
            width=22,
            height=9,
            font=("Segoe UI", 8, "italic"),
        )
        self.poster_label.pack(fill="x", pady=5)

        # 3. Title & Info
        title_text = self.anime.get("title", "Unknown")
        if len(title_text) > 28:
            title_text = title_text[:25] + "..."

        self.title_lbl = tk.Label(
            self,
            text=title_text,
            bg="#252526",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill="x", pady=(5, 2))

        episodes = self.anime.get("episodes") or 12
        self.ep_lbl = tk.Label(
            self,
            text=f"Episodes: {episodes} total",
            bg="#252526",
            fg="#AAAAAA",
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.ep_lbl.pack(fill="x")

        # 4. Progress Indicator
        self.progress_frame = tk.Frame(self, bg="#252526")
        self.progress_frame.pack(fill="x", pady=(8, 0))

        self.progress_lbl = tk.Label(
            self.progress_frame,
            text="Watch Status",
            bg="#252526",
            fg="#888888",
            font=("Segoe UI", 7),
        )
        self.progress_lbl.pack(anchor="w")

        self.progress = ttk.Progressbar(
            self.progress_frame, length=100, mode="determinate"
        )
        self.progress.pack(fill="x", pady=(2, 0))
        self.progress["value"] = (self.rank * 18) % 100

        # Async Image Loader
        img_url = self.anime.get("images", {}).get("jpg", {}).get("image_url")
        if img_url:
            threading.Thread(
                target=self.load_image, args=(img_url, self.rank), daemon=True
            ).start()

    def load_image(self, url, rank):
        try:
            time.sleep(rank * 0.2)  # Short delay to prevent server flooding
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                raw_data = resp.read()

            image = Image.open(io.BytesIO(raw_data))
            image = image.resize((160, 200), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)

            self.poster_label.config(image=self.photo, text="", bg="#252526")
        except Exception:
            self.poster_label.config(text="[ Image Offline ]")

    def on_hover(self, event):
        self.config(highlightbackground="#007ACC", bg="#2D2D30")
        self.badge_frame.config(bg="#2D2D30")
        self.title_lbl.config(bg="#2D2D30")
        self.score_label.config(bg="#2D2D30")
        self.ep_lbl.config(bg="#2D2D30")
        self.progress_frame.config(bg="#2D2D30")

    def on_leave(self, event):
        self.config(highlightbackground="#3A3A3C", bg="#252526")
        self.badge_frame.config(bg="#252526")
        self.title_lbl.config(bg="#252526")
        self.score_label.config(bg="#252526")
        self.ep_lbl.config(bg="#252526")
        self.progress_frame.config(bg="#252526")


class InteractiveGridApp:

    def __init__(self, root):
        self.root = root
        self.root.geometry("980x680")
        self.root.configure(bg="#1E1E1E")
        self.root.overrideredirect(True)

        # Title Bar
        self.title_bar = tk.Frame(self.root, bg="#2D2D2D", height=32)
        self.title_bar.pack(fill="x", side="top")

        self.title_lbl = tk.Label(
            self.title_bar,
            text=" ⛩️ Anime Network - Visual Grid Explorer",
            bg="#2D2D2D",
            fg="white",
            font=("Segoe UI", 9, "bold"),
        )
        self.title_lbl.pack(side="left", padx=10)

        self.close_btn = tk.Button(
            self.title_bar,
            text="✕",
            command=self.root.destroy,
            bg="#2D2D2D",
            fg="white",
            bd=0,
            width=4,
            activebackground="#E81123",
        )
        self.close_btn.pack(side="right", fill="y")

        # Workspace Container
        self.main_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        self.top_bar = tk.Frame(self.main_frame, bg="#1E1E1E")
        self.top_bar.pack(fill="x", pady=(0, 5))

        self.header = tk.Label(
            self.top_bar,
            text="Trending Anime Showcase",
            bg="#1E1E1E",
            fg="white",
            font=("Segoe UI", 16, "bold"),
        )
        self.header.pack(side="left")

        self.load_btn = tk.Button(
            self.top_bar,
            text="🔄 Load Live Media Grid",
            command=self.load_grid,
            bg="#007ACC",
            fg="white",
            bd=0,
            padx=12,
            pady=5,
            font=("Segoe UI", 9, "bold"),
        )
        self.load_btn.pack(side="right")

        # Network Status Banner
        self.status_lbl = tk.Label(
            self.main_frame,
            text="Ready to load anime feed...",
            bg="#1E1E1E",
            fg="#AAAAAA",
            font=("Segoe UI", 8, "italic"),
        )
        self.status_lbl.pack(anchor="w", pady=(0, 10))

        # Scrollable Canvas
        self.canvas = tk.Canvas(
            self.main_frame, bg="#1E1E1E", bd=0, highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient="vertical", command=self.canvas.yview
        )
        self.grid_frame = tk.Frame(self.canvas, bg="#1E1E1E")

        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", expand=True, fill="both")
        self.scrollbar.pack(side="right", fill="y")

        # Load grid automatically on open
        self.load_grid()

    def load_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.status_lbl.config(
            text="⏳ Connecting to Jikan API server...", fg="#FFD700"
        )
        threading.Thread(target=self.fetch_and_build, daemon=True).start()

    def fetch_and_build(self):
        url = "https://api.jikan.moe/v4/top/anime?limit=6"
        data = []

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode()).get("data", [])

            self.root.after(
                0,
                lambda: self.status_lbl.config(
                    text="🟢 Live API Connected!", fg="#28A745"
                ),
            )
        except Exception as e:
            # Server timed out (504) or rate-limited (429) -> Switch to Mock Data
            data = MOCK_ANIME_DATA
            self.root.after(
                0,
                lambda: self.status_lbl.config(
                    text="⚡ Jikan API 504 Timeout: Loaded Offline Cached Cards",
                    fg="#E81123",
                ),
            )

        # Render Cards
        for index, item in enumerate(data):
            row = index // 3
            col = index % 3
            self.root.after(
                10,
                lambda anime=item, r=index + 1, rw=row, cl=col: self.create_card(
                    anime, r, rw, cl
                ),
            )

    def create_card(self, anime, rank, row, col):
        card = AnimeCard(self.grid_frame, anime_data=anime, rank=rank)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")


if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveGridApp(root)
    root.mainloop()
