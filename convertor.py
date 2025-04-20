import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy import VideoFileClip
from pytube import YouTube
import os
from PIL import Image, ImageTk
import threading

class MP4toM4AConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 & YouTube to M4A Converter")
        self.root.geometry("500x400")
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

        # YouTube URL input
        self.url_label = tk.Label(
            self.main_frame,
            text="Enter YouTube URL:",
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
        self.progress_bar.pack_forget()  # Hidden initially

        # Footer
        self.footer = tk.Label(
            self.main_frame,
            text="Made by Rup Sagar Gautam 😉",
            font=("Helvetica", 8),
            bg="#f0f2f5",
            fg="#777"
        )
        self.footer.pack(side="bottom", pady=10)

    def convert_to_m4a(self, video_path, is_youtube=False):
        try:
            self.progress_label.config(text="Converting... Please wait.")
            self.progress_bar.pack()
            self.progress_bar.start()

            # Extract filename and create m4a path
            base = os.path.splitext(video_path)[0]
            m4a_path = base + ".m4a"

            # Load video and extract audio
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                if is_youtube:
                    os.remove(video_path)  # Clean up temporary file
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.progress_label.config(text="")
                messagebox.showerror("Error", "The selected video has no audio track!")
                return
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
                os.remove(video_path)  # Clean up on error
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

    def download_youtube(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return None
        
        try:
            self.progress_label.config(text="Downloading... Please wait.")
            self.progress_bar.pack()
            self.progress_bar.start()

            # Download YouTube video
            yt = YouTube(url)
            # Get the highest quality audio stream (usually mp4 with audio)
            stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
            if not stream:
                stream = yt.streams.filter(file_extension='mp4').first()
                if not stream:
                    raise Exception("No suitable stream found!")
            
            # Download to a temporary file
            temp_file = stream.download(output_path=".", filename="temp_video.mp4")
            
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            return temp_file

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.config(text="")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            return None

    def select_file(self):
        video_path = filedialog.askopenfilename(
            title="Select MP4 Video",
            filetypes=[("MP4 files", "*.mp4")]
        )
        if video_path:
            self.convert_to_m4a(video_path, is_youtube=False)

    def start_conversion_thread(self):
        # Run local file conversion in a separate thread
        threading.Thread(target=self.select_file, daemon=True).start()

    def start_youtube_thread(self):
        # Run YouTube download and conversion in a separate thread
        threading.Thread(target=self.process_youtube, daemon=True).start()

    def process_youtube(self):
        temp_file = self.download_youtube()
        if temp_file:
            self.convert_to_m4a(temp_file, is_youtube=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MP4toM4AConverter(root)
    root.mainloop()