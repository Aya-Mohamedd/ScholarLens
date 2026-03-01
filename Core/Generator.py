import json
import asyncio
import edge_tts
import os
import subprocess
import textwrap
from moviepy.config import get_setting 
from moviepy.editor import (
    ImageClip, 
    concatenate_videoclips, 
    AudioFileClip
)

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- Helper Function for SRT Time Format (00:00:00,000) ---
def format_time(seconds):
    td = float(seconds)
    hours = int(td // 3600)
    minutes = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int((td % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# 1. Audio generation using Edge-TTS
async def process_audio(file_path):
    audio_folder = os.path.join("assets", "scene_audios")
    if not os.path.exists(audio_folder): 
        os.makedirs(audio_folder)
    
    with open(file_path, 'r', encoding='utf-8') as f: 
        script_data = json.load(f)
    
    for i, scene in enumerate(script_data, start=1):
        output_file = os.path.join(audio_folder, f"scene_{i}.mp3")
        communicate = edge_tts.Communicate(scene['narration'], "en-US-AndrewNeural")
        await communicate.save(output_file)
        scene['audio_file'] = output_file
    
    with open('final_synced_script.json', 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    
    return script_data

# 2. Image generation (Placeholder)
def generate_free_images_v3(json_input):
    output_dir = os.path.join("assets", "video_assets_wide")
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
    print(f"Checking: {output_dir}")
    pass

# 3. Video generation using FFmpeg with Smart Subtitle Timing
def create_final_video_with_subs():
    TEMP_VIDEO_NAME = "temp_raw_video.mp4"
    FINAL_VIDEO_NAME = "ScholarLens_Final_Subtitled.mp4"
    SRT_FILE = "subtitles.srt"
    
    # Get the internal FFMPEG binary path from MoviePy
    FFMPEG_BINARY = get_setting("FFMPEG_BINARY")
    
    if os.path.exists(FINAL_VIDEO_NAME):
        print(f"The video: '{FINAL_VIDEO_NAME}' Already exist...")
        return 

    if not os.path.exists('final_synced_script.json'):
        print("Error: final_synced_script.json is not exist")
        return

    with open('final_synced_script.json', 'r', encoding='utf-8') as f: 
        scenes = json.load(f)
    
    video_clips = []
    srt_content = []
    current_global_time = 0.0
    subtitle_counter = 1
    target_width = 1280 

    print("Step 1: Compiling scenes and calculating smart subtitle timing...")

    for i, scene in enumerate(scenes):
        audio_p = scene.get('audio_file')
        visual = scene.get('visual_ref', '')
        full_text = scene.get('narration', '')

        img_p = os.path.join('assets', 'extracted_images', visual) if visual.startswith('image_p') else os.path.join('assets', 'video_assets_wide', f"scene_{i+1}.png")
        
        if os.path.exists(img_p) and os.path.exists(audio_p):
            audio = AudioFileClip(audio_p)
            scene_duration = audio.duration
            
            # Create video clip for the scene
            img = (ImageClip(img_p)
                   .set_duration(scene_duration)
                   .set_audio(audio)
                   .resize(width=target_width))
            video_clips.append(img)

            # --- Smart Timing Logic ---
            # Split text into smaller chunks for better readability
            wrapped_lines = textwrap.wrap(full_text, width=50) 
            total_chars = sum(len(line) for line in wrapped_lines)
            
            scene_relative_start = 0.0
            for line in wrapped_lines:
                # Calculate how long this specific line should stay on screen
                line_duration = scene_duration * (len(line) / total_chars) if total_chars > 0 else scene_duration
                
                start_srt = format_time(current_global_time + scene_relative_start)
                end_srt = format_time(current_global_time + scene_relative_start + line_duration)
                
                srt_content.append(f"{subtitle_counter}\n{start_srt} --> {end_srt}\n{line}\n")
                
                scene_relative_start += line_duration
                subtitle_counter += 1
            
            current_global_time += scene_duration
            print(f"Scene {i+1} processed with {len(wrapped_lines)} subtitle chunks.")

    # Save the generated SRT file
    with open(SRT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    # Step 2: Render Raw Video
    if video_clips:
        print("Final video rendering starting (Raw)...")
        final_raw = concatenate_videoclips(video_clips, method="compose")
        final_raw.write_videofile(TEMP_VIDEO_NAME, fps=24, codec="libx264", audio_codec="aac")

        print("Step 3: Hardcoding professional subtitles using FFmpeg...")
        # Escape path for Windows FFmpeg
        srt_path_fixed = SRT_FILE.replace("\\", "/").replace(":", "\\:")
        
        # Professional Styling: 
        # BorderStyle=3 (Opaque Box) ensures readability
        ffmpeg_cmd = [
            FFMPEG_BINARY, '-y', '-i', TEMP_VIDEO_NAME,
            '-vf', f"subtitles='{srt_path_fixed}':force_style='FontSize=16,PrimaryColour=&HFFFFFF,BackColour=&H80000000,BorderStyle=3,Outline=0,Shadow=0,Alignment=2,MarginV=25'",
            '-c:a', 'copy', FINAL_VIDEO_NAME
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            if os.path.exists(TEMP_VIDEO_NAME): os.remove(TEMP_VIDEO_NAME)
            print(f"✨ Success! Masterpiece ready: {FINAL_VIDEO_NAME}")
        except Exception as e:
            print(f"⚠️ FFmpeg Error: {e}")