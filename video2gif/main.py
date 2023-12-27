import shutil
import subprocess
from math import ceil, floor
from os import startfile
from pathlib import Path

import cv2

print(
    '\n=================================\nConvert video to gif - v8\n================================='
)
while True:
    print('\nPlease drag the video into this window or press Enter to exit:')
    vid = input('>>> ')
    if not vid:
        break

    vid = vid.replace('"', '')
    name = '.'.join(vid.split('/')[-1].split('.')[:-1])

    name_new = name
    count = 1
    while Path(f'{name_new}.gif').exists():
        name_new = f'{name}_{count}'
        count += 1
    name = name_new

    if (temp_path := Path('cv_temp')).exists():
        shutil.rmtree(temp_path)
    temp_path.mkdir()

    # Get video properties
    cap = cv2.VideoCapture(vid)
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    print('--------------------------')
    # FPS and width
    print(f'\nVideo fps is {round(video_fps, 2)}fps')
    print('Select which fps you want to extract from video. If leave blank, extract all')
    if not (vidcustom_fps := input('>>> ')):
        vidcustom_fps = str(video_fps)

    # Extract video
    print('\nExtracting frames...\n')

    subprocess.run(['ffmpeg', '-i', vid, '-r', vidcustom_fps, r'cv_temp/%05d.png'])

    # Manual modify
    modify = 'y'
    while modify.lower() == 'y':
        print('Modify frames? (y/n). Default is no (n)')
        modify = input('>>> ')

        if modify.lower() == 'y':
            startfile(temp_path)

    print('--------------------------')

    ms_list = list(range(2, 1001))
    fps_list = sorted(
        list(set([round(1 / (x * 0.01), 2) for x in ms_list])), reverse=True
    )
    
    print(
        'Please select gif fps: [10, 13, 17, 20, 25, 33, 50] or any number smaller than 10.\nIf leave blank, program will auto choose the closest one to video fps:'
    )
    fps = input('>>> ')

    custom_fps = float(fps) if fps else video_fps
    fps = str(min(fps_list, key=lambda x: abs(float(x) - custom_fps)))

    print(f'GIF fps is {fps}')
    print('--------------------------')
    print(f'\nVideo width is {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}px')
    print(
        'Please select gif width size (px). It cannot be larger than video width.\nIf leave blank, program will choose video width as final.'
    )
    if not (width := input('>>> ')):
        width = str(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))

    print(f'GIF width is {width}px')

    cap.release()
    cv2.destroyAllWindows()

    # Convert to gif by gifski
    print('\nConverting to gif...\n')
    subprocess.run([
        'gifski', 
        '-o', f'{name}.gif', 
        '--fps', fps, 
        '-W', width, 
        '--quality', '100', 
        '--motion-quality', '100',
        '--lossy-quality', '100',
        '--extra',
        'cv_temp/*.png'
    ])
    shutil.rmtree(temp_path)
    print(
        '\n\n--------------------------\nFinish. Enjoy the gif\n--------------------------'
    )
    # input('Enter to exit...')
