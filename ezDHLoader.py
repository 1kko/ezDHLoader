import PySimpleGUI as sg
import pafy
from urllib.parse import urlparse, parse_qs
import time
import random
import configparser


def output_callback(total, recvd, ratio, rate, eta):
    global progress_bar
    try:
        # print(recvd, ratio, eta)
        progress_bar.UpdateBar(ratio)
        etaText = window['eta']
        etaText.update("ETA: " + str(eta) + "s")
    except:
        pass


if __name__ == "__main__":
    with_apikey = ""
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config['DEFAULT']['YOUTUBE_API_KEY'] not in [None, '']:
            pafy.set_api_key(config['DEFAULT']['YOUTUBE_API_KEY'])
            with_apikey = " (API Key Enabled)"
    except:
        pass

    layout = [
        [sg.Text("Youtube URL:")],
        [sg.InputText(size=(80, 20), key='url')],
        [sg.Submit("OK"), sg.Cancel()],
        [sg.ProgressBar(1, orientation='h', size=(
            45, 5), key='progressbar'),
         sg.Text(size=(12, 1), key='eta', justification='r')]
        # [sg.Output(size=(80, 20))],
    ]

    window = sg.Window('ezDHLoader v0.5' + with_apikey, layout)
    progress_bar = window['progressbar']

    youtubeId = ""
    event, values = window.read()
    url = values['url']

    try:
        if url.startswith("http"):
            res = urlparse(url)
            if res.netloc == "www.youtube.com" or res.netloc == "youtube.com":
                # Url starts with www.youtube.com
                youtubeId = parse_qs(res.query)['v'][0]

            if res.netloc == "youtu.be":
                # Url starts with youtu.be
                youtubeId = res.path[1:]

        # download
        y = pafy.new(youtubeId)
        video = y.getbest()
        vfilename = video.download(
            quiet=True, callback=output_callback, remux_audio=True)

        sg.Popup("Done")

    except Exception as e:
        sg.Popup("Oops", e)
