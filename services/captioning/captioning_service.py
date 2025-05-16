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

import json
import os
import platform
from typing import Optional

from config.config import my_config
from services.alinls.speech_process import AliRecognitionService
from services.audio.faster_whisper_recognition_service import FasterWhisperRecognitionService
from services.audio.sensevoice_whisper_recognition_service import SenseVoiceRecognitionService
from services.audio.tencent_recognition_service import TencentRecognitionService
from services.captioning.common_captioning_service import Captioning
import subprocess

from tools.file_utils import generate_temp_filename
import streamlit as st

from tools.utils import get_session_option

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# print("当前脚本的绝对路径是:", script_path)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)

font_dir = os.path.join(script_dir, '../../fonts')
font_dir = os.path.abspath(font_dir)

# windows路径需要特殊处理
if platform.system() == "Windows":
    font_dir = font_dir.replace("\\", "\\\\\\\\")
    font_dir = font_dir.replace(":", "\\\\:")


# 生成字幕
def generate_caption():
    captioning = Captioning()
    captioning.initialize()
    speech_recognizer_data = captioning.speech_recognizer_from_user_config()
    # print(speech_recognizer_data)
    recognition_type = st.session_state.get('recognition_audio_type')
    if recognition_type == "remote":
        selected_audio_provider = my_config['audio']['provider']
        if selected_audio_provider == 'Azure':
            print("selected_audio_provider: Azure")
            captioning.recognize_continuous(speech_recognizer=speech_recognizer_data["speech_recognizer"],
                                            format=speech_recognizer_data["audio_stream_format"],
                                            callback=speech_recognizer_data["pull_input_audio_stream_callback"],
                                            stream=speech_recognizer_data["pull_input_audio_stream"])
        if selected_audio_provider == 'Ali':
            print("selected_audio_provider: Ali")
            ali_service = AliRecognitionService()
            result_list = ali_service.process(get_session_option("audio_output_file"))
            captioning._offline_results = result_list
        if selected_audio_provider == 'Tencent':
            print("selected_audio_provider: Tencent")
            tencent_service = TencentRecognitionService()
            result_list = tencent_service.process(get_session_option("audio_output_file"),
                                                  get_session_option("audio_language"))
            if result_list is None:
                return
            captioning._offline_results = result_list
    if recognition_type == "local":
        selected_audio_provider = my_config['audio'].get('local_recognition',{}).get('provider')
        if selected_audio_provider =='fasterwhisper':
            print("selected_audio_provider: fasterwhisper")
            fasterwhisper_service = FasterWhisperRecognitionService()
            result_list = fasterwhisper_service.process(get_session_option("audio_output_file"),
                                                  get_session_option("audio_language"))
            print(result_list)
            if result_list is None:
                return
            captioning._offline_results = result_list

        if selected_audio_provider =='sensevoice':
            print("selected_audio_provider: sensevoice")
            fasterwhisper_service = SenseVoiceRecognitionService()
            result_list = fasterwhisper_service.process(get_session_option("audio_output_file"),
                                                  get_session_option("audio_language"))
            print(result_list)
            if result_list is None:
                return
            captioning._offline_results = result_list

    captioning.finish()

# def generate_caption():
#     captioning = Captioning()
#     captioning.initialize()
    
#     # Get the script text that was used to generate the audio
#     # Get video content from multiple scene texts
#     video_content = ""
#     for i in range(1, 6):  # 1 through 5
#         scene_text_path = st.session_state.get(f"video_scene_text_{i}", "")
#         if scene_text_path and os.path.exists(scene_text_path):  # Check if path exists
#             try:
#                 with open(scene_text_path, 'r', encoding='utf-8') as file:
#                     scene_text = file.read()
#                     if scene_text:  # Skip empty files
#                       video_content += scene_text + " "
#             except Exception as e:
#                 print(f"Error reading file {scene_text_path}: {e}")
#     video_content = video_content.strip()  # Remove trailing space
#     if not video_content:
#         print("No video content found in session state")
#         return
    
#     # Get the audio file path and determine its duration
#     audio_file = st.session_state.get("audio_output_file")
#     if not audio_file or not os.path.exists(audio_file):
#         print(f"Audio file not found: {audio_file}")
#         return
    
#     # Get audio duration using ffprobe
#     import subprocess
#     import json
    
#     cmd = [
#         'ffprobe', 
#         '-v', 'error', 
#         '-show_entries', 'format=duration', 
#         '-of', 'json', 
#         audio_file
#     ]
    
#     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     duration = float(json.loads(result.stdout)['format']['duration'])
    
#     # Generate subtitles from the script text
#     output_file = st.session_state.get("captioning_output")
#     if not output_file:
#         random_name = str(int(time.time()))
#         output_file = os.path.join(os.path.dirname(audio_file), f"{random_name}.srt")
#         st.session_state["captioning_output"] = output_file
    
#     # Generate subtitles based on the script text
#     generate_script_based_subtitles(video_content, output_file, duration)

# # Generate caption with script selected
# def generate_script_based_subtitles(script_text, output_file, audio_duration):
#     """Generate subtitles based on script text by splitting at punctuation marks
    
#     Args:
#         script_text: The text script used for voice generation
#         output_file: Path to output SRT file
#         audio_duration: Duration of the audio in seconds
#     """
#     def format_time(seconds):
#         """Format time in seconds to SRT format (HH:MM:SS,mmm)"""
#         hours = int(seconds // 3600)
#         minutes = int((seconds % 3600) // 60)
#         seconds = seconds % 60
#         milliseconds = int((seconds - int(seconds)) * 1000)
#         return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

#     # Split text by punctuation marks (for both English and Chinese)
#     import re
    
#     # Split by common punctuation (., !, ?, 。, ！, ？, etc.)
#     sentences = re.split(r'([.!?。！？;；])', script_text)
    
#     # Combine each sentence with its punctuation
#     real_sentences = []
#     i = 0
#     while i < len(sentences) - 1:
#         if i + 1 < len(sentences) and len(sentences[i+1]) == 1:  # If next item is punctuation
#             real_sentences.append(sentences[i] + sentences[i+1])
#             i += 2
#         else:
#             if sentences[i].strip():  # Only add non-empty strings
#                 real_sentences.append(sentences[i])
#             i += 1
    
#     # Filter out empty sentences
#     real_sentences = [s.strip() for s in real_sentences if s.strip()]
    
#     # Calculate time per sentence (distribute evenly across audio duration)
#     if not real_sentences:
#         return
    
#     time_per_sentence = audio_duration / len(real_sentences)
    
#     # Write SRT file
#     with open(output_file, 'w', encoding='utf-8') as f:
#         for i, sentence in enumerate(real_sentences):
#             start_time = i * time_per_sentence
#             end_time = (i + 1) * time_per_sentence
            
#             # Format timestamps as SRT requires (HH:MM:SS,mmm)
#             start_str = format_time(start_time)
#             end_str = format_time(end_time)
            
#             # Write SRT entry
#             f.write(f"{i+1}\n")
#             f.write(f"{start_str} --> {end_str}\n")
#             f.write(f"{sentence}\n\n")
    
#     return output_file


# 添加字幕
def add_subtitles(video_file, subtitle_file, font_name='Songti TC Bold', font_size=12, primary_colour='#FFFFFF',
                  outline_colour='#FFFFFF', margin_v=16, margin_l=4, margin_r=4, border_style=1, outline=0, alignment=2,
                  shadow=0, spacing=2):
    output_file = generate_temp_filename(video_file)
    # 添加透明度通道（AA），默认00表示不透明，并确保颜色值为6位
    # 将HEX颜色转换为BGRA格式（AARRGGBB -> BBGGRRAA）
    def hex_to_bgra(hex_color):
        hex_color = hex_color.lstrip('#')
        alpha = hex_color[6:8] if len(hex_color) >= 8 else '00'
        rgb = hex_color[:6].ljust(6, '0')
        bgr = rgb[4:6] + rgb[2:4] + rgb[0:2]  # RRGGBB -> BBGGRR
        return f"&H{alpha}{bgr}&"
    
    primary_colour = hex_to_bgra(primary_colour)
    outline_colour = hex_to_bgra(outline_colour)
    # windows路径需要特殊处理
    if platform.system() == "Windows":
        subtitle_file = subtitle_file.replace("\\", "\\\\\\\\")
        subtitle_file = subtitle_file.replace(":", "\\\\:")
    vf_text = f"subtitles={subtitle_file}:fontsdir={font_dir}:force_style='Fontname={font_name},Fontsize={font_size},Alignment={alignment},MarginV={margin_v},MarginL={margin_l},MarginR={margin_r},BorderStyle={border_style},Outline={outline},Shadow={shadow},PrimaryColour={primary_colour},OutlineColour={outline_colour},Spacing={spacing}'"
    # 构建FFmpeg命令
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', video_file,  # 输入视频文件
        '-vf', vf_text,  # 输入字幕文件
    ]
    # 检查是否有GPU可用
    try:
        # 检查NVIDIA编码器是否可用
        check_cmd = ['ffmpeg', '-hide_banner', '-encoders']
        result = subprocess.run(check_cmd, capture_output=True, text=True)
            
        # 根据可用的NVIDIA编码器选择合适的选项
        if 'h264_nvenc' in result.stdout:
            ffmpeg_cmd.extend([
                '-c:v', 'h264_nvenc',  # 使用NVIDIA H.264编码器
                '-preset', 'p1',       # 编码速度预设 (可选值: p1-p7, p1最快)
                '-tune', 'hq',         # 高质量设置
                ])
        else:
            print("NVIDIA GPU encoders not available, falling back to CPU")
    except Exception as e:
        print(f"Error checking GPU encoders: {e}. Using CPU instead.")    
    
    # 添加其他必要的参数
    ffmpeg_cmd.extend([
        '-y',
        output_file  # 输出文件
    ])
    print(" ".join(ffmpeg_cmd))
    # 调用ffmpeg
    subprocess.run(ffmpeg_cmd, check=True)
    # 重命名最终的文件
    if os.path.exists(output_file):
        os.remove(video_file)
        os.renames(output_file, video_file)
