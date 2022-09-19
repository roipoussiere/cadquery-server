'AutoScreencast is a tool used to automatically create screencasts by reading instructions.'

import os
import os.path as op
from subprocess import Popen
from datetime import datetime, timedelta
from threading import Thread
from time import sleep, time
from random import random

import pyautogui as ag
import pyperclip


# Changing screen resolution:
#     xrandr --output DP-1 --mode 1440x900
#     xrandr --output DP-1 --mode 1680x1050


class AutoScreencast:
    'Main class of the AutoScreencast tool.'

    keys_interval = 0.1
    text_interval = 0.5

    def __init__(self, video_dir: str):
        self.video_dir = op.abspath(video_dir)

        ag.PAUSE = 0
        file_name_prefix = f"demo_{ datetime.now().strftime('%Y-%m-%d_%H:%M:%S') }"
        self.video_path_prefix = op.join(self.video_dir, file_name_prefix)
        self.proc = None
        self.subtitles = ''
        self.startup = None
        self.sub_counter = 0

    def type(self, text: str, slow=True):
        'type text, with a workaround to support special characters'

        for char in text:
            pyperclip.copy(char)
            ag.hotkey('ctrl', 'shift', 'v')
            if slow:
                sleep(self.keys_interval * random())
                if char == ' ':
                    sleep(self.text_interval * random())

        sleep(self.keys_interval)
        ag.hotkey('enter')
        sleep(self.keys_interval)
        if slow:
            sleep(self.text_interval)

    def screencast(self):
        'function to start screencast using ffmpeg, called in an other thread.'

        str_size = '%dx%d' % ag.size()
        video_path = self.video_path_prefix + '.mp4'
        comand = f'ffmpeg -loglevel error -f x11grab -s { str_size } -r 25 -i :0.0 { video_path }'

        self.proc = Popen(comand.split(' '))

    def init(self):
        'init the screencast'

        if not op.isdir(self.video_dir):
            os.makedirs(self.video_dir)

        daemon = Thread(target=self.screencast, daemon=True)
        daemon.start()
        self.startup = timedelta(seconds=time())

        sleep(1)

    def end(self):
        'exit the screencast properly'

        sleep(0.5)
        self.proc.terminate()
        sleep(0.5)
        ag.hotkey('enter')

        with open(self.video_path_prefix + '.srt', 'w', encoding='utf-8') as sub_file:
            sub_file.write(self.subtitles)

    def move(self, pos: str):
        'move cursor'

        pos_x, pos_y = pos.replace(' ', '').split(',')
        ag.moveTo(int(pos_x), int(pos_y), duration=1.5)

    def keys(self, keys: str):
        'hit keys'

        ag.hotkey(*keys.split('+'))

    def subt(self, text: timedelta):
        'add a subtitle'

        def delta_to_str(delta: str):
            return str(delta)[:-3].replace('.', ',')

        start = timedelta(seconds=time()) - self.startup
        end = start + timedelta(seconds=1)

        self.subtitles += f'{ str(self.sub_counter) }\n'
        self.subtitles += f'{ delta_to_str(start) } --> { delta_to_str(end) }\n'
        self.subtitles += f'{ text }\n\n'
        self.sub_counter += 1

    def read(self, instructions_path: str):
        'read instructions file'

        with open(op.abspath(instructions_path), encoding='utf-8') as md_file:
            try:
                for line in md_file.readlines():
                    line = line.strip('\n')
                    if line == '' or line.startswith('>'):
                        pass
                    if line.startswith('    '):
                        self.type(line[4:])
                    elif line.startswith('- `'):
                        self.keys(line[3:-1])
                    elif line.startswith('- *'):
                        self.move(line[3:-1])
                    else:
                        self.subt(line)
            except Exception as error:
                self.end()
                raise error


sch = AutoScreencast('./screencasts')
sch.init()
sch.read('./screencast.md')
sch.end()
