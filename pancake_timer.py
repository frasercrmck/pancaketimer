import os
import sys
import time
import argparse
import platform
import subprocess
from enum import Enum

# This is silly
system = platform.system()
if system == 'Linux':
    vlc = 'cvlc'
elif system == 'Darwin':
    vlc= '/Applications/VLC.app/Contents/MacOS/VLC'
else:
    sys.stderr.write(f"Could not identify platform '{system}': "
                      "(only supports 'Linux' or 'Darwin')\n")
    sys.exit(1)

beep_file = f'file://{os.path.dirname(os.path.abspath(__file__))}/beep.mov'

def beep():
    os.system(f'{vlc} --play-and-exit {beep_file} vlc://quit 2> /dev/null')

time_step = 1
BAR_CHAR = '='
SPACE_CHAR = ' '


class Colour(Enum):
    GREEN = 32   # First: default value
    RED = 31
    YELLOW = 33


def get_progress_bar(bar_width, total_width, text):
    # Brutally truncate and strings that are too long
    text = text[:total_width]
    text_len = len(text)
    bar_width = int(bar_width)
    half_width = int(float(total_width) / 2)
    half_text_len_lhs = int(text_len / 2)
    half_text_len_rhs = text_len - half_text_len_lhs
    bar_lhs = min(half_width - half_text_len_lhs, bar_width)
    bar_rhs = max(0, bar_width - half_width - half_text_len_rhs)
    spacing_lhs = half_width - half_text_len_lhs - bar_lhs
    spacing_rhs = total_width - bar_rhs - half_width - half_text_len_rhs
    return f"{BAR_CHAR * bar_lhs}{SPACE_CHAR * spacing_lhs}" \
           f"{text}" \
           f"{BAR_CHAR * bar_rhs}{SPACE_CHAR * spacing_rhs}"


def write_progress_bar(bar_width, total_width, text, colour):
    sys.stdout.write(u"\u001b[1000D{b0}\u001b[{fgc}m{bar}\u001b[0m{b1}".format(
        bar=get_progress_bar(bar_width, total_width, text),
        b0='[', b1=']', fgc=colour.value
        )
    )
    sys.stdout.flush()


def time_side(beep_time, colour, total_width):
    threshold = 0

    bar_fill = total_width
    step = float(total_width) / beep_time

    t = 0
    start = time.perf_counter()
    while t <= beep_time:
        t = time.perf_counter() - start
        if t >= threshold:
            write_progress_bar(bar_fill, total_width,
                               '{0:>2}/{1}'.format(
                                   int(beep_time) - int(t), int(beep_time)),
                               colour)
            bar_fill -= step
            threshold += time_step


def time_pancake(side1_time, side2_time, flip_time, tty_width, colour):
    total_width = int(tty_width - 2)
    time_side(side1_time, colour, total_width)
    write_progress_bar(0, total_width, "FLIP FLIP FLIP!", colour)
    beep()
    time.sleep(flip_time)
    time_side(side2_time, colour, total_width)


def main():
    colour_choices = [str(v.name.lower()) for v in Colour]

    parser = argparse.ArgumentParser(description='')

    modes = {
            'crepe'   : [80, 40, 10],
            'pancake' : [85, 60, 5],
    }

    parser.add_argument('--side1-time', type=float, default=85)
    parser.add_argument('--side2-time', type=float, default=60)
    parser.add_argument('--flip-time', type=float, default=5)
    parser.add_argument('--repeat-count', type=int, default=1)
    parser.add_argument('--colour', choices=colour_choices,
                        default=colour_choices[0])
    parser.add_argument('--mode', choices=modes.keys(),
            help="Sets (and overwrites) side1/side2/flip values:\n"
                 "{0}".format([[k, vals] for k,vals in modes.items()]))


    args = parser.parse_args()
    args.colour = Colour[args.colour.upper()]

    if args.mode in modes:
        args.side1_time, args.side2_time, args.flip_time =\
                modes[args.mode]

    _, columns = subprocess.check_output(['stty', 'size']).decode().split()

    for i in range(0, args.repeat_count):
        time_pancake(args.side1_time, args.side2_time,
                     args.flip_time, tty_width=int(columns),
                     colour=args.colour)
        if i != args.repeat_count - 1:
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write("Enjoy your pancakes!\n")
        sys.exit(0)
