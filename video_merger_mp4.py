import os
import subprocess
import random
import time
import itertools
from pathlib import Path

FFMPEG_PATH = r"C:\\ffmpeg-7.1-full_build\\bin\\ffmpeg.exe" 
FFPROBE_PATH = r"C:\\ffmpeg-7.1-full_build\\bin\\ffprobe.exe" 
AUDIO_PATH = "D:\\Yee\\Intern\\RSW\\SQL WEB\\material_audio\\1.mp3"
INPUT_PATH = "D:\\Yee\\Intern\\RSW\\SQL WEB\\material_vid" # Folder containing images and videos
OUTPUT_PATH = "D:\\Yee\\Intern\\RSW\\SQL WEB\\MoneyPrinterPlus\\final"
OUTPUT_FILENAME = "media_slideshow.mp4"

# Utility functions
def random_with_system_time():
    """Generate a random number with system time"""
    return int(time.time() * 10000 + random.randint(0, 9999))

def generate_temp_filename(input_filename, extension=None, new_directory=None):
    """Generate a temporary filename based on an input filename"""
    if extension is None:
        extension = os.path.splitext(input_filename)[1]
    
    filename = f"{random_with_system_time()}{extension}"
    
    if new_directory:
        os.makedirs(new_directory, exist_ok=True)
        return os.path.join(new_directory, filename)
    
    return os.path.join(os.path.dirname(input_filename), filename)

def get_video_duration(video_file):
    """Get the duration of a video file"""
    cmd = [FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration', 
           '-of', 'default=noprint_wrappers=1:nokey=1', video_file]
    output = subprocess.check_output(cmd).decode('utf-8').strip()
    return float(output)

def get_video_length_list(video_list):
    """Get a list of video durations"""
    return [get_video_duration(video) for video in video_list]

def gen_filter(segments, target_width, target_height, transition_type="xfade", 
               transition_value="fade", transition_duration=1, with_audio=False):
    """Generate FFmpeg filter complex string for video transitions"""
    video_fades = ""
    audio_fades = ""
    settb = ""
    last_fade_output = "0v"
    last_audio_output = "0:a"

    video_length = 0
    file_lengths = [0] * len(segments)

    if target_width:
        for i in range(len(segments)):
            settb += f"[{i}:v]settb=AVTB,scale=w={target_width}:h={target_height}:force_original_aspect_ratio=1,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2[{i}v];"

    str_list = [str(f) for f in segments]
    print("Video lengths: " + " ".join(str_list))
    
    for i in range(len(segments) - 1):
        file_lengths[i] = segments[i]
        video_length += float(file_lengths[i])
        next_fade_output = f"v{i}{i+1}"
        
        # Video transition
        video_fades += f"[{last_fade_output}][{i+1}v]{transition_type}=transition={transition_value}:duration={float(transition_duration)}:offset={video_length - float(transition_duration) * (i + 1)}"
        video_fades += f"[{next_fade_output}];" if (i) < len(segments) - 2 else ",format=yuv420p[video];"
        last_fade_output = next_fade_output

        # Audio transition if needed
        if with_audio:
            next_audio_output = f"a{i}{i+1}"
            audio_fades += f"[{last_audio_output}][{i+1}:a]acrossfade=d={float(transition_duration)}:c2=nofade"
            audio_fades += f"[{next_audio_output}];" if (i) < len(segments) - 2 else "[audio]"
            last_audio_output = next_audio_output

    if with_audio:
        return settb + video_fades + audio_fades
    return settb + video_fades

def is_image_file(file_path):
    """Check if a file is an image based on its extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.bmp']

def is_video_file(file_path):
    """Check if a file is a video based on its extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.mp4', '.mov', '.avi', '.mkv']

def convert_image_to_video(image_file, output_dir, duration=5, fps=30, target_width=None, target_height=None, audio_file=None):
    """Convert an image to a video clip with specified duration"""
    output_file = generate_temp_filename(image_file, ".mp4", output_dir)
    
    scale_filter = ""
    if target_width and target_height:
        scale_filter = f"scale=w={target_width}:h={target_height}:force_original_aspect_ratio=1,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
    
    cmd = [
        FFMPEG_PATH,
        '-loop', '1',
        '-i', image_file
    ]
    
    # Add audio input
    if audio_file and os.path.exists(audio_file):
        cmd.extend(['-i', audio_file])
    else:
        # Fallback to silent audio if no audio file or file doesn't exist
        cmd.extend(['-f', 'lavfi', '-i', 'anullsrc'])
    
    # Continue with rest of command
    cmd.extend([
        '-t', str(duration),
        '-r', str(fps),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',  # End when shortest input ends
        '-pix_fmt', 'yuv420p'
    ])
    
    # Add scale filter if needed
    if scale_filter:
        cmd.extend(['-vf', scale_filter])
    
    # Add output file
    cmd.extend([
        '-y',
        output_file
    ])
    
    print(f"Converting image to video: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    return output_file

def merge_videos(input_list, output_file, fps=30, target_width=1080, target_height=1920,
                enable_transition=True, transition_type="xfade", transition_value="fade", 
                transition_duration=1, image_duration=5, audio_file=None):
    """
    Merge multiple videos and images into one with optional transition effects
    """
    temp_dir = os.path.dirname(output_file)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Process input files - convert images to videos if needed
    processed_video_list = []
    temp_files_to_remove = []
    
    for input_file in input_list:
        if is_image_file(input_file):
            # Convert image to video
            video_file = convert_image_to_video(
                input_file, 
                temp_dir, 
                duration=image_duration, 
                fps=fps, 
                target_width=target_width, 
                target_height=target_height,
                audio_file=audio_file 
            )
            processed_video_list.append(video_file)
            temp_files_to_remove.append(video_file)
        else:
            # Add video file directly
            processed_video_list.append(input_file)
    
    # Create a temporary file list for simple concatenation
    temp_filelist_path = os.path.join(temp_dir, f'video_merge_filelist_{random_with_system_time()}.txt')
    
    with open(temp_filelist_path, 'w') as f:
        for video_file in processed_video_list:
            f.write(f"file '{video_file}'\n")
    
    # Basic command for concatenation without transitions
    ffmpeg_concat_cmd = [
        FFMPEG_PATH,
        '-f', 'concat',
        '-safe', '0',
        '-i', temp_filelist_path,
        '-c', 'copy',
        '-fflags', '+genpts',
        '-y',
        output_file
    ]
    
    # If transitions are enabled and we have more than one processed file
    if enable_transition and len(processed_video_list) > 1:
        video_length_list = get_video_length_list(processed_video_list)
        
        # Generate filter complex for transitions
        filter_complex = gen_filter(
            video_length_list,
            target_width, target_height,
            transition_type,
            transition_value,
            transition_duration,
            True  # Include audio transitions
        )
        
        # File inputs from the list
        files_input = [['-i', f] for f in processed_video_list]
        ffmpeg_concat_cmd = [
            FFMPEG_PATH, 
            *itertools.chain(*files_input),
            '-filter_complex', filter_complex,
            '-map', '[video]',
            '-map', '[audio]',
            '-y',
            output_file
        ]
    
    # Execute the FFmpeg command
    print("Executing:", " ".join(ffmpeg_concat_cmd))
    subprocess.run(ffmpeg_concat_cmd)
    
    # Clean up temporary files
    if os.path.exists(temp_filelist_path):
        os.remove(temp_filelist_path)
    
    for temp_file in temp_files_to_remove:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return output_file

def merge_videos_with_audio(input_list, output_file, fps=30, target_width=1080, target_height=1920,
                           enable_transition=True, transition_type="xfade", transition_value="fade",
                           transition_duration=1, image_duration=5, audio_file=None):
    """Merge videos with consistent audio handling"""
    # First merge all the videos without handling audio transitions
    temp_video = generate_temp_filename(output_file, ".mp4", os.path.dirname(output_file))
    
    # Process videos first
    processed_result = merge_videos(
        input_list, 
        temp_video,
        fps, 
        target_width, 
        target_height,
        enable_transition, 
        transition_type, 
        transition_value, 
        transition_duration, 
        image_duration,
        None  # Don't use audio file yet
    )
    
    # Now add a global audio track if provided
    if audio_file and os.path.exists(audio_file):
        final_output = output_file
        
        cmd = [
            FFMPEG_PATH,
            '-i', processed_result,
            '-i', audio_file,
            '-map', '0:v',
            '-map', '1:a',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            final_output
        ]
        
        print(f"Adding global audio track: {' '.join(cmd)}")
        subprocess.run(cmd)
        
        # Clean up
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        return final_output
    
    # If no audio file, just rename the temp file
    os.rename(temp_video, output_file)
    return output_file

if __name__ == "__main__":
    # Get the folder path
    folder_path = os.path.normcase(INPUT_PATH)
    
    # Use Path to find all JPEG files
    media_files = []
    
    # Find image files
    for ext in ['.jpg', '.jpeg', '.png']:
        media_files.extend(list(Path(folder_path).glob(f'*{ext}')))
    
    # Find MP4 files (and other video formats if needed)
    media_files.extend(list(Path(folder_path).glob('*.mp4')))
    
    # Convert Path objects to strings
    media_files = [str(file) for file in media_files]
    
    # Sort files by name
    media_files.sort()
    
    print(f"Found {len(media_files)} media files in {folder_path}")
    print("Images:", [f for f in media_files if is_image_file(f)])
    print("Videos:", [f for f in media_files if is_video_file(f)])

    # Set background audio path, use None if file doesn't exist
    background_audio = os.path.normcase(AUDIO_PATH)
    if not os.path.exists(background_audio):
        background_audio = None
    
    output = os.path.normcase(OUTPUT_PATH + "\\" + OUTPUT_FILENAME) 
    
    # Create slideshow from media files
    result = merge_videos_with_audio(
        media_files,
        output,
        fps=30,
        target_width=1920,
        target_height=1080,
        enable_transition=True,
        transition_type="xfade",
        transition_value="fade",
        transition_duration=1,
        image_duration=4,  # How long each image should display (in seconds)
        audio_file=background_audio  # Audio will only be used for images, videos keep their own audio
    )
    
    print(f"Media slideshow saved to: {result}")