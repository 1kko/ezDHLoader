import PySimpleGUI as sg
from urllib.parse import urlparse, parse_qs
import os
import logging
import yt_dlp

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def progress_hook(d):
    global progress_bar, window
    try:
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total_bytes:
                downloaded = d.get('downloaded_bytes', 0)
                ratio = downloaded / total_bytes
                progress_bar.UpdateBar(ratio)
                eta = d.get('eta', 0)
                window['eta'].update(f"ETA: {eta}s")
    except Exception as e:
        logger.error(f"Error in callback: {e}")

if __name__ == "__main__":
    layout = [
        [sg.Text("Youtube URL:")],
        [sg.InputText(size=(80, 20), key='url')],
        [sg.Submit("OK"), sg.Cancel()],
        [sg.ProgressBar(1, orientation='h', size=(
            45, 5), key='progressbar'),
         sg.Text(size=(12, 1), key='eta', justification='r')],
        [sg.Text("Destination", size=(15, 1)), sg.InputText(os.getcwd(),
                                                            key='dstPath'), sg.FolderBrowse()],
    ]

    window = sg.Window('ezDHLoader v0.9', layout)
    progress_bar = window['progressbar']

    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
            
        if event == 'OK':
            url = values['url']
            try:
                logger.debug(f"Processing URL: {url}")
                
                ydl_opts = {
                    'format': 'best',
                    'progress_hooks': [progress_hook],
                    'outtmpl': os.path.join(values['dstPath'], '%(title)s.%(ext)s'),
                    'verbose': True
                }
                
                logger.debug("Starting download...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                sg.Popup("Done")
                window['url'].update('')
                progress_bar.UpdateBar(0)
                window['eta'].update('')

            except Exception as e:
                logger.exception("Download failed")
                sg.Popup("Oops", f"Error: {str(e)}\nCheck the console for detailed logs.")

    window.close()
