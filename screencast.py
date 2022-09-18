import os
import os.path as op
from subprocess import Popen
from datetime import datetime, timedelta
from threading import Thread
from time import sleep, time
from random import random

import pyautogui as ag
import pyperclip


ag.PAUSE = 0
KEYS_INTERVAL = 0.1
TEXT_INTERVAL = 0.5
HR_SCREEN_SIZE = (1680, 1050)
LR_SCREEN_SIZE = (1440, 900)
VIDEO_DIR = op.abspath('./screencasts')


class ScreencastHelper:
    def __init__(self):
        file_name_prefix = f"demo_{ datetime.now().strftime('%Y-%m-%d_%H:%M:%S') }"
        self.file_path_prefix = op.join(VIDEO_DIR, file_name_prefix)
        self.proc = None
        self.subtitles = ''
        self.startup = None
        self.sub_counter = 0

    def write_text(self, text: str, slow=True):
        '''workaround to support special characters'''

        for char in text:
            pyperclip.copy(char)
            ag.hotkey('ctrl', 'shift', 'v')
            if slow:
                sleep(KEYS_INTERVAL * random())
                if char == ' ':
                    sleep(TEXT_INTERVAL * random())

        sleep(KEYS_INTERVAL)
        ag.hotkey('enter')
        sleep(KEYS_INTERVAL)
        if slow:
            sleep(TEXT_INTERVAL)

    def screencast(self):
        comand = 'ffmpeg -f x11grab -s %dx%d -r 25 -i :0.0 %s' \
            % (*HR_SCREEN_SIZE, self.file_path_prefix + '.mp4')

        self.proc = Popen(comand.split(' '))

    def start(self):
        if not op.isdir(VIDEO_DIR):
            os.makedirs(VIDEO_DIR)

        daemon = Thread(target=self.screencast, daemon=True)
        daemon.start()
        self.startup = timedelta(seconds=time())

        sleep(1)
        ag.hotkey('ctrl', 'shift', 't')

    def end(self):
        sleep(0.5)
        self.proc.terminate()
        sleep(0.5)
        ag.hotkey('enter')

        sleep(0.5)
        with open(self.file_path_prefix + '.srt', 'w', encoding='utf-8') as sub_file:
            sub_file.write(self.subtitles)

    def subtitle(self, text: str):
        delta_to_str = lambda time: str(time)[:-3].replace('.', ',')

        start = timedelta(seconds=time()) - self.startup
        end = start + timedelta(seconds=1)

        self.subtitles += f'{ str(self.sub_counter) }\n'
        self.subtitles += f'{ delta_to_str(start) } --> { delta_to_str(end) }\n'
        self.subtitles += f'{ text }\n\n'
        self.sub_counter += 1


# if ag.size() == HR_SCREEN_SIZE:
#     write_text('xrandr --output DP-1 --mode %dx%d' % LR_SCREEN_SIZE)
#     sleep(3)


sch = ScreencastHelper()
sch.start()
sch.subtitle('echoing some text')
sch.write_text("echo 'hello world! :)'")
sch.subtitle('moving pointer')
ag.moveTo(200, 200, duration=1.5)
sch.subtitle('echoing some text again')
sch.write_text("echo 'hellooooo'")
ag.hotkey('ctrl', 'shift', 'w')
sch.end()

# write_text('xrandr --output DP-1 --mode %dx%d' % HR_SCREEN_SIZE)
