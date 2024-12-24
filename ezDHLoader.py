import logging
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import yt_dlp
import ffmpeg_downloader

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ezDHLoader v0.8')
        self.root.geometry('800x200')
        
        self.ffmpeg_path = ffmpeg_downloader.get_ffmpeg_path()
        
        # URL Frame
        url_frame = ttk.Frame(root, padding="10")
        url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(url_frame, text="Youtube URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Destination Frame
        dest_frame = ttk.Frame(root, padding="10")
        dest_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(dest_frame, text="Destination:").grid(row=0, column=0, sticky=tk.W)
        self.dest_entry = ttk.Entry(dest_frame, width=70)
        self.dest_entry.insert(0, os.getcwd())
        self.dest_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(dest_frame, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=5)
        
        # Progress Frame
        progress_frame = ttk.Frame(root, padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=600, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.eta_label = ttk.Label(progress_frame, text="ETA: --")
        self.eta_label.grid(row=0, column=1, padx=5)
        
        # Button Frame
        button_frame = ttk.Frame(root, padding="10")
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel Download", command=self.cancel_download, state='disabled')
        self.cancel_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=root.quit).grid(row=0, column=2, padx=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)

    def progress_hook(self, d):
        try:
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total_bytes:
                    downloaded = d.get('downloaded_bytes', 0)
                    ratio = (downloaded / total_bytes) * 100
                    eta = d.get('eta', 0)
                    self.progress_var.set(ratio)
                    self.eta_label.config(text=f"ETA: {eta}s")
                    self.root.update_idletasks()
        except Exception as e:
            logger.error(f"Error in callback: {e}")

    def download(self):
        try:
            url = self.url_entry.get()
            if not url:
                messagebox.showwarning("Warning", "Please enter a URL")
                return
            
            self.is_downloading = True
            self.download_btn.config(state='disabled')
            self.cancel_btn.config(state='normal')
            
            logger.debug(f"Processing URL: {url}")
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.dest_entry.get(), '%(title)s.%(ext)s'),
                'verbose': True,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }, {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }],
                'prefer_ffmpeg': True,
                'keepvideo': False
            }

            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

            logger.debug("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.current_download = ydl
                if not self.is_downloading:
                    return
                ydl.download([url])

            if self.is_downloading:
                self.root.after(0, self.reset_ui, True)

        except Exception as e:
            logger.exception("Download failed")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            self.root.after(0, self.reset_ui, False)

    def cancel_download(self):
        if self.is_downloading:
            self.is_downloading = False
            if self.current_download:
                self.current_download._download_retcode = 1  # Signal yt-dlp to stop
            self.root.after(0, self.reset_ui, False)

    def reset_ui(self, show_success=False):
        """Reset UI elements after download"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.focus()
        self.progress_var.set(0)
        self.eta_label.config(text="ETA: --")
        self.download_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.is_downloading = False
        self.current_download = None
        
        if show_success:
            messagebox.showinfo("Success", "Download completed!")

    def start_download(self):
        # Run download in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
