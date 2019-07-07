import os
import time
import argparse

vlc = '/Applications/VLC.app/Contents/MacOS/VLC'
beep_file = f'file://{os.path.dirname(os.path.abspath(__file__))}/beep.mov'

def beep():
    os.system(f'{vlc} --play-and-exit {beep_file} vlc://quit 2> /dev/null')

time_step = 5

def time_pancake(side1_time, side2_time, flip_time):
    for i, beep_time in enumerate([side1_time, side2_time]):
        threshold = time_step
        start = time.perf_counter()
        while True:
            t = time.perf_counter() - start
            if t > threshold:
                print(int(t))
                threshold += time_step
            if t > beep_time:
                beep()
                break
        if i != 1:
            time.sleep(flip_time)
            print('starting again')

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--side1-time', type=float, default=85)
    parser.add_argument('--side2-time', type=float, default=60)
    parser.add_argument('--flip-time', type=float, default=5)
    parser.add_argument('--repeat-count', type=int, default=1)

    args = parser.parse_args()

    for i in range(0, args.repeat_count):
        time_pancake(args.side1_time, args.side2_time, args.flip_time);
        if i != args.repeat_count - 1:
            input("Press Enter to continue...")
