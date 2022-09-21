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


# Exit script: slam the cursor into a corner
# Changing screen resolution before and after recording (better visibility):
#     xrandr --output DP-1 --mode 1440x900
#     xrandr --output DP-1 --mode 1680x1050


class AutoScreencast:
    'Main class of the AutoScreencast tool.'

    def __init__(self, video_dir: str, prefix: str):
        self.video_dir = op.abspath(video_dir)

        ag.PAUSE = 0.3
        file_name_prefix = f"{ prefix }_{ datetime.now().strftime('%Y-%m-%d_%H:%M:%S') }"
        self.video_path_prefix = op.join(self.video_dir, file_name_prefix)
        self.proc = None
        self.subtitles = ''
        self.startup = None
        self.sub_counter = 0

    def type(self, text: str, slow=True):
        'type text, with a workaround to support special characters'

        pause = ag.PAUSE
        ag.PAUSE = 0
        for char in text:
            pyperclip.copy(char)
            ag.hotkey('ctrl', 'shift', 'v')
            if slow:
                sleep((pause if char == ' ' else ag.MINIMUM_DURATION) * random())

        ag.PAUSE = pause
        ag.hotkey('enter')
        sleep(pause)

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
        'exit the screencast properly and write subtitles'

        sleep(1)
        self.proc.terminate()

        with open(self.video_path_prefix + '.srt', 'w', encoding='utf-8') as sub_file:
            sub_file.write(self.subtitles)

    def move(self, pos: str):
        'move cursor'

        pos_x, pos_y = pos.replace(' ', '').split(',')
        ag.moveTo(int(pos_x), int(pos_y), 1, ag.easeOutQuad)

    def click(self, pos: str=''):
        'mouse click'

        if pos:
            self.move(pos)
        ag.click()

    def drag(self, pos: str):
        'click then move cursor'

        pos_x, pos_y = pos.replace(' ', '').split(',')
        ag.dragTo(int(pos_x), int(pos_y), 1, ag.easeOutQuad)

    def keys(self, keys: str):
        'hit keys'

        for key in keys.replace(' ', '').split(','):
            ag.hotkey(*key.split('+'))

        sleep(ag.PAUSE)

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
                    if line == '' or line.startswith('<!--'):
                        pass
                    if line.startswith('    '):
                        self.type(line[4:])
                    elif line.startswith('__`'):
                        self.keys(line[3:-3])
                    elif line.startswith('---'):
                        sleep(0.5 * (len(line) - 2))
                    elif line.startswith('> move to '):
                        self.move(line[10:])
                    elif line.startswith('> click to '):
                        self.click(line[11:])
                    elif line.startswith('> click'):
                        self.click()
                    elif line.startswith('> drag to '):
                        self.drag(line[10:])
                    elif line.startswith('>'):
                        pass
                    else:
                        self.subt(line)
            except Exception as error:
                self.end()
                raise error


sch = AutoScreencast('./screencasts', 'demo')
sch.init()
sch.read('./tools/screencast.md')
sch.end()
