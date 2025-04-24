import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy import VideoFileClip
import yt_dlp
import os
import re
import sys
import subprocess
from PIL import Image, ImageTk
import threading
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class MP4toM4AConverter:
    def __init__(self, root):
        # Set FFmpeg path relative to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            os.environ["FFMPEG_BINARY"] = ffmpeg_path
        else:
            messagebox.showwarning("FFmpeg Not Found", "FFmpeg is required for conversion. Please ensure ffmpeg.exe is in the script directory.")

        self.root = root
        self.root.title("MP4 & YouTube to M4A Converter")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 10), background="#f0f2f5")

        # Create main frame
        self.main_frame = tk.Frame(root, bg="#f0f2f5")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Header
        self.header = tk.Label(
            self.main_frame,
            text="🎧 MP4 & YouTube to M4A Converter",
            font=("Helvetica", 18, "bold"),
            bg="#f0f2f5",
            fg="#333"
        )
        self.header.pack(pady=(0, 20))

        # URL input
        self.url_label = tk.Label(
            self.main_frame,
            text="Enter Video URL:",
            font=("Helvetica", 10),
            bg="#f0f2f5",
            fg="#555"
        )
        self.url_label.pack()

        self.url_entry = tk.Entry(
            self.main_frame,
            width=50,
            font=("Helvetica", 10)
        )
        self.url_entry.pack(pady=5)

        # Download Video button with hover effect
        self.btn_download_video = tk.Button(
            self.main_frame,
            text="Download Video",
            command=self.start_download_thread,
            font=("Helvetica", 12),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.btn_download_video.pack(pady=10)
        self.btn_download_video.bind("<Enter>", lambda e: self.btn_download_video.config(bg="#F57C00"))
        self.btn_download_video.bind("<Leave>", lambda e: self.btn_download_video.config(bg="#FF9800"))

        # Download & Convert button with hover effect
        self.btn_download = tk.Button(
            self.main_frame,
            text="Download & Convert",
            command=self.start_youtube_thread,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            activebackground="#1e88e5",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.btn_download.pack(pady=10)
        self.btn_download.bind("<Enter>", lambda e: self.btn_download.config(bg="#1e88e5"))
        self.btn_download.bind("<Leave>", lambda e: self.btn_download.config(bg="#2196F3"))

        # File selection button with hover effect
        self.btn_select = tk.Button(
            self.main_frame,
            text="Select Local MP4 File",
            command=self.start_conversion_thread,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.btn_select.pack(pady=10)
        self.btn_select.bind("<Enter>", lambda e: self.btn_select.config(bg="#45a049"))
        self.btn_select.bind("<Leave>", lambda e: self.btn_select.config(bg="#4CAF50"))

        # Progress label
        self.progress_label = tk.Label(
            self.main_frame,
            text="",
            font=("Helvetica", 10),
            bg="#f0f2f5",
            fg="#555"
        )
        self.progress_label.pack(pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            mode="indeterminate",
            length=300
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()

        # Footer
        self.footer = tk.Label(
            self.main_frame,
            text="Made by Rup Sagar Gautam 😉",
            font=("Helvetica", 8),
            bg="#f0f2f5",
            fg="#777"
        )
        self.footer.pack(side="bottom", pady=10)

    def download_from_internet(self):
        """Download a video from the internet using yt-dlp to a user-specified location."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL!")
            return

        # Basic URL validation (ensure it's a valid URL format)
        if not re.match(r'^https?://.+$', url):
            messagebox.showerror("Error", "Invalid URL format!")
            return

        try:
            self.progress_label.config(text="Downloading... Please wait.")
            self.progress_bar.pack()
            self.progress_bar.start()

            # Get default filename from yt-dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                default_filename = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.m4a', '.mp4')

            # Open "Save As" dialog
            save_path = filedialog.asksaveasfilename(
                title="Save Video As",
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
                initialfile=os.path.basename(default_filename),
                initialdir=os.path.dirname(default_filename) if os.path.dirname(default_filename) else os.getcwd()
            )

            if not save_path:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.progress_label.config(text="")
                messagebox.showinfo("Cancelled", "Download cancelled by user.")
                return

            # yt-dlp options for video+audio
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'outtmpl': save_path,
                'quiet': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            messagebox.showinfo("Success", f"Video saved as:\n{save_path}")

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            logging.error(f"Download error: {str(e)}")
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def convert_to_m4a(self, video_path, is_youtube=False):
        """Convert an MP4 file to M4A audio format with user-specified save location."""
        try:
            self.progress_label.config(text="Converting... Please wait.")
            self.progress_bar.pack()
            self.progress_bar.start()

            # Get the base filename (without path or extension) for the default save name
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            default_save_name = f"{base_filename}.m4a"

            # Open "Save As" dialog to let user choose the output path
            m4a_path = filedialog.asksaveasfilename(
                title="Save M4A As",
                defaultextension=".m4a",
                filetypes=[("M4A files", "*.m4a"), ("All files", "*.*")],
                initialfile=default_save_name,
                initialdir=os.path.dirname(video_path)
            )

            # If user cancels the dialog, stop the process
            if not m4a_path:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.progress_label.config(text="")
                if is_youtube:
                    os.remove(video_path)
                messagebox.showinfo("Cancelled", "Conversion cancelled by user.")
                return

            # Load video and extract audio
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                if is_youtube:
                    os.remove(video_path)
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.progress_label.config(text="")
                messagebox.showerror("Error", "The selected video has no audio track!")
                return

            # Extract audio and save to user-specified path
            audio = video.audio
            audio.write_audiofile(m4a_path, codec='aac')

            # Close resources
            audio.close()
            video.close()

            # Clean up temporary file if YouTube download
            if is_youtube:
                os.remove(video_path)

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            messagebox.showinfo("Success", f"Audio saved as:\n{m4a_path}")

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            if is_youtube and os.path.exists(video_path):
                os.remove(video_path)
            logging.error(f"Conversion error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

    def download_youtube(self):
        """Download a YouTube video using yt-dlp."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return None

        # Basic URL validation
        if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/.+$', url):
            messagebox.showerror("Error", "Invalid YouTube URL!")
            return None

        try:
            self.progress_label.config(text="Downloading... Please wait.")
            self.progress_bar.pack()
            self.progress_bar.start()

            # Clean up any existing temp file
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")

            # yt-dlp options for video+audio
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'outtmpl': 'temp_video.mp4',
                'quiet': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            temp_file = "temp_video.mp4"

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            return temp_file

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            logging.error(f"Download error: {str(e)}")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            return None

    def select_file(self):
        """Select a local MP4 file for conversion."""
        video_path = filedialog.askopenfilename(
            title="Select MP4 Video",
            filetypes=[("MP4 files", "*.mp4")]
        )
        if video_path:
            self.convert_to_m4a(video_path, is_youtube=False)

    def start_conversion_thread(self):
        """Run local file conversion in a separate thread."""
        threading.Thread(target=self.select_file, daemon=True).start()

    def start_youtube_thread(self):
        """Run YouTube download and conversion in a separate thread."""
        threading.Thread(target=self.process_youtube, daemon=True).start()

    def start_download_thread(self):
        """Run video download in a separate thread."""
        threading.Thread(target=self.download_from_internet, daemon=True).start()

    def process_youtube(self):
        """Process YouTube video: download and convert to M4A."""
        temp_file = self.download_youtube()
        if temp_file:
            self.convert_to_m4a(temp_file, is_youtube=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MP4toM4AConverter(root)
    root.mainloop()