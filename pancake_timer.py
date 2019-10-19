import os
import sys
import time
import argparse
import subprocess

vlc = '/Applications/VLC.app/Contents/MacOS/VLC'
beep_file = f'file://{os.path.dirname(os.path.abspath(__file__))}/beep.mov'

def beep():
    os.system(f'{vlc} --play-and-exit {beep_file} vlc://quit 2> /dev/null')

time_step = 1
BAR_CHAR = '='
SPACE_CHAR = ' '

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


def write_progress_bar(bar_width, total_width, text):
    sys.stdout.write(u"\u001b[1000D{b0}\u001b[32m{bar}\u001b[0m{b1}".format(
        bar=get_progress_bar(bar_width, total_width, text),
        b0='[', b1=']'
        )
    )
    sys.stdout.flush()

def time_pancake(side1_time, side2_time, flip_time, tty_width):
    total_width = int(tty_width - 2)
    for i, beep_time in enumerate([side1_time, side2_time]):
        threshold = time_step

        bar_fill = total_width
        step = float(total_width) / beep_time

        write_progress_bar(total_width, total_width,
                           '{0:>2}/{0}'.format(int(beep_time)))

        start = time.perf_counter()
        while True:
            t = time.perf_counter() - start
            if t > threshold:
                bar_fill -= step
                threshold += time_step
                write_progress_bar(bar_fill, total_width,
                                   '{0:>2}/{1}'.format(
                                       int(beep_time - t + 1), int(beep_time)))
            if t > beep_time:
                write_progress_bar(bar_fill, total_width, "FLIP FLIP FLIP!")
                beep()
                break
        if i != 1:
            time.sleep(flip_time)

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--side1-time', type=float, default=85)
    parser.add_argument('--side2-time', type=float, default=60)
    parser.add_argument('--flip-time', type=float, default=5)
    parser.add_argument('--repeat-count', type=int, default=1)

    args = parser.parse_args()

    _, columns = subprocess.check_output(['stty', 'size']).decode().split()

    for i in range(0, args.repeat_count):
        time_pancake(args.side1_time, args.side2_time,
                     args.flip_time, tty_width=int(columns));
        if i != args.repeat_count - 1:
            input("Press Enter to continue...")
