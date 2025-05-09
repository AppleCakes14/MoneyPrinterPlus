#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#
#

import itertools
import os
import random
import subprocess
from datetime import timedelta

import streamlit as st

from services.captioning.captioning_service import add_subtitles
from services.hunjian.hunjian_service import get_session_video_scene_text, get_video_scene_text_list
from services.video.texiao_service import gen_filter
from services.video.video_service import DEFAULT_DURATION, get_image_info, get_video_duration, get_video_info, \
    get_video_length_list, add_background_music
from tools.file_utils import generate_temp_filename
from tools.tr_utils import tr
from tools.utils import run_ffmpeg_command, random_with_system_time

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)
# 视频出目录
video_output_dir = os.path.join(script_dir, "../../final")
video_output_dir = os.path.abspath(video_output_dir)

# work目录
work_output_dir = os.path.join(script_dir, "../../work")
work_output_dir = os.path.abspath(work_output_dir)


def merge_generate_subtitle(video_scene_video_list, video_scene_text_list):
    enable_subtitles = st.session_state.get("enable_subtitles")
    if enable_subtitles and video_scene_text_list is not None:
        st.write(tr("Add Subtitles..."))
        for video_file, scene_text in zip(video_scene_video_list, video_scene_text_list):
            if scene_text is not None and scene_text != "":
                generate_subtitles(video_file, scene_text)


def generate_subtitles(video_file, scene_text):
    # 获取视频时长
    video_duration = get_video_duration(video_file)
    # 生成字幕文件
    # 设置输出字幕
    random_name = random_with_system_time()
    captioning_output = os.path.join(work_output_dir, f"{random_name}.srt")
    subtitle_file = generate_temp_filename(captioning_output)
    gen_subtitle_file(subtitle_file, scene_text, video_duration)
    # 添加字幕

    font_name = st.session_state.get('subtitle_font')
    font_size = st.session_state.get('subtitle_font_size')
    primary_colour = st.session_state.get('subtitle_color')
    outline_colour = st.session_state.get('subtitle_border_color')
    outline = st.session_state.get('subtitle_border_width')
    alignment = st.session_state.get('subtitle_position')
    add_subtitles(video_file, subtitle_file,
                  font_name=font_name,
                  font_size=font_size,
                  primary_colour=primary_colour,
                  outline_colour=outline_colour,
                  outline=outline,
                  alignment=alignment)
    print("file with subtitle:", video_file)


def format_time(seconds):
    """格式化时间为 SRT 字幕格式"""
    time = str(timedelta(seconds=seconds))
    if '.' in time:
        time, milliseconds = time.split('.')
        milliseconds = int(milliseconds) * 1000
    else:
        milliseconds = 0
    return f"{time},000" if milliseconds == 0 else f"{time},{milliseconds:03d}"

# def format_time(seconds):
#     """Format time in seconds to SRT format (HH:MM:SS,mmm)"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = seconds % 60
#     milliseconds = int((seconds - int(seconds)) * 1000)
#     return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


def gen_subtitle_file(subtitle_file, scene_text, video_duration):
    """生成 SRT 字幕文件"""
    start_time = 0
    end_time = video_duration

    with open(subtitle_file, 'w', encoding='utf-8') as file:
        file.write("1\n")
        file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
        file.write(f"{scene_text}\n")
        file.write("\n")


def merge_get_video_list():
    print("merge_get_video_list begin")
    video_dir_list, video_text_list = get_session_video_scene_text()
    video_scene_text_list =[]
    if video_text_list is not None:
        video_scene_text_list = get_video_scene_text_list(video_text_list)
    # video_scene_video_list = get_video_scene_video_list(video_dir_list)
    return get_video_scene_video_list(video_dir_list), video_scene_text_list


def get_video_scene_video_list(video_dir_list):
    video_scene_video_list = []
    for video_dir in video_dir_list:
        if video_dir is not None:
            # video_file = random_video_from_dir(video_dir)
            video_files = get_all_videos_from_dir(video_dir)
            # video_scene_video_list.append(video_files)
            video_scene_video_list = video_files
    return video_scene_video_list


def random_video_from_dir(video_dir):
    # 获取媒体文件夹中的所有图片和视频文件
    media_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if
                   f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]

    # Get any existing video files
    video_files = [f for f in media_files if f.lower().endswith(('.mp4', '.mov'))]
    
    # Convert image files to video if needed
    if not video_files:
        image_files = [f for f in media_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if image_files:
            # Random select an image to convert
            image_file = random.choice(image_files)
            
            # Convert image to video
            fps = st.session_state.get("video_fps", 30)
            target_width, target_height = st.session_state.get("video_size", "1920x1080").split('x')
            target_width, target_height = int(target_width), int(target_height)
            
            # Create a temporary video file
            output_name = generate_temp_filename(image_file, ".mp4", work_output_dir)
            
            # Within random_video_from_dir function
            ffmpeg_cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', image_file,
                '-t', str(DEFAULT_DURATION),
                '-r', str(fps),
                '-c:v', 'libx264',
                '-filter_complex',
                f"[0:v]scale={target_width}:{target_height},boxblur=10:1[bg];"
                f"[0:v]scale=w={target_width}:h={target_height}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2",
                '-y', output_name
            ]
            print(" ".join(ffmpeg_cmd))
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Add audio to the video (Silent audio)
            output_with_audio = output_name.replace(".mp4", "_audio.mp4")
            add_audio_cmd = [
                'ffmpeg',
                '-i', output_name,                     # input video without audio
                '-f', 'lavfi',                         # use lavfi to generate audio
                '-t', str(DEFAULT_DURATION),           # match video duration
                '-i', 'anullsrc=r=44100:cl=stereo',    # generate silent audio
                '-c:v', 'copy',                        # copy video stream as-is
                '-c:a', 'aac',                         # encode audio in AAC
                '-shortest',                           # cut audio if longer than video
                '-y', output_with_audio                # output file with audio
            ]
            print(" ".join(add_audio_cmd))
            subprocess.run(add_audio_cmd, check=True, capture_output=True)

            # Replace output_name with the new file that includes audio
            output_name = output_with_audio
            return output_name
    
    # If we have video files, choose one randomly
    if video_files:
        return random.choice(video_files)
    else:
        # Should not reach here if conversion worked
        return random.choice(media_files)

def get_all_videos_from_dir(video_dir):
    """Get all media files from directory and convert images to videos if needed"""
    # Get all media files from directory
    media_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if
                  f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]
    
    processed_files = []
    
    # Process each file
    for media_file in media_files:
        if media_file.lower().endswith(('.mp4', '.mov')):
            # Check if video needs fps conversion
            fps = st.session_state.get("video_fps", 30)
            video_width, video_height = get_video_info(media_file)
            # Generate output filename for the processed video
            output_name = generate_temp_filename(media_file, new_directory=work_output_dir)
            
            # Convert video to target fps
            if video_width / video_height > target_width / target_height:
                # Landscape video - blurred background
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', media_file,  # 输入文件
                    '-r', str(fps),  # 设置帧率
                    '-an',  # 去除音频
                    '-vf',
                    f"split[original][blur];[blur]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=20:5[blurred];"
                    f"[original]scale={target_width}:-1:force_original_aspect_ratio=1[scaled];"
                    f"[scaled]crop='if(gte(in_w,{target_width}),{target_width},in_w)':'if(gte(in_h,{target_height}),{target_height},in_h)':(in_w-{target_width})/2:(in_h-{target_height})/2[cropped];"
                    f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                    '-y',
                    output_name
                ]
            else:
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', media_file,  # 输入文件
                    '-r', str(fps),  # 设置帧率
                    '-an',  # 去除音频
                    '-vf',
                    f"split[original][blur];[blur]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=20:5[blurred];"
                    f"[original]scale=-1:{target_height}:force_original_aspect_ratio=1[scaled];"
                    f"[scaled]crop='if(gte(in_w,{target_width}),{target_width},in_w)':'if(gte(in_h,{target_height}),{target_height},in_h)':"
                    f"(in_w-{target_width})/2:(in_h-{target_height})/2[cropped];"
                    f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                    '-y',
                    output_name
                ]

            
            print(" ".join(ffmpeg_cmd))
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            
            output_with_audio = output_name.replace(".mp4", "_audio.mp4")
            add_audio_cmd = [
                'ffmpeg',
                '-i', output_name,
                '-f', 'lavfi',
                '-t', str(DEFAULT_DURATION),
                '-i', 'anullsrc=r=44100:cl=stereo',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y', output_with_audio
            ]
            print(" ".join(add_audio_cmd))
            subprocess.run(add_audio_cmd, check=True, capture_output=True)
            
            processed_files.append(output_with_audio)

            # Add the fps-normalized video to the list
            # processed_files.append(output_name)
        else:
            # Convert images to videos
            fps = st.session_state.get("video_fps", 30)
            target_width, target_height = st.session_state.get("video_size", "1920x1080").split('x')
            target_width, target_height = int(target_width), int(target_height)
            img_width, img_height = get_image_info(media_file)
            # Create a temporary video file
            output_name = generate_temp_filename(media_file, ".mp4", work_output_dir)
            
            if img_height >= img_width:
                # Portrait image with background
                # Convert image to video
                ffmpeg_cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', media_file,
                '-t', str(DEFAULT_DURATION),
                '-r', str(fps),
                '-c:v', 'libx264',
                '-vf',
                f"split[original][blur];"
                f"[blur]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=20:5[blurred];"  # Create a blurred background
                f"[original]scale=-1:{target_height}:force_original_aspect_ratio=1[scaled];"  # Resize the portrait to fit the target height
                f"[blurred][scaled]overlay=(W-w)/2:(H-h)/2,format=yuv420p",  # Center the portrait on the blurred background
                '-y', output_name
                ]
            else:
                # Landscape image - blurred background
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-loop', '1',
                    '-i', media_file,
                    '-t', str(DEFAULT_DURATION),
                    '-r', str(fps),
                    '-c:v', 'libx264',
                    '-vf',
                    f"split[original][blur];"
                    f"[blur]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=20:5[blurred];"
                    f"[original]scale={target_width}:-1:force_original_aspect_ratio=1[scaled];"
                    f"[scaled]crop='if(gte(in_w,{target_width}),{target_width},in_w)':'if(gte(in_h,{target_height}),{target_height},in_h)':(in_w-{target_width})/2:(in_h-{target_height})/2[cropped];"
                    f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                    '-y', output_name
                ]
            print(" ".join(ffmpeg_cmd))
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Add audio to the video (silent audio)
            output_with_audio = output_name.replace(".mp4", "_audio.mp4")
            add_audio_cmd = [
                'ffmpeg',
                '-i', output_name,
                '-f', 'lavfi',
                '-t', str(DEFAULT_DURATION),
                '-i', 'anullsrc=r=44100:cl=stereo',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y', output_with_audio
            ]
            print(" ".join(add_audio_cmd))
            subprocess.run(add_audio_cmd, check=True, capture_output=True)
            
            processed_files.append(output_with_audio)
    
    return processed_files

class VideoMergeService:
    def __init__(self, video_list):
        self.video_list = video_list
        self.fps = st.session_state["video_fps"]
        self.target_width, self.target_height = st.session_state["video_size"].split('x')
        self.target_width = int(self.target_width)
        self.target_height = int(self.target_height)

        self.enable_background_music = st.session_state["enable_background_music"]
        self.background_music = st.session_state["background_music"]
        self.background_music_volume = st.session_state["background_music_volume"]

        self.enable_video_transition_effect = st.session_state["enable_video_transition_effect"]
        self.video_transition_effect_duration = st.session_state["video_transition_effect_duration"]
        self.video_transition_effect_type = st.session_state["video_transition_effect_type"]
        self.video_transition_effect_value = st.session_state["video_transition_effect_value"]
        self.default_duration = DEFAULT_DURATION

    # def normalize_video(self):
    #     return_video_list = []
    #     for media_file in self.video_list:
    #         # 如果当前文件是图片，添加转换为视频的命令
    #         if media_file.lower().endswith(('.jpg', '.jpeg', '.png')):
    #             output_name = generate_temp_filename(media_file, ".mp4", work_output_dir)
    #             # 判断图片的纵横比和
    #             img_width, img_height = get_image_info(media_file)
    #             if img_width / img_height > self.target_width / self.target_height:
    #                 # 转换图片为视频片段 图片的视频帧率必须要跟视频的帧率一样，否则可能在最后的合并过程中导致 合并过后的视频过长
    #                 ffmpeg_cmd = [
    #                     'ffmpeg',
    #                     '-loop', '1',
    #                     '-i', media_file,
    #                     '-c:v', 'h264',
    #                     '-t', str(self.default_duration),
    #                     '-r', str(self.fps),
    #                     '-vf',
    #                     f'scale=-1:{self.target_height}:force_original_aspect_ratio=1,crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2',
    #                     '-y', output_name]
    #             else:
    #                 ffmpeg_cmd = [
    #                     'ffmpeg',
    #                     '-loop', '1',
    #                     '-i', media_file,
    #                     '-c:v', 'h264',
    #                     '-t', str(self.default_duration),
    #                     '-r', str(self.fps),
    #                     '-vf',
    #                     f'scale={self.target_width}:-1:force_original_aspect_ratio=1,crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2',
    #                     '-y', output_name]
    #             print(" ".join(ffmpeg_cmd))
    #             subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
    #             return_video_list.append(output_name)

    #         else:
    #             # 当前文件是视频文件
    #             video_duration = get_video_duration(media_file)
    #             video_width, video_height = get_video_info(media_file)
    #             output_name = generate_temp_filename(media_file, new_directory=work_output_dir)
    #             # 不需要拉伸也不需要裁剪，只需要调整分辨率和fps
    #             if video_width / video_height > self.target_width / self.target_height:
    #                 command = [
    #                     'ffmpeg',
    #                     '-i', media_file,  # 输入文件
    #                     '-r', str(self.fps),  # 设置帧率
    #                     '-vf',
    #                     f"scale=-1:{self.target_height}:force_original_aspect_ratio=1,crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2",
    #                     # 设置视频滤镜来调整分辨率
    #                     # '-vf', f'crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2',
    #                     '-y',
    #                     output_name  # 输出文件
    #                 ]
    #             else:
    #                 command = [
    #                     'ffmpeg',
    #                     '-i', media_file,  # 输入文件
    #                     '-r', str(self.fps),  # 设置帧率
    #                     '-vf',
    #                     f"scale={self.target_width}:-1:force_original_aspect_ratio=1,crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2",
    #                     # 设置视频滤镜来调整分辨率
    #                     # '-vf', f'crop={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2',
    #                     '-y',
    #                     output_name  # 输出文件
    #                 ]
    #             # 执行FFmpeg命令
    #             print(" ".join(command))
    #             run_ffmpeg_command(command)
    #             return_video_list.append(output_name)
    #     self.video_list = return_video_list
    #     return return_video_list

    def normalize_video(self):
        """Convert videos to portrait format with blurred background for landscape content with GPU acceleration"""
        return_video_list = []
        
        # Determine if GPU acceleration is available and which type to use
        # This implementation focuses on NVIDIA GPUs (NVENC)
        print(self.video_list)
        for media_file in self.video_list:
            # Create output filename
            print(media_file)
            print(type(media_file))
            output_name = generate_temp_filename(media_file, ".mp4" if media_file.lower().endswith(('.jpg', '.jpeg', '.png')) else "", work_output_dir)
            
            if media_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Handle image files
                try:
                    img_width, img_height = get_image_info(media_file)
                    # Ensure exact target dimensions for all outputs to avoid transition errors
                    if img_height >= img_width:
                        # Portrait image with background
                        ffmpeg_cmd = [
                            'ffmpeg',
                            '-loop', '1',  # Loop the image (create a video from an image)
                            '-i', media_file,  # Input image file
                            '-c:v', 'libx264',  # Video codec
                            '-pix_fmt', 'yuv420p',  # Pixel format (to ensure compatibility)
                            '-preset', 'medium',  # Encoder preset
                            '-t', str(self.default_duration),  # Video duration
                            '-r', str(self.fps),  # Frame rate
                            '-vf',
                            f"split[original][blur];"
                            f"[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"  # Create a blurred background
                            f"[original]scale=-1:{self.target_height}:force_original_aspect_ratio=1[scaled];"  # Resize the portrait to fit the target height
                            f"[blurred][scaled]overlay=(W-w)/2:(H-h)/2,format=yuv420p",  # Center the portrait on the blurred background
                            '-y',  # Overwrite output file if it exists
                            output_name  # Output file name
                        ]
                    else:
                        # Landscape image - blurred background
                        ffmpeg_cmd = [
                            'ffmpeg',
                            '-loop', '1',
                            '-i', media_file,
                            '-c:v', 'libx264',
                            '-pix_fmt', 'yuv420p',
                            '-preset', 'medium',
                            '-t', str(self.default_duration),
                            '-r', str(self.fps),
                            '-vf', 
                            f"split[original][blur];"
                            f"[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale={self.target_width}:-1:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p", 
                            '-y', output_name
                        ]
                    
                    print(" ".join(ffmpeg_cmd))
                    subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error processing image: {e}")
                    # Simplest fallback that should always work - without GPU
                    fallback_cmd = [
                        'ffmpeg',
                        '-loop', '1',
                        '-i', media_file,
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-t', str(self.default_duration),
                        '-r', str(self.fps),
                        '-vf', f'scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=decrease,pad={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2:black',
                        '-y', output_name
                    ]
                    subprocess.run(fallback_cmd, check=True)
                    
            else:
                # Get video properties
                video_duration = get_video_duration(media_file)
                video_width, video_height = get_video_info(media_file)
                output_name = generate_temp_filename(media_file, new_directory=work_output_dir)
                
                if self.seg_min_duration > video_duration:
                    print("需要扩展视频...")
                    # 需要扩展视频
                    stretch_factor = float(self.seg_min_duration) / float(video_duration)  # 拉长比例
                    if video_width / video_height > self.target_width / self.target_height:
                        command = [
                            'ffmpeg',
                            '-i', media_file,  # 输入文件
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-vf',
                            f"setpts={stretch_factor}*PTS,split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale=-1:{self.target_height}:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name  # 输出文件
                        ]
                    else:
                        command = [
                            'ffmpeg',
                            '-i', media_file,  # 输入文件
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-vf',
                            f"setpts={stretch_factor}*PTS,split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale={self.target_width}:-1:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name  # 输出文件
                        ]
                    # 执行FFmpeg命令
                    print(" ".join(command))
                    run_ffmpeg_command(command)
                
                elif self.seg_max_duration < video_duration:
                    print("需要裁减视频...")
                    # 需要裁减视频
                    if video_width / video_height > self.target_width / self.target_height:
                        cmd = [
                            'ffmpeg',
                            '-i', media_file,
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-t', str(self.seg_max_duration),
                            '-vf',
                            f"split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale=-1:{self.target_height}:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name
                        ]
                    else:
                        cmd = [
                            'ffmpeg',
                            '-i', media_file,
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-t', str(self.seg_max_duration),
                            '-vf',
                            f"split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale={self.target_width}:-1:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name
                        ]
                    # 执行FFmpeg命令
                    print(" ".join(cmd))
                    run_ffmpeg_command(cmd)
                
                else:
                    # 不需要拉伸也不需要裁剪，只需要调整分辨率和fps
                    if video_width / video_height > self.target_width / self.target_height:
                        command = [
                            'ffmpeg',
                            '-i', media_file,  # 输入文件
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-vf',
                            f"split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale=-1:{self.target_height}:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name
                        ]
                    else:
                        command = [
                            'ffmpeg',
                            '-i', media_file,  # 输入文件
                            '-r', str(self.fps),  # 设置帧率
                            '-an',  # 去除音频
                            '-vf',
                            f"split[original][blur];[blur]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height},boxblur=20:5[blurred];"
                            f"[original]scale={self.target_width}:-1:force_original_aspect_ratio=1[scaled];"
                            f"[scaled]crop='if(gte(in_w,{self.target_width}),{self.target_width},in_w)':'if(gte(in_h,{self.target_height}),{self.target_height},in_h)':"
                            f"(in_w-{self.target_width})/2:(in_h-{self.target_height})/2[cropped];"
                            f"[blurred][cropped]overlay=(W-w)/2:(H-h)/2,format=yuv420p",
                            '-y',
                            output_name
                        ]
                    # 执行FFmpeg命令
                    print(" ".join(command))
                    run_ffmpeg_command(command)
                
            return_video_list.append(output_name)
        
        self.video_list = return_video_list
        return return_video_list

    # def generate_video_with_bg_music(self):
    #     # 生成视频和音频的代码
    #     random_name = str(random_with_system_time())
    #     merge_video = os.path.join(video_output_dir, "final-" + random_name + ".mp4")
    #     temp_video_filelist_path = os.path.join(video_output_dir, 'generate_video_with_bg_file_list.txt')

    #     # 创建包含所有视频文件的文本文件
    #     with open(temp_video_filelist_path, 'w') as f:
    #         for video_file in self.video_list:
    #             f.write(f"file '{video_file}'\n")

    #     # 拼接视频
    #     ffmpeg_concat_cmd = ['ffmpeg',
    #                          '-f', 'concat',
    #                          '-safe', '0',
    #                          '-i', temp_video_filelist_path,
    #                          '-c', 'copy',
    #                          '-fflags',
    #                          '+genpts',
    #                          '-y',
    #                          merge_video]

    #     # 是否需要转场特效
    #     if self.enable_video_transition_effect and len(self.video_list) > 1:
    #         video_length_list = get_video_length_list(self.video_list)
    #         print("启动转场特效")
    #         zhuanchang_txt = gen_filter(video_length_list, None, None,
    #                                     self.video_transition_effect_type,
    #                                     self.video_transition_effect_value,
    #                                     self.video_transition_effect_duration,
    #                                     True)

    #         # File inputs from the list
    #         files_input = [['-i', f] for f in self.video_list]
    #         ffmpeg_concat_cmd = ['ffmpeg', *itertools.chain(*files_input),
    #                              '-filter_complex', zhuanchang_txt,
    #                              '-map', '[video]',
    #                              '-map', '[audio]',
    #                              '-y',
    #                              merge_video]

    #     subprocess.run(ffmpeg_concat_cmd)
    #     # 删除临时文件
    #     os.remove(temp_video_filelist_path)

    #     # 添加背景音乐
    #     if self.enable_background_music:
    #         add_background_music(merge_video, self.background_music, self.background_music_volume)
    #     return merge_video
    def generate_video_with_bg_music(self):
        # 生成视频和音频的代码
        random_name = str(random_with_system_time())
        merge_video = os.path.join(video_output_dir, "final-" + random_name + ".mp4")
        temp_video_filelist_path = os.path.join(video_output_dir, 'generate_video_with_bg_file_list.txt')

        # 是否需要转场特效
        if self.enable_video_transition_effect and len(self.video_list) > 1:
            # First normalize all videos to have the same timebase
            normalized_videos = []
            for idx, video in enumerate(self.video_list):
                normalized_output = generate_temp_filename(video, f"_norm_{idx}.mp4", work_output_dir)
                # Force the same format for all videos to ensure transition compatibility
                norm_cmd = [
                    'ffmpeg',
                    '-i', video,
                    '-c:v', 'libx264',  # Use the same codec for all
                    '-r', str(self.fps),  # Force the same frame rate
                    '-pix_fmt', 'yuv420p',  # Consistent pixel format
                    '-vsync', 'cfr',  # Constant frame rate
                    '-vf', f'fps={self.fps}',  # Additional frame rate enforcement
                    '-y',
                    normalized_output
                ]
                subprocess.run(norm_cmd, check=True)
                normalized_videos.append(normalized_output)
            
            # Now apply transitions to the normalized videos
            video_length_list = get_video_length_list(normalized_videos)
            print("启动转场特效")
            zhuanchang_txt = gen_filter(video_length_list, None, None,
                                        self.video_transition_effect_type,
                                        self.video_transition_effect_value,
                                        self.video_transition_effect_duration,
                                        True)

            # File inputs from the list
            files_input = [['-i', f] for f in normalized_videos]
            ffmpeg_concat_cmd = ['ffmpeg', *itertools.chain(*files_input),
                                '-filter_complex', zhuanchang_txt,
                                '-map', '[video]',
                                '-map', '[audio]',
                                '-c:v', 'libx264',
                                '-c:a', 'aac',
                                '-y',
                                merge_video]
        else:
            # 创建包含所有视频文件的文本文件
            with open(temp_video_filelist_path, 'w') as f:
                for video_file in self.video_list:
                    f.write(f"file '{video_file}'\n")

            # 拼接视频
            ffmpeg_concat_cmd = ['ffmpeg',
                                '-f', 'concat',
                                '-safe', '0',
                                '-i', temp_video_filelist_path,
                                '-c', 'copy',
                                '-fflags',
                                '+genpts',
                                '-y',
                                merge_video]
            
        print(" ".join(ffmpeg_concat_cmd))
        subprocess.run(ffmpeg_concat_cmd)
        
        # Cleanup temp files
        if os.path.exists(temp_video_filelist_path):
            os.remove(temp_video_filelist_path)
            
        # Clean up normalized videos if they were created
        if self.enable_video_transition_effect and len(self.video_list) > 1:
            for video in normalized_videos:
                if os.path.exists(video):
                    try:
                        os.remove(video)
                    except:
                        pass

        # 添加背景音乐
        if self.enable_background_music:
            add_background_music(merge_video, self.background_music, self.background_music_volume)
        return merge_video