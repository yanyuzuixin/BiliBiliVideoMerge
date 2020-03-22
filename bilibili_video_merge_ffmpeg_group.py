# -*- coding:utf-8 -*- 

import os
import json
import shutil
import natsort
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips

source_paths = [
    r"E:/BiliBiliDownload/49361421",
    r"E:/BiliBiliDownload/89151329",
    r"E:/BiliBiliDownload/91575042",
    r"E:/BiliBiliDownload/92833829",
]
# 在路径下找到指定后缀名的文件(默认文件唯一)，返回文件路径
def _find_file(path, suffix):
    sub_items = os.listdir(path)
    for item in sub_items:
        if os.path.splitext(item)[1] == suffix:
            return f'{path}/{item}'
    return None

# 读取.dvi文件，获取批量下载的多P视频的总标题
def _get_root_folder_name(path):
    dvi_file_path = _find_file(path, '.dvi')
    with open(dvi_file_path, 'r', encoding='utf-8') as f:
        dvi_json = json.load(f)
    return dvi_json['Title']

# 以总标题创建一个文件夹
def create_root_folder(path):
    root_folder_name = _get_root_folder_name(path)
    root_folder_name = root_folder_name.replace(' ', '')
    root_folder_name = root_folder_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    root_folder_name = root_folder_name.replace('*', '_').replace('?', '_').replace('"', '_')
    root_folder_name = root_folder_name.replace('<', '_').replace('>', '_').replace('|', '_')

    path = f'{path}/../{root_folder_name}'
    if os.path.exists(path) == False:
        os.mkdir(path)
    return path

# 读取分P视频原文件夹里的.info文件，获取文件中关键信息
def _read_part_info(path):
    info_file_path = _find_file(path, '.info')
    with open(info_file_path, 'r', encoding='utf-8') as f:
        info_json = json.load(f)
    aid = info_json['Aid']
    part_no = info_json['PartNo']
    part_name = info_json['PartName']
    total_parts = info_json['TotalParts']
    return aid, part_no, part_name, total_parts

def merge_part_video(path,output_path):
    aid, part_no, part_name, total_parts = _read_part_info(path)

    part_name = part_name.replace(' ', '')
    part_name = part_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    part_name = part_name.replace('*', '_').replace('?', '_').replace('"', '_')
    part_name = part_name.replace('<', '_').replace('>', '_').replace('|', '_')

    merge_video_name = f'P{part_no}_{part_name}(AV{aid})'
    part_videos = list()
    for sub_item in os.listdir(path):
        if os.path.splitext(sub_item)[1] == '.flv' or os.path.splitext(sub_item)[1] == '.mp4':
            part_videos.append(f'{path}/{sub_item}')
    if total_parts != len(part_videos):
        print(f'video num error {total_parts} {len(part_videos)}')
        exit('video num error')
    part_videos = natsort.natsorted(part_videos)
    # part_videos.sort()
    video_clips = list()
    video_cnt = 0
    for part_video in part_videos:
        video_cnt += 1
        subprocess.call(f'ffmpeg -i {part_video} -c copy -bsf:v h264_mp4toannexb -f mpegts input{video_cnt}.ts', shell=True)
        video_clips.append(f'input{video_cnt}.ts')


    merge_cmd = '|'.join(video_clips)
    merge_cmd = f'ffmpeg -i "concat:{merge_cmd}" -c copy -bsf:a aac_adtstoasc -movflags +faststart output.mp4'
    subprocess.call(merge_cmd, shell=True)

    final_video_name = f'{merge_video_name}.mp4'
    output_video_path = f'{output_path}/{final_video_name}'

    shutil.copy('output.mp4', output_video_path)

    for tmp in video_clips:
        os.remove(tmp)
    os.remove('output.mp4')
    print(f'{output_video_path} Merge Success!')


if __name__ == "__main__":
    for source_path in source_paths:
        root_folder_path = create_root_folder(source_path)
        for sub_item in natsort.natsorted(os.listdir(source_path)):
            path = f'{source_path}/{sub_item}'
            if os.path.isdir(path):
                merge_part_video(path, root_folder_path)
        print("Merge Finished")
    pass
