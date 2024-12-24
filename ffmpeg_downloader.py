import os
import sys
import shutil
import tempfile
import urllib.request
import zipfile

def get_ffmpeg_path():
    """Get or download FFmpeg executable path"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_path = os.path.join(base_path, 'ffmpeg')
    if not os.path.exists(ffmpeg_path):
        os.makedirs(ffmpeg_path, exist_ok=True)
    
    if sys.platform == 'win32':
        ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_exe):
            download_ffmpeg_windows(ffmpeg_path)
        return ffmpeg_path
    else:
        # For Linux/Mac, assume FFmpeg is installed system-wide
        return None

def download_ffmpeg_windows(ffmpeg_path):
    """Download FFmpeg for Windows"""
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    print("Downloading FFmpeg...")
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        urllib.request.urlretrieve(ffmpeg_url, tmp_file.name)
        
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith(('ffmpeg.exe', 'ffprobe.exe')):
                    zip_ref.extract(file, ffmpeg_path)
                    # Move files from nested directory to ffmpeg_path
                    nested_file = os.path.join(ffmpeg_path, file)
                    final_file = os.path.join(ffmpeg_path, os.path.basename(file))
                    shutil.move(nested_file, final_file)
        
        # Clean up nested directories
        for item in os.listdir(ffmpeg_path):
            if os.path.isdir(os.path.join(ffmpeg_path, item)):
                shutil.rmtree(os.path.join(ffmpeg_path, item))
    
    os.unlink(tmp_file.name) 